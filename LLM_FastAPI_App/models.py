from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Users(Base):
    __tablename__ = "users"
    #Define the columns for the user table
    id = Column(Integer,primary_key=True,index=True)
    email = Column(String,unique=True)
    username = Column(String,unique=True)
    hashed_password = Column(String)
    role = Column(String)

class ChatHistory(Base):
    __tablename__ = "chathistory"
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer)
    chat_title = Column(String)


