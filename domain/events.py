from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class Event(BaseModel):
    """Base class for domain events"""
    user_id: int
    created_at: datetime = Field(default_factory=datetime.now)


class WalletCreated(Event):
    balance: float = 0.0


class WalletDeleted(Event):
    pass


class Deposited(BaseModel):
    wallet_id: str
    amount: float = 0.0


class Withdrawn(BaseModel):
    wallet_id: str
    amount: float = 0.0
