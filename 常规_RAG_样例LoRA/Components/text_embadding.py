import os,hnswlib,torch
import numpy as np
from .cutils import load_from_json,save_to_json
from typing import TYPE_CHECKING, Any, Dict, List, Union, Optional
from sentence_transformers import SentenceTransformer

class SimpleEmbedding:
    def __init__(self,model_name_or_path:str,file_path:str,device:str="cuda:0",batch_size:int=32):
        self.device=device
        self.batch_size=batch_size
        self.model= SentenceTransformer(model_name_or_path,device=self.device).half().eval()
        self.fold=os.path.join ("cache",os.path.basename(file_path).replace(".json", ""))
        self.text_name=os.path.join( self.fold,"texts.json")
        self.vector_name=os.path.join( self.fold,"vectors.npy")
        if not os.path.exists(self.fold):            
            torch.cuda.empty_cache()
            self.text= load_from_json(file_path)
            self.vectors=self.model.encode(self.text,device=self.device,batch_size=self.batch_size,show_progress_bar=True)
            torch.cuda.empty_cache()
            save_to_json(self.text,self.text_name)
            np.save(self.vector_name,self.vectors)
        else:
            self.text= load_from_json(self.text_name)
            self.vectors=np.load(self.vector_name)
        self.hnsw = hnswlib.Index(space="cosine", dim=self.vectors.shape[1])
        self.hnsw.init_index(max_elements=self.vectors.shape[0], ef_construction=100, M=16)
        self.hnsw.set_ef(80)
        self.hnsw.add_items(self.vectors)
        print("hnsw init done, shape =", self.vectors.shape)
        pass
    def search(self,query:Union[str,list[str]],topk:int=10,need_cosine_distance_score:bool=False,need_out_paires:bool=True):
        if isinstance(query,str):
            q_vector=self.model.encode([query],device=self.device,batch_size=self.batch_size,show_progress_bar=True)
        elif isinstance(query,list):
            q_vector=self.model.encode(query,device=self.device,batch_size=self.batch_size,show_progress_bar=True)
        else:
            raise ValueError("query 必须是 str 或者是 list[str]")
        labels, sims = self.hnsw.knn_query(q_vector, topk)
        arrays=[]
        for row in range(labels.shape[0]):
            array=[]
            for col in range(labels.shape[1]):
                if need_cosine_distance_score:
                    array.append((self.text[labels[row,col]],sims[row,col]))
                else:
                    array.append(self.text[labels[row,col]])
            if need_out_paires:
                arrays.append({"query":query[row],"retrieve_results":array})
            else:
                arrays.append(array)
        return arrays
    pass