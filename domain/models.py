from datetime import datetime
import uuid
from pydantic import BaseModel, Field
from domain.value_objects import IRRCurrency


class Wallet(BaseModel):
    """Wallet entity"""

    wallet_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="id")
    user_id: int
    currency: IRRCurrency = "IRR"
    balance: float = Field(default=0.0, gt=0.0, description="balance must be positive")
    created_at: datetime = Field(default_factory=datetime.now)
    deleted_at: datetime = None

    class Config:
        from_attributes = True
