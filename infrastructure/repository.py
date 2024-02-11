from typing import Callable
from domain.events import WalletCreated, Deposited, Withdrawn
from domain.models import Wallet
from infrastructure.data_access import mongo_instance
from pymongo.errors import PyMongoError, DuplicateKeyError


class WalletCommandRepository:
    def __init__(self):
        self.db = mongo_instance

    async def _run_transaction(self, transaction_func: Callable):
        session = await self.db.client.start_session()

        try:
            async with session.start_transaction():
                await transaction_func(session)
        except (PyMongoError, ValueError, DuplicateKeyError) as e:
            if session.has_ended:
                raise e
        finally:
            session.end_session()

    async def create_wallet(self, event: WalletCreated) -> None:
        async def transaction_logic(session):
            wallet = Wallet(user_id=event.user_id)
            await self.db.wallet_collection.insert_one(
                document=wallet.model_dump(),
                session=session
            )
            await self.db.event_collection.insert_one(
                document=event.model_dump(),
                session=session
            )

        await self._run_transaction(transaction_logic)

    async def deposit(self, event: Deposited) -> None:
        async def transaction_logic(session):
            await self.db.wallet_collection.find_one_and_update(
                {'wallet_id': event.wallet_id},
                {'$inc': {'balance': event.amount}},
                session=session
            )
            await self.db.event_collection.insert_one(
                document=event.model_dump(),
                session=session
            )

        await self._run_transaction(transaction_logic)

    async def withdraw(self, event: Withdrawn) -> None:
        async def transaction_logic(session):
            wallet = await self.db.wallet_collection.find_one(
                {'wallet_id': event.wallet_id}, session=session
            )
            balance = wallet['balance']
            if balance <= 0:
                raise ValueError('Unable to withdraw')

            await self.db.wallet_collection.update_one(
                {'wallet_id': event.wallet_id},
                {'$inc': {'balance': -event.amount}},
                session=session
            )
            await self.db.event_collection.insert_one(event.model_dump(), session=session)

        await self._run_transaction(transaction_logic)


class WalletQueryRepository:
    def __init__(self):
        self.db = mongo_instance

    async def get_wallet(self, user_id: int = None, wallet_id: str = None) -> dict | None:

        if not wallet_id:
            wallet = await self.db.wallet_collection.find_one({'user_id': user_id})
        else:
            wallet = await self.db.wallet_collection.find_one({'wallet_id': wallet_id})
        return wallet if wallet else None

    async def get_balance(self, wallet_id: str) -> float:
        wallet = await self.get_wallet(wallet_id=wallet_id)

        if not wallet:
            raise ValueError("Could not find wallet")
        return wallet['balance']
