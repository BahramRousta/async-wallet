from pydantic import BaseModel


class CreateWalletInSchema(BaseModel):
    user_id: int


class CreateWalletOutSchema(BaseModel):
    user_id: int
    wallet_id: int
    balance: float
