from datetime import datetime, timedelta
from sqlalchemy.orm.session import Session
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from config.db import get_db
from models import User


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30000




class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_name: str | None = None


class UserDisplay(BaseModel):
    id: int
    user_name: str
    email: str | None = None
    first_name: str | None = None
    is_active: bool | None = None
    class Config:
        orm_mode = True


# class UserInDB(User):
#     hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

auth_route = APIRouter(
    tags=['auth'],
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# def get_user(db, username: str):
#     user


def get_user_by_username(username: str, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.user_name == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail = f'User {username} with  not found')
    return user

# def authenticate_user(db, username:str, password: str):
#     user = db.query(User).filter(User.user_name == username).first()
#     if not user:
#          raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail = "Invalid Credentials")
#     if not verify_password(password, user.password):
#         raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail = "Incorrect Password")
#     return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(user_name=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.user_name == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail = f'User {username} with  not found')
    # user = get_user_by_username(db, id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserDisplay = Depends(get_current_user)):
    if current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@auth_route.post("/token", response_model=Token)
async def login_for_access_token(request: OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
    user = db.query(User).filter(User.user_name == request.username).first()
    if not user:
         raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail = "Invalid Credentials")
    if not verify_password(request.password, user.password):
        raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail = "Incorrect Password")
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_route.get("/users/me/", response_model=UserDisplay)
async def read_users_me(current_user: UserDisplay = Depends(get_current_user)):
    return current_user


@auth_route.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.user_name}]



