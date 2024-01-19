from wallet import WalletAggeregate
from events import TransactionCreated
from models import Wallet, User
from events import FoundDeposited, FoundWithDrawen


def deposit(wallet: Wallet, aggeregate: WalletAggeregate, amount: float) -> float:
    intit_trans_event = TransactionCreated(
        user_id=wallet.user_id,
        wallet_id=wallet.wallet_id,
        amount=amount
    )

    deposit_event = FoundDeposited(
        user_id=wallet.user_id,
        wallet_id=wallet.id, 
        amount=amount
    )

    aggeregate.events.append(intit_trans_event)
    aggeregate.events.append(deposit_event)
    aggeregate.apply()

    return wallet.balance


def withdraw(wallet: Wallet, aggeregate: WalletAggeregate, amount: float) -> float:
    intit_trans_event = TransactionCreated(
        user_id=wallet.user_id,
        wallet_id=wallet.wallet_id,
        amount=amount
    )

    withdraw_event = FoundWithDrawen(
        user_id=wallet.user_id,
        wallet_id=wallet.id, 
        amount=amount
    )

    aggeregate.events.append(intit_trans_event)
    aggeregate.events.append(withdraw_event)
    aggeregate.apply()

    return wallet.balance



if __name__ == '__main__':

    user = User(id=1)

    wallet = Wallet(user_id=user.id)
    
    aggeregate = WalletAggeregate(wallet=wallet)

    deposit = deposit(aggeregate=aggeregate, wallet=wallet, amount=10000)
    