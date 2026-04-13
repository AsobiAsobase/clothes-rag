"""
知识库
"""
import  os
import config_data as config
import  hashlib
from langchain_chroma import  Chroma
from langchain_community.embeddings import  DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime
def check_md5(md5_str:str): #参数名是:md5_str,str是数据类型
    """检查传入的md5字符串是否已经被处理过了
    return False(md5未处理过) True(已经处理过，以后记录)
    """
    if not os.path.exists(config.md5_path):
        #if进入表示文件不存在，那肯定没有处理过这个md5了
        open(config.md5_path, 'w', encoding='utf-8').close()
        return  False
    else:
        for line in open(config.md5_path,'r',encoding='utf-8').readlines():
            line = line.strip()#处理字符串前后的空格和回车
            if line == md5_str:
                return True #已处理过
        return False
def save_md5(md5_str:str):
    """将传入的md5字符串，记录到文件里保存"""
    with open(config.md5_path,'a',encoding="utf-8") as f:
        f.write(md5_str + '\n')
def get_string_md5(input_str,encoding='utf-8'):
    """将传入的字符串转换为md5字符串"""
    md5_obj = hashlib.md5()  # 创建一个 MD5 计算器对象
    str_bytes = input_str.encode(encoding)  # 把字符串转成字节（MD5 只认字节）
    md5_obj.update(str_bytes)  # 把字节喂给 MD5 计算器
    md5_hex = md5_obj.hexdigest()  # 取出计算好的 MD5 值（32位十六进制字符串）
    return md5_hex  # 返回 MD5 值
    pass
class KnowledgeBaseService(object):
    def __init__(self):
        #如果文件夹不存在则创建，如果存在则跳过
        os.makedirs(config.persist_directory,exist_ok=True)
        self.chroma = Chroma(
             collection_name=config.collection_name,
             embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
             persist_directory=config.persist_directory,
        )  #向量存储的实例Chroma向量库对象
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            length_function=len,
        ) #文本分割器的对象

    def upload_by_str(self, data: str, filename):
        """将传入的字符串，进行向量化，存入向量数据库中"""
        md5_hex = get_string_md5(data)
        if check_md5(md5_hex):
            return "[跳过]内容已经存在知识库中"
        if len(data) > config.max_split_char_number:
            knowledge_chunks = self.splitter.split_text(data)
        else:
            knowledge_chunks = [data]
        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "小曹"
        }
        self.chroma.add_texts(
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks],
        )
        save_md5(md5_hex)
        return "[成功]内容已经成功载入向量库"
if __name__ == '__main__':
    service = KnowledgeBaseService()
    r = service.upload_by_str("周杰伦","testfile")
    print(r)