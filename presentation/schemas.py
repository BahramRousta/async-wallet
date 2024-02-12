import datetime
from pydantic import BaseModel, field_validator


class CreateWalletInSchema(BaseModel):
    user_id: int


class GetWalletOutSchema(BaseModel):
    user_id: int
    wallet_id: str
    balance: float


class DepositIn(BaseModel):
    wallet_id: str
    amount: float

    @field_validator('amount')
    def amount_must_be_positive(cls, value):
        if value < 0:
            raise ValueError('amount must be positive')

        return value


class WithdrawIn(BaseModel):
    wallet_id: str
    amount: float

    @field_validator('amount')
    def amount_must_be_positive(cls, value):
        if value < 0:
            raise ValueError('amount must be positive')

        return value


class BalanceOut(BaseModel):
    balance: float


class TransactionOut(BaseModel):
    event_type: str
    created_at: datetime.datetime
    transaction_id: str
    amount: float