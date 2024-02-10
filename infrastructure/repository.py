from domain.events import WalletCreated
from domain.models import Wallet
from infrastructure.db import mongo_instance


class WalletCommandRepository:
    def __init__(self):
        self.db = mongo_instance

    async def create_wallet(self, event: WalletCreated) -> None:
        wallet = Wallet(user_id=event.user_id)
        await self.db.wallet_collection.insert_one(wallet.model_dump())
        await self.db.event_collection.insert_one(event.model_dump())


class WalletQueryRepository:
    def __init__(self):
        self.db = mongo_instance

    async def get_wallet(self, user_id: int) -> dict | None:
        wallet = await self.db.wallet_collection.find_one({'user_id': user_id})
        return wallet if wallet else None