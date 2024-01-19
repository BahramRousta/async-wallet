from models import Wallet
from events import TransactionCreated, FoundWithDrawen, FoundDeposited
from db import EventStore


class WalletAggeregate:

    def __init__(self, wallet: Wallet) -> None:
        self.wallet = wallet
        self.events = []
        self.event_store_repository = EventStore()
    
    def deposit(self, amount: float):
        self.wallet.balance += amount

    def withdraw(self, amount: float):

        if amount <= 0:
            raise ValueError("Amonut can not be negetive.")

        self.wallet.balance -= amount
    
    def apply(self):
        try:
            for event in self.events:

                if isinstance(event, FoundDeposited):
                    self.deposit(event.amount)
                
                elif isinstance(event, FoundWithDrawen):
                    self.withdraw(event.amount)

        except Exception:
            raise ValueError("Unexepted event")
