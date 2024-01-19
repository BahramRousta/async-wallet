from pydantic import BaseModel
from pydantic.dataclasses import dataclass


class WalletEvent(BaseModel):
    """Base wallet event class"""
    user_id: int
    wallet_id: int


@dataclass(frozen=True)
class TransactionCreated(BaseModel):
    amount: float


@dataclass(frozen=True)
class FoundDeposited(BaseModel):
    amount: float


@dataclass
class FoundWithDrawn(BaseModel):
    amount: float
