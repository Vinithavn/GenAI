from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from unstructured.partition.auto import partition
from langchain_core.documents import Document 


def load_model(model_name):
    if model_name == "Gemini":
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    elif model_name == "Lllama 3.2":
        llm = ChatOllama(
        model="llama3.2",
        temperature=0,
        )
    else:
        llm = None
    return llm

#read the document from the user 
def read_document(doc_path):
    loader = PyPDFLoader(doc_path)
    return loader.load()


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

