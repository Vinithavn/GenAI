from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# This url is used to create a location of this database in the fastapi application
SQLALCHEMY_DATABASE_URL = "sqlite:///./llm_app.db"

#Create a database engine to open up a connection to the database
#Connect arguments are used to define the connections to the database.
#Check same thread - By default, sqllite will consider only one thread per request
#In fast api, we could have multiple threads that can interact with the db at the same time
engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       connect_args={"check_same_thread":False})

# Each instance of the session will be a database session
#autocommit and autoflush is set to false, to make sure database transactions are not done automatically
session_local = sessionmaker(autoflush=False,bind=engine)

#An object of the database which we can use to interact with the data which we create
Base = declarative_base()
