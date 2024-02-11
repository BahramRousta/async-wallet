from datetime import datetime
import uuid
from pydantic import BaseModel, Field, field_validator
from domain.exceptions import NegativeBalanceError
from domain.value_objects import IRRCurrency


class Wallet(BaseModel):
    """Wallet entity"""

    wallet_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='id')
    user_id: int
    currency: IRRCurrency = 'IRR'
    balance: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    deleted_at: datetime = None

    class Config:
        from_attributes = True

    @field_validator('balance')
    def balance_must_be_positive(cls, value: float) -> ValueError | float:
        if value < 0:
            raise NegativeBalanceError('balance must be positive')
        return value