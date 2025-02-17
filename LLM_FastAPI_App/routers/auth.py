import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import session_local
from typing import Annotated
from sqlalchemy.orm import Session
from models import Users
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError
from datetime import timedelta, datetime, timezone

router = APIRouter(prefix="/auth",tags=["auth"])

SECRET_KEY = '433e7739907d695edaf25795244dd6853a6f2605ff87df1e41d16116e6d7f373'
ALGORITHM = "HS256"

#Here we are using the hashing algorithm called bcrypt
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oath2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateUserRequest(BaseModel):
    email:str
    username:str
    password:str
    role:str

class Token(BaseModel):
    access_token:str
    token_type:str


def get_db():
    db = session_local() # Returns a new database session
    try:
        yield db # Yield will pause the function execution here, returning the db object to the caller
    finally:
        db.close() # Close the connection after each session


db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username:str,password:str,db):
    user = db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user

def create_access_token(username:str,userid:int,role:str,
                        expires_delta:timedelta):
    encode = {'sub':username,'id':userid,'role':role}
    expired = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expired}) # add the expired time to the dict
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token:Annotated[str,Depends(oath2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username :str =payload.get('sub')
        user_id:int =payload.get('id')
        role:str=payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail = 'Could not validate user')
        return {'username':username,'id':user_id,"role":role}
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user')



@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_new_user(db:db_dependency,
                          user_request:CreateUserRequest):

    create_user_model = Users(
        email = user_request.email,
        username = user_request.username,
        hashed_password = bcrypt_context.hash(user_request.password),
        role = user_request.role,
    )
    db.add(create_user_model)
    db.commit()


@router.post("/token",response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],
                                 db:db_dependency):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user')

    token = create_access_token(user.username,user.id,
                                user.role,timedelta(minutes=20))

    return {"access_token":token,"token_type":"Bearer"}
