from domain.events import WalletCreated
from infrastructure.repository import WalletCommandRepository


class CreateWalletCommand:

    def __init__(self):
        self.repository = WalletCommandRepository()

    async def execute(self, event: WalletCreated):
        await self.repository.create_wallet(event=event)

