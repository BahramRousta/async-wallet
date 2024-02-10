from pydantic import BaseModel


class CreateWalletInSchema(BaseModel):
    user_id: int


class GetWalletOutSchema(BaseModel):
    user_id: int
    wallet_id: str
    balance: float
