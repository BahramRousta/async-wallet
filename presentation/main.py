from typing import List
from datetime import datetime
from fastapi import FastAPI, status, HTTPException
from domain.events import WalletCreated, Deposited, Withdrawn
from domain.models import Wallet
from infrastructure.data_access import mongo_instance
from presentation.schemas import (
    GetWalletOutSchema,
    DepositIn,
    WithdrawIn,
    TransactionOut,
)
from services.commands import CreateWalletCommand, DepositCommand, WithdrawCommand
from services.queries import (
    WalletQueryService,
    WalletBalanceQueryService,
    WalletTransactionQueryService,
    WalletReplyEventsQueryService,
)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await mongo_instance.client.start_session()


@app.post("/create-wallet/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_wallet(user_id: int) -> dict:

    existing_wallet = await WalletQueryService().execute(user_id=user_id)

    if existing_wallet:
        raise HTTPException(status_code=400, detail="Wallet already exists")

    wallet = Wallet(user_id=user_id)
    event = WalletCreated(user_id=user_id, wallet_id=wallet.wallet_id)
    await CreateWalletCommand().execute(event)

    return {
        "data": event.model_dump(),
        "message": "Wallet created successfully",
        "status": status.HTTP_201_CREATED,
    }


@app.get(
    "/get-wallet/{user_id}",
    response_model=GetWalletOutSchema,
    status_code=status.HTTP_200_OK,
)
async def get_wallet(user_id: int) -> dict:
    existing_wallet = await WalletQueryService().execute(user_id=user_id)

    if not existing_wallet:
        raise HTTPException(status_code=404, detail="Wallet does not exist.")

    return existing_wallet


@app.post("/deposit/")
async def deposit(deposit: DepositIn) -> dict:

    wallet_id = deposit.wallet_id
    existing_wallet = await WalletQueryService().execute(wallet_id=wallet_id)

    if not existing_wallet:
        raise HTTPException(status_code=404, detail="Wallet does not exist.")

    event = Deposited(wallet_id=wallet_id, amount=deposit.amount)
    await DepositCommand().execute(event=event)

    return {
        "data": event.model_dump(),
        "message": "Wallet created successfully",
        "status": status.HTTP_200_OK,
    }


@app.post("/withdraw/")
async def withdraw(withdraw: WithdrawIn) -> dict:
    wallet_id = withdraw.wallet_id
    existing_wallet = await WalletQueryService().execute(wallet_id=wallet_id)

    if not existing_wallet:
        raise HTTPException(status_code=404, detail="Wallet does not exist.")

    event = Withdrawn(wallet_id=wallet_id, amount=withdraw.amount)
    try:
        await WithdrawCommand().execute(event=event)

        return {
            "data": event.model_dump(),
            "message": "Wallet created successfully",
            "status": status.HTTP_200_OK,
        }
    except Exception as e:
        return {
            "data": e.args,
            "message": "Withdraw failed.",
            "status": status.HTTP_400_BAD_REQUEST,
        }


@app.get("/balance/{wallet_id}/")
async def wallet_balance(wallet_id: str) -> dict:
    try:
        balance = await WalletBalanceQueryService().execute(wallet_id=wallet_id)
        return {"balance": balance}
    except Exception as e:
        return {
            "data": e.args,
            "message": "Withdraw failed.",
            "status": status.HTTP_400_BAD_REQUEST,
        }


@app.get("/transactions/{wallet_id}/")
async def wallet_transactions(wallet_id: str) -> List[dict] | dict:
    try:
        transactions: list = await WalletTransactionQueryService().execute(wallet_id)
        return transactions
    except Exception as e:
        return {"data": e.args, "message": "", "status": status.HTTP_400_BAD_REQUEST}


@app.get("/events/{wallet_id}/")
async def reply_events(wallet_id: str, from_date: str, to_date: str) -> dict:
    try:
        from_date_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_date_dt = datetime.strptime(to_date, "%Y-%m-%d")

        wallet_events: dict = await WalletReplyEventsQueryService().execute(
            wallet_id, from_date_dt, to_date_dt
        )

        return wallet_events

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
