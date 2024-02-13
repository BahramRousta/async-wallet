from typing import List
from datetime import datetime
from infrastructure.repository import WalletQueryRepository


class BaseWalletQuery:
    def __init__(self):
        self.repository = WalletQueryRepository()


class WalletQueryService(BaseWalletQuery):
    async def execute(self, user_id: int = None, wallet_id: str = None) -> dict | None:
        if user_id:
            wallet = await self.repository.get_wallet(user_id=user_id)
        else:
            wallet = await self.repository.get_wallet(wallet_id=wallet_id)

        return (
            None
            if not wallet
            else {
                "wallet_id": wallet.get("wallet_id", ""),
                "user_id": wallet.get("user_id", ""),
                "balance": wallet.get("balance", ""),
            }
        )


class WalletBalanceQueryService(BaseWalletQuery):
    async def execute(self, wallet_id: str) -> float:
        return await self.repository.get_balance(wallet_id=wallet_id)


class WalletTransactionQueryService(BaseWalletQuery):
    async def execute(self, wallet_id: str) -> List[dict]:
        return await self.repository.get_transactions(wallet_id=wallet_id)


class WalletReplyEventsQueryService(BaseWalletQuery):
    async def execute(self, wallet_id: str, from_date: str, to_date: str) -> dict:
        return await self.repository.get_events(
            wallet_id=wallet_id, from_date=from_date, to_date=to_date
        )
