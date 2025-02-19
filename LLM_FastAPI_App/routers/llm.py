from fastapi import APIRouter,File,UploadFile,Query,Depends,HTTPException
from datetime import datetime


from llm_utils import retrieve_generate, summarizer
from typing import Optional,Annotated
from llm_utils.completion import generate
from database import session_local
from routers.auth import get_current_user
from sqlalchemy.orm import Session
from starlette import status
from models import ChatHistory
import shutil
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from warnings import filterwarnings
filterwarnings("ignore")

load_dotenv()

router = APIRouter(prefix = "/llm",tags = ["llm"])

allowed_extensions = [".pdf",".jpg",".png",".jpeg",".html",".docx"]

conn_url = os.getenv('MONGO_URI')
if conn_url is None:
    conn_url = "mongodb://localhost:27017/"
print(conn_url)

try:
    client = MongoClient(conn_url)
    db = client["your_database_name"]  # Choose your database name
    collection = db["chat_history"]  # Choose your collection name
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")


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

    # If the user fail to authenticate
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # If the user is an authenticated user
    user_id = user.get("id")
    chat_history_model = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).first()

    if chat_history_model is None:
        print("New user")
    else:
        print("Existing User")


    history_collection = list(collection.find(
        {"user_id": user_id},
        sort=[("timestamp", -1)],  # Sort by timestamp, newest first
        limit=10
    ))
    if history_collection:
        history_collection.reverse()
        chat_message_history = " ".join([chat["role"]+":"+chat["content"]+"\n" for chat in history_collection])
    else:
        chat_message_history =None

    print("CHAT HISTORY:",chat_message_history)
    print("User query:",query)


    # Get the LLM response for the query with history
    llm_response = generate(chat_message_history,query,model_name)
    print(llm_response)
    #store the chat message information to the sqlite db

    chat_history_model_new = ChatHistory(
        user_id=user_id,
        chat_title=f"{user_id}_chat")
    db.add(chat_history_model_new)
    db.commit()

    #Store the updated chat history to Mongodb
    try:
        print("Adding the user query to collection")
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
    except:
       raise HTTPException(status_code=500, detail="An error occurred during chat.")

    return llm_response


    
    
'''
A user interface where the user can chat, upload document and ask questions
or can ask the model to summarize

1. Need chat history to be saved. Load chat history of a user
2. Need a db where we can store the username, password and history
'''

    