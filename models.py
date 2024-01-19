from pydantic import BaseModel


class User(BaseModel):
    id: int


class Wallet(BaseModel):    
    user_id: int
    balance: float
