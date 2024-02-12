import uuid
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class Event(BaseModel):
    """Base class for domain events"""
    event_type: str
    created_at: datetime = Field(default_factory=datetime.now)

    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, 'event_type'):
            cls.event_type = cls.__name__


class WalletCreated(Event):
    user_id: int
    balance: float = 0.0


class WalletDeleted(Event):
    user_id: int
    wallet_id: str


class TransactionEvent(Event):
    """Base class for transaction events"""
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wallet_id: str
    amount: float = 0.0


class Deposited(TransactionEvent):
    pass


class Withdrawn(TransactionEvent):
    pass