from tqdm.auto import tqdm 
import os,torch, transformers
from transformers import AutoTokenizer, AutoModelForCausalLM,BitsAndBytesConfig,DataCollatorForSeq2Seq
from typing import TYPE_CHECKING, Any, Dict, List, Union, Optional
from torch.utils.data import DataLoader

LLM_PATH="J:\\我的博士论文\\LLMs\\Qwen" # 可以改成自己的模型文件路径

MODEL_PATHS = {    
    # 千问系列
    "Qwen2.5-7B":os.path.join(LLM_PATH,"Qwen2.5-7B-Instruct"),
    "Qwen2.5-Coder-7B":os.path.join(LLM_PATH,"Qwen2.5-Coder-7B-Instruct"),
    "Qwen3-8B":os.path.join(LLM_PATH,"Qwen3-8B"),
}

class LLM_Inference(object):
    def __init__(self,name_or_path:str,device: Optional[str] ,dtype: torch.dtype ,**karges) -> None:
        """
        初始化模型及其相关配置。
        
        参数:
        - name_or_path: 模型的名称或路径。
        - device: 设备信息，用于指定模型运行的硬件环境，如"cpu"或"cuda"。
        - dtype: 模型权重的数据类型，例如torch.float32。
        - **karges: 其他关键字参数，用于灵活配置(目前只支持`QInt4`)。
        
        返回:
        无返回值。
        """
        self.model_path=MODEL_PATHS.get(name_or_path,name_or_path)
        modelname= os.path.basename(self.model_path).lower()        
        assert "qwen2.5" in modelname or "qwen3" in self.model_path # 这里暂时只对千问做了适配
        if karges.get("QInt4",False): # 这里默认不启动Qint4推理，如需要请自行修改
            self.quantization_config=BitsAndBytesConfig(load_in_8bit=False,load_in_4bit=True,bnb_4bit_compute_dtype=torch.bfloat16,bnb_4bit_quant_storage=torch.uint8,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=False)        
        else:
            self.quantization_config=None
        self.device=device
        self.dtype=dtype
        self.name_or_path=name_or_path
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        if isinstance(self.quantization_config,BitsAndBytesConfig):
            self.model = AutoModelForCausalLM.from_pretrained(self.model_path, trust_remote_code=True,device_map=device,torch_dtype=self.dtype,quantization_config=self.quantization_config).eval()
        else:
            self.model = AutoModelForCausalLM.from_pretrained(self.model_path, trust_remote_code=True,device_map=device,torch_dtype=self.dtype).eval()
        if self.tokenizer.padding_side != "left":
            self.tokenizer.padding_side = "left"
        if not isinstance(self.tokenizer.pad_token_id,int) :
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        if not isinstance(self.tokenizer.pad_token,str) :
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.data_collator = DataCollatorForSeq2Seq(tokenizer=self.tokenizer,model=self.model,label_pad_token_id=self.tokenizer.pad_token_id)
        pass
    def _batch_output(self,query:list[str],role:str,batch_size:int,gen_kwargs: dict[str,Any]):
        dataset=[self.tokenizer.apply_chat_template([{"role": role, "content": n}],add_generation_prompt=True,tokenize=True,return_dict=True) for n in tqdm(query,desc="令牌处理")]
        dataloader = DataLoader(dataset, batch_size=batch_size, collate_fn=self.data_collator)
        results=list[str]()
        for batch in tqdm(dataloader,desc="响应中..."):
            batch=batch.to(self.model.device)
            outputs = self.model.generate(**batch, **gen_kwargs)
            outputs = outputs[:, batch['input_ids'].shape[1]:]
            results.extend(self.tokenizer.batch_decode(outputs, skip_special_tokens=True))
        return results
    def _single_output(self,query:str,role:str,gen_kwargs: dict[str,Any]):
        inputs = self.tokenizer.apply_chat_template([{"role": role, "content": query}],add_generation_prompt=True,tokenize=True,return_tensors="pt",return_dict=True).to(self.model.device)
        outputs = self.model.generate(**inputs, **gen_kwargs)
        outputs = outputs[:, inputs['input_ids'].shape[1]:] 
        return [self.tokenizer.decode(outputs[0], skip_special_tokens=True)]
    def response(self,query: Union[str,list[str]], **karges):
        """
        根据输入的查询生成响应。

        可以处理单个查询字符串`str`或查询字符串列表`list[str]`，根据给定的角色和生成参数，
        生成相应的响应。支持通过调整max_length或max_new_tokens参数来控制输出长度。

        参数:
        - query (Union[str, list[str]]): 输入的查询，可以是单个查询字符串或查询字符串列表。
        - **karges: 可变关键字参数，用于指定角色`role`、最大长度`max_length`或者最大新长度`max_new_tokens`、是否成对返回结果`return_as_pair`等。

        返回:
        - 成对返回时为List[Dict[str, str]]，否则为生成的响应列表。
        """
        torch.cuda.empty_cache()
        role=karges.get("role","user")
        max_length = karges.get("max_length",None)
        return_as_pair= karges.get("return_as_pair",False)
        if isinstance (max_length,int):
            gen_kwargs = {"max_length":min(max_length,128000), "do_sample": True, "top_k": 1}
        else:
            gen_kwargs = {"max_new_tokens":karges.get("max_new_tokens",1024), "do_sample": True, "top_k": 1}
        with torch.inference_mode():
            if isinstance(query,str):
                results=self._single_output(query,role,gen_kwargs)
                torch.cuda.empty_cache()
                if return_as_pair:
                    results_dict=list[dict[str,str]]()
                    for _input_str,output_str in zip([query],results):
                        results_dict.append({"input":_input_str,"output":output_str})
                    return results_dict
                else:
                    return results
            elif isinstance(query,list):
                results=self._batch_output(query,role,max(karges.get("batch_size",4),2),gen_kwargs)
                torch.cuda.empty_cache()
                if return_as_pair:
                    results_dict=list[dict[str,str]]()
                    for _input_str,output_str in zip(query,results):
                        results_dict.append({"input":_input_str,"output":output_str})
                    return results_dict
                else:
                    return results
            else:
                raise ValueError("query 必须是 str 或者是 list[str]")
    pass
