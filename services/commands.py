from domain.events import WalletCreated, Deposited, Withdrawn
from infrastructure.repository import WalletCommandRepository


class BaseWalletCommand:
    def __init__(self):
        self.repository = WalletCommandRepository()


class CreateWalletCommand(BaseWalletCommand):
    async def execute(self, event: WalletCreated):
        await self.repository.create_wallet(event=event)


class DepositCommand(BaseWalletCommand):
    async def execute(self, event: Deposited):
        await self.repository.deposit(event=event)


class WithdrawCommand(BaseWalletCommand):
    async def execute(self, event: Withdrawn):
        await self.repository.withdraw(event=event)
