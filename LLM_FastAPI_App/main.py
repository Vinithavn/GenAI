from fastapi import FastAPI
import models
from database import engine

from routers import llm, auth
from utils import *
from dotenv import load_dotenv
from warnings import filterwarnings
filterwarnings("ignore")

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(llm.router)
