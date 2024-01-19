from dataclasses import dataclass

class Event:
    """Base event class"""


@dataclass(frozen=True)
class TransactionCreated:
    user_id: int
    wallet_id: int
    amount: float


@dataclass(frozen=True)
class FoundDeposited:
    user_id: int
    wallet_id: int
    amount: float


@dataclass
class FoundWithDrawen:
    user_id: int
    wallet_id: int
    amount: float