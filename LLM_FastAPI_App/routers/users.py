from fastapi import APIRouter,Depends,HTTPException
from routers.auth import get_current_user
from typing import Annotated
from starlette import status

from pymongo import MongoClient
import os
from dotenv import load_dotenv
from warnings import filterwarnings
filterwarnings("ignore")\

load_dotenv()

conn_url = os.getenv('MONGO_URL')

router = APIRouter(prefix = "/user",tags = ["user"])

user_dependency = Annotated[dict,Depends(get_current_user)]

def delete_chat_history(user_id, MONGO_URI):
    """Deletes chat history for a given user ID from MongoDB.

    Args:
        user_id: The ID of the user whose chat history to delete.
        MONGO_URI: The MongoDB connection URI.
    """
    try:
        with MongoClient(MONGO_URI) as client:
            db = client["your_database_name"]  # Replace with your database name
            collection = db["chat_history"]  # Replace with your collection name

            result = collection.delete_many({"user_id": user_id})

            print(f"Deleted {result.deleted_count} chat entries for user {user_id}.")


            if result.deleted_count == 0:
                print(f"No chat history found for user {user_id}.")

    except Exception as e:
        print(f"Error deleting chat history: {e}")


# Example usage:
@router.post("/delete_chat_history")
async def delete_chat(user:user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    user_id_to_delete = user.get("id")
    MONGO_URI = os.getenv("MONGO_URI") # Get URI from environment variables.
    if MONGO_URI is None:
        MONGO_URI = "mongodb://localhost:27017/" # Default URI if not set.
    delete_chat_history(user_id_to_delete, MONGO_URI)
    return f"Chat history deleted for user {user.get('username')}"