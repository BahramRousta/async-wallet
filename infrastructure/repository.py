from typing import Callable, List
from domain.events import WalletCreated, Deposited, Withdrawn
from domain.models import Wallet
from infrastructure.data_access import mongo_instance
from pymongo.errors import PyMongoError, DuplicateKeyError


class WalletCommandRepository:
    def __init__(self):
        self.db = mongo_instance
        self.wallet_collection = None
        self.event_collection = None

    async def _initialize_collections(self):
        self.wallet_collection = await self.db.wallet_collection
        self.event_collection = await self.db.event_collection

    async def _run_transaction(self, transaction_func: Callable):

        try:
            async with await self.db.client.start_session() as session:
                async with session.start_transaction():
                    await transaction_func(session)
        except (PyMongoError, ValueError, DuplicateKeyError) as e:
            raise e

    async def create_wallet(self, event: WalletCreated) -> None:
        if not self.wallet_collection or not self.event_collection:
            await self._initialize_collections()

        async def transaction_logic(session):
            wallet = Wallet(user_id=event.user_id)

            await self.wallet_collection.insert_one(
                document=wallet.model_dump(),
                session=session
            )
            await self.event_collection.insert_one(
                document=event.model_dump(),
                session=session
            )

        await self._run_transaction(transaction_logic)

    async def deposit(self, event: Deposited) -> None:
        if not self.wallet_collection or not self.event_collection:
            await self._initialize_collections()

        async def transaction_logic(session):
            await self.wallet_collection.find_one_and_update(
                {'wallet_id': event.wallet_id},
                {'$inc': {'balance': event.amount}},
                session=session
            )
            await self.event_collection.insert_one(
                document=event.model_dump(),
                session=session
            )

        await self._run_transaction(transaction_logic)

    async def withdraw(self, event: Withdrawn) -> None:
        if not self.wallet_collection or not self.event_collection:
            await self._initialize_collections()

        async def transaction_logic(session):
            wallet = await self.wallet_collection.find_one(
                {'wallet_id': event.wallet_id}, session=session
            )

            balance = wallet['balance']
            if event.amount > balance:
                raise ValueError('Unable to withdraw')

            await self.wallet_collection.update_one(
                {'wallet_id': event.wallet_id},
                {'$inc': {'balance': -event.amount}},
                session=session
            )
            await self.event_collection.insert_one(event.model_dump(), session=session)

        await self._run_transaction(transaction_logic)


class WalletQueryRepository:
    def __init__(self):
        self.db = mongo_instance
        self.wallet_collection = None
        self.event_collection = None

    async def _initialize_collections(self):
        self.wallet_collection = await self.db.wallet_collection
        self.event_collection = await self.db.event_collection

    async def get_wallet(self, user_id: int = None, wallet_id: str = None) -> dict | None:
        if not self.wallet_collection or not self.event_collection:
            await self._initialize_collections()

        if not wallet_id:
            wallet = await self.wallet_collection.find_one({'user_id': user_id})
        else:
            wallet = await self.wallet_collection.find_one({'wallet_id': wallet_id})
        return wallet if wallet else None

    async def get_balance(self, wallet_id: str) -> float:
        wallet = await self.get_wallet(wallet_id=wallet_id)

        if not wallet:
            raise ValueError("Could not find wallet")
        return wallet['balance']

    async def get_transactions(self, wallet_id: str) -> List[dict]:
        if not self.wallet_collection or not self.event_collection:
            await self._initialize_collections()
        documents = self.event_collection.find({'wallet_id': wallet_id}, {'_id': 0, 'wallet_id': 0})
        transactions = [document async for document in documents]
        return transactions
