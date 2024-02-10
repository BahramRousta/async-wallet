from domain.events import Event, Deposited, Withdrawn
from services.commands import WalletDepositCommandService


class WalletAggregator:
    def __init__(self, wallet_id, user_id):
        self.wallet_id = wallet_id
        self.user_id = user_id
        self.events = []

    def deposit(self, event: Event) -> None:
        self.apply(event)

    def withdraw(self, event: Event) -> None:
        self.apply(event)

    def apply(self, event: Event) -> None:

        if isinstance(event, Deposited):
            WalletDepositCommandService.execute(wallet_id=self.wallet_id)

        if isinstance(event, Withdrawn):
            self.wallet_id.withdraw(amount=event.amount)
