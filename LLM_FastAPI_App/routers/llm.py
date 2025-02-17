from fastapi import APIRouter,File,UploadFile,Query,Depends,HTTPException
from llm_utils import retrieve_generate, summarizer
from typing import Optional,Annotated
from llm_utils.competion import generate
from database import session_local
from routers.auth import get_current_user
from sqlalchemy.orm import Session
from starlette import status
import shutil
import os

router = APIRouter(prefix = "/llm",tags = ["llm"])

allowed_extensions = [".pdf",".jpg",".png",".jpeg",".html",".docx"]

def get_db():
    db = session_local() # Returns a new database session
    try:
        yield db # Yield will pause the function execution here, returning the db object to the caller
    finally:
        db.close() # Close the connection after each session

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

def upload_document(file):
    file_extension = "." + file.filename.split(".")[-1]
    if file_extension not in allowed_extensions:
        return "File format not supported"
    else:
        if not os.path.exists("input_data_files"):
            os.makedirs("input_data_files")
        else:
            shutil.rmtree("input_data_files")
            os.makedirs("input_data_files")
        temp_file_path = f'input_data_files/temp_{file.filename}'
        try:
            with open(temp_file_path,'wb') as f:
                shutil.copyfileobj(file.file,f)
            upload = True
        except:
            upload = False
        return upload

    
        
@router.post("/ask-from-document")
def ask_from_document(db:db_dependency,
                      user:user_dependency,
                      query:str,
                      model_name: str = Query('Gemini', enum=['Gemini', 'Lllama 3.2']),
                      file:UploadFile=File(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    upload = upload_document(file)
    if not upload:
        return "Unable to upload"
    else:
        doc_path = os.listdir("input_data_files")
        complete_path = ["input_data_files/"+i for i in doc_path]
        llm_response = retrieve_generate.ask_llm(query, complete_path, model_name)
        return llm_response 
    

@router.post("/summarize")
async def summarize(db:db_dependency,
                    user:user_dependency,
                    model_name: str = Query('Gemini', enum=['Gemini', 'Lllama 3.2']),
                    context:Optional[str]=None,
                    file:Optional[UploadFile] = File(None)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if not file:
        if context is not None:
            llm_response = summarizer.summarize_text(context, model_name)
            return llm_response
        else:
            return "Either upload a document or provide text to summarize"
    
    else:
        upload = upload_document(file)
        if not upload:
            return "Unable to upload"
        else:
            doc_path = os.listdir("input_data_files")
            complete_path = ["input_data_files/"+i for i in doc_path]
            llm_response = summarizer.summarize_document(complete_path, model_name)
            return llm_response
        
@router.post("/chat")
async def chat(db:db_dependency,
               user:user_dependency,
               query:str,
               model_name:str=Query('Gemini',enum=["Gemini",'Llama 3.2'])):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    llm_response = generate(query,model_name)
    return llm_response


    
    
'''
A user interface where the user can chat, upload document and ask questions
or can ask the model to summarize

1. Need chat history to be saved. Load chat history of a user
2. Need a db where we can store the username, password and history
'''

    