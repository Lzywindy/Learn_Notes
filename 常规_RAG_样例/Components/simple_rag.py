import torch
from  typing import Union
from .llm_inference import LLM_Inference
from .text_embadding import SimpleEmbedding
class SimpleRAG_Workflow:
    def __init__(self,  **karges) -> None:
        self.vector_db=SimpleEmbedding(karges.get("embedding_model_or_path","BAAI/bge-m3"),karges.get("embedding_text_source","Text.json"),karges.get("embedding_gpu","cuda:0"),karges.get("embedding_batch_size",16))
        self.inference_model=LLM_Inference(karges.get("inference_model_or_path","Qwen/Qwen2.5-Coder-7B"),device=karges.get("inference_gpu","cuda:1"),dtype=torch.bfloat16,QInt4=karges.get("QInt4",False))
    def query(self,prompt_template:str,query:Union[str,list[str]],topk:int,**gen_kwargs):
        if isinstance(query,str):
            query=[query]
        search_result=self.vector_db.search(query,topk=topk,need_cosine_distance_score=False,need_out_paires=True)
        final_result=self.inference_model.response(query=[prompt_template.format(query=sr['query'],evidences="\n".join(sr['retrieve_results']))  for sr in search_result],**gen_kwargs)
        result=[]
        for q,r,s in zip(query,final_result,search_result):
            result.append({"query":q,"response":r,"search_result":s})
        return result
    pass