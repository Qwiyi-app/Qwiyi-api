from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional



class UserNameBase(BaseModel):
    username : str

class UserBase(BaseModel):
    username : str
    firstname : str
    lastname : str
    othername : str
    email : str
    password : str
   

class UserDisplay(BaseModel):
    id : int
    first_name : str
    last_name : str
    email: Optional[str] = None
    class Config:
        orm_mode = True

