from datetime import datetime
from pydantic import BaseModel, Field


class Event(BaseModel):
    """Base class for domain events"""
    user_id: int
    created_at: datetime = Field(default_factory=datetime.now)


class WalletCreated(Event):
    balance: float = 0.0


class WalletDeleted(Event):
    pass


class Deposited(Event):
    amount: float = 0.0


class Withdrawn(Event):
    amount: float = 0.0
