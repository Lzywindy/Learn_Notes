import os,pickle,json
from  typing import Any,Union, List, Dict
def _check_create_dirs(file_path: str):
    """
    # 代码解释
    这段代码的功能是检查给定文件路径的父目录是否存在，如果不存在则创建该目录。具体逻辑如下：
    1. 使用 `os.path.dirname` 获取文件路径的父目录路径。
    2. 如果父目录路径不为空，则进一步检查该路径是否存在。
    3. 如果路径不存在，则调用 `os.makedirs` 创建该目录。

    # 控制流图
    ```mermaid
    flowchart TD
        A[开始] --> B[获取文件路径的父目录]
        B --> C{父目录是否为空}
        C -->|是| D[结束]
        C -->|否| E{父目录是否存在}
        E -->|否| F[创建父目录]
        F --> G[结束]
        E -->|是| G[结束]
    ```
    """
    # 获取文件路径的父目录
    p = os.path.dirname(file_path)
    # 检查父目录是否为空
    if p != '':
        # 检查父目录是否存在
        if not os.path.exists(p):
            # 如果父目录不存在，则创建该目录
            os.makedirs(p)
    pass
def load_object(filename:str):
    """
    从指定的文件名加载对象。
    
    此函数尝试从给定的文件名中读取数据，并将数据反序列化为一个对象。
    如果文件不存在，函数返回None。
    
    参数:
    - filename (str): 包含序列化对象的文件的名称。
    
    返回:
    - content: 反序列化后的对象，如果文件不存在则返回None。
    """
    # 检查文件是否存在
    if not  os.path.exists(filename): 
        return None
    # 打开文件以读取和反序列化对象
    with open(filename,'rb') as f:
        content=pickle.loads(f.read())
        f.close()
    return content
def save_object(content:Any,filename:str):
    """
    将内容保存为对象到指定的文件中。

    本函数通过pickle序列化的方式将任意类型的content保存到filename指定的文件路径中。
    如果content为空，则不执行任何操作。本函数确保在写入文件之前，文件所需的目录结构已经创建完成。

    参数:
    content: 待保存的内容，可以是任意类型。
    filename: 保存内容的文件路径。

    返回:
    无返回值。
    """
    if not content: 
        return
    _check_create_dirs(filename)
    with open(filename,'wb') as f:
        f.write(pickle.dumps(content))
        f.close()
    pass
def load_from_json(file_path: str) -> Union[None, Dict, List]:
    """
    从指定的文件路径加载JSON数据并解析。

    此函数尝试从给定的文件路径中读取JSON数据，如果文件不存在，则返回None。
    如果文件存在，它将打开文件，读取内容，并将内容解析为JSON格式的数据，然后返回。
    支持返回的数据类型可以是字典、列表或None。

    参数:
    file_path (str): JSON文件的路径。

    返回:
    Union[None, Dict, List]: 解析后的JSON数据，如果文件不存在则返回None。
    """
    if not os.path.exists(file_path):
        return None
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.loads(f.read())
            f.close()
        return content
    pass
def save_to_json(data: Union[Dict, List], file_path: str):
    """
    将数据保存到JSON文件中。
    
    该函数接受一个字典或列表形式的数据，并将其序列化为JSON格式，
    然后将序列化的数据写入到指定的文件路径中。如果文件路径中的目录不存在，
    则会先创建目录。
    
    参数:
    data (Union[Dict, List]): 要保存的字典或列表数据。
    file_path (str): 数据保存的文件路径。
    
    返回:
    无返回值。
    """
    _check_create_dirs(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))
        f.close()
    pass
def load_jsonline(file_path: str) -> List:
    """
    从指定的文件路径加载 JSON Lines 文件中的数据。
    
    JSON Lines 是一种轻量级的数据交换格式，每一行都是一个独立的 JSON 对象。
    本函数读取文件中的每一行，并将其解析为 JSON 对象，最终返回一个包含所有对象的列表。
    
    参数:
    file_path: str - 文件的路径。
    
    返回:
    List - 包含解析后的 JSON 对象的列表。如果文件不存在，返回一个空列表。
    """
    if not os.path.exists(file_path):
        return []
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            datas = [json.loads(n) for n in f.readlines()]
            f.close()
        return datas
    pass
def save_jsonline(datas: List, file_path: str):
    """
    将数据列表以JSON格式保存到指定文件中。
    
    该函数负责将一个包含多个数据项的列表转换为JSON格式的字符串，并将其写入到指定路径的文件中。
    每个数据项在文件中占一行，以实现可读性和逐步处理的需求。
    
    参数:
    - datas: List，包含多个数据项的列表，每个数据项都将被转换为JSON格式的字符串。
    - file_path: str，保存JSON格式数据的文件路径。函数会确保文件路径的父目录存在，如果不存在，会自动创建。
    
    返回值:
    无
    """
    _check_create_dirs(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        for data in datas:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
        f.close()
    pass
def addon_jsonline(data: Union[Dict, List], file_path: str):
    """
    将数据以JSON格式追加到指定文件中。

    该函数接受一个字典或列表形式的数据，将其转换为JSON格式的字符串，并追加到指定的文件中。
    如果文件不存在，该函数将创建必要的目录结构和文件。此函数用于在不删除原有数据的情况下，
    向文件中添加新的JSON数据行。

    参数:
    data (Union[Dict, List]): 需要写入文件的字典或列表数据。
    file_path (str): 数据写入的目标文件路径。

    返回:
    无
    """
    _check_create_dirs(file_path)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
        f.close()
    pass
def load_jsonlines_or_json(file_path: str) -> Union[None, List]:
    """
    尝试加载JSON Lines格式或普通JSON格式的文件数据。

    参数:
    file_path (str): 文件路径，用于尝试加载数据。

    返回:
    Union[None, List]: 成功加载时返回数据列表，加载失败时返回None。
    """
    if not os.path.exists(file_path):
        return None
    try:
        return load_jsonline(file_path)
    except:
        return load_from_json(file_path)
def load_text(file_path: str)-> str:
    """
    从指定的文件路径加载文件内容。

    如果文件不存在，则返回空字符串。此函数旨在以一种简单的方式读取文本文件内容，
    并处理文件不存在的情况。

    参数:
    file_path (str): 文件的路径。

    返回:
    str: 文件的内容或空字符串（如果文件不存在）。
    """
    if not os.path.exists(file_path):
        return ""
    with open(file_path,'r',encoding='utf-8') as f:
        contents=f.read()
        f.close()
    return contents
def save_text(data: Union[str,list,set,dict],file_path: str):
    """
    将给定的数据保存到指定的文本文件中。
    
    参数:
    data: 要保存的数据，可以是字符串、列表、集合或字典。
    file_path: 要保存文件的路径。
    
    返回:
    无
    """
    _check_create_dirs(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        if type(data)==list or type(data)==set:
            for d in data:
                f.write("{}\n".format(d))
        elif type(data)==dict:
            for k,v in data.items():
                f.write("{}\t{}\n".format(k,v))
        else:
            f.write(data)
        f.close()
    pass