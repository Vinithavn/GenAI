from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_ollama import ChatOllama,OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from unstructured.partition.auto import partition
from langchain_core.documents import Document 
import shutil
import os
from datetime import datetime



allowed_extensions = [".pdf",".jpg",".png",".jpeg",".html",".docx"] 

partition_function_dict = {
    ".csv":"partition_csv",    
    ".eml":"partition_email",     
    ".msg":"partition_msg",    
    ".epub":"partition_epub",    
    ".xls":"partition_xlsx",    
    ".xlsx":"partition_xlsx",    
    ".html":"partition_html",    
    ".htm":"partition_html",    
    ".bmp":"partition_image",    
    ".heic":"partition_image",    
    ".jpeg":"partition_image",     
    ".png":"partition_image",     
    ".jpg":"partition_image",    
    ".tiff":"partition_image",    
    ".md":"partition_md",    
    ".org":"partition_org",    
    ".odt":"partition_odt",    
    ".pdf":"partition_pdf",    
    ".txt":"partition_text",    
    ".text":"partition_text",    
    ".log":"partition_text",    
    ".ppt":"partition_ppt",     
    ".pptx":"partition_pptx",    
    ".rst":"partition_rst",    
    ".rtf":"partition_rtf",    
    ".tsv":"partition_tsv",    
    ".doc":"partition_doc",     
    ".docx":"partition_docx",    
    ".xml":"partition_xml" } 

def extract_text_all_formats(filenames:list[str]):  
    documents = []  
    i = 0 
    for filename in filenames:    
        extension = "."+filename.split(".")[1]    
        if extension in partition_function_dict.keys():      
            partition_function = partition_function_dict[extension]    
        else:      
            partition_function=None    
        elements = partition(filename=filename, content_type=partition_function)    
        extracted_text = "\n\n".join([str(el) for el in elements])    
        documents.append(Document(id=i, metadata={"source": filename},page_content=extracted_text,))    
        i+=1 
    return documents

def upload_document(file):
    file_extension = "." + file.filename.split(".")[-1]
    if file_extension not in allowed_extensions:
        return "File format not suppported"
    else:
        if not os.path.exists("input_data_files"):
            os.makedirs("input_data_files")
        else:
            shutil.rmtree("input_data_files")
        temp_file_path = f'LLM_App/input_data_files/temp_{file.filename}'
        try:
            with open(temp_file_path,'wb') as f:
                shutil.copyfileobj(file.file,f)
            return {"status":"Document uploaded successfully."}
        except:
            return {"status":"Unable to upload the document."}

def load_model(model_name):
    if model_name == "Gemini":
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    elif model_name == "Lllama 3.2":
        llm = ChatOllama(
        model="llama3.2",
        temperature=0,
        )
        embeddings = OllamaEmbeddings(model="llama3.2")
    else:
        llm = None,None
    return llm,embeddings

#read the document from the user 
def read_document(doc_path):
    loader = PyPDFLoader(doc_path)
    return loader.load()

def get_chat_history(collection,user_id):
    history_collection = list(collection.find(
        {"user_id": user_id},
        sort=[("timestamp", -1)],  # Sort by timestamp, newest first
        limit=10
    ))
    if history_collection:
        history_collection.reverse()
        chat_message_history = " ".join([chat["role"] + ":" + chat["content"] + "\n" for chat in history_collection])
    else:
        chat_message_history = None
    return chat_message_history

def save_chat_history(collection,user_id,query,llm_response):
    collection.insert_one({
        "user_id": user_id,
        "timestamp": datetime.now(),
        "role": "user",
        "content": query
    })
    collection.insert_one({
        "user_id": user_id,
        "timestamp": datetime.now(),
        "role": "assistant",
        "content": llm_response  # replace with actual response.
    })