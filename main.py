import time
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
)
from services.commands import CreateWalletCommand, DepositCommand, WithdrawCommand
from services.queries import (
    WalletQueryService,
    WalletBalanceQueryService,
    WalletTransactionQueryService,
    WalletReplyEventsQueryService,
)
from presentation.schemas import BaseResponse
from infrastructure.els import client as es


app = FastAPI()


@app.on_event("startup")
async def startup():
    await mongo_instance.client.start_session()


@app.post("/create-wallet/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_wallet(user_id: int) -> BaseResponse:
    """
    Create a new wallet for the given user ID.

    Args:
        user_id (int): The ID of the user for whom the wallet will be created.

    Returns:
        dict: Response containing the details of the created wallet.
    """

    existing_wallet = await WalletQueryService().execute(user_id=user_id)

    if existing_wallet:
        es.index(
            index="wallet_logs",
            document={
                "message": "Wallet created failed",
                "success": False,
                "user_id": user_id,
                "timestamp": datetime.now(),
            },
        )
        raise HTTPException(status_code=400, detail="Wallet already exists")

    wallet = Wallet(user_id=user_id)
    event = WalletCreated(user_id=user_id, wallet_id=wallet.wallet_id)
    await CreateWalletCommand().execute(event)
    es.index(
        index="wallet_logs",
        document={
            "message": "Wallet created successfully",
            "success": True,
            "user_id": user_id,
            "timestamp": datetime.timestamp(datetime.now()),
        },
    )
    return BaseResponse(
        data=event.model_dump(),
        message="Wallet created successfully",
        status=status.HTTP_201_CREATED,
        success=True,
    )


@app.get(
    "/get-wallet/{user_id}",
    response_model=GetWalletOutSchema,
    status_code=status.HTTP_200_OK,
)
async def get_wallet(user_id: int) -> dict:
    """
    Retrieve the details of the wallet associated with the given user ID.

    Args:
        user_id (int): The ID of the user.

    Returns:
        dict: Details of the wallet.
    """

    existing_wallet = await WalletQueryService().execute(user_id=user_id)

    if not existing_wallet:
        raise HTTPException(status_code=404, detail="Wallet does not exist.")

    return existing_wallet


@app.post("/deposit/")
async def deposit(deposit: DepositIn) -> BaseResponse:
    """
    Deposit funds into a wallet.

    Args:
        deposit (DepositIn): Input data containing wallet ID and amount to be deposited.

    Returns:
        dict: Response containing details of the deposit transaction.
    """

    wallet_id = deposit.wallet_id
    existing_wallet = await WalletQueryService().execute(wallet_id=wallet_id)

    if not existing_wallet:
        raise HTTPException(status_code=404, detail="Wallet does not exist.")

    event = Deposited(wallet_id=wallet_id, amount=deposit.amount)
    await DepositCommand().execute(event=event)

    return BaseResponse(
        data=event.model_dump(),
        message="Deposit successful",
        status=status.HTTP_200_OK,
        success=True,
    )


@app.post("/withdraw/")
async def withdraw(withdraw: WithdrawIn) -> BaseResponse:
    """
    Withdraw funds from a wallet.

    Args:
        withdraw (WithdrawIn): Input data containing wallet ID and amount to be withdrawn.

    Returns:
        dict: Response containing details of the withdrawal transaction.
    """

    wallet_id = withdraw.wallet_id
    existing_wallet = await WalletQueryService().execute(wallet_id=wallet_id)

    if not existing_wallet:
        raise HTTPException(status_code=404, detail="Wallet does not exist.")

    event = Withdrawn(wallet_id=wallet_id, amount=withdraw.amount)
    try:
        await WithdrawCommand().execute(event=event)

        return BaseResponse(
            data=event.model_dump(),
            message="Withdrawal successful",
            status=status.HTTP_200_OK,
            success=True,
        )
    except Exception as e:
        return BaseResponse(
            data=e.args,
            message="Withdrawal failed",
            status=status.HTTP_400_BAD_REQUEST,
            success=False,
        )


@app.get("/balance/{wallet_id}/")
async def wallet_balance(wallet_id: str) -> BaseResponse:
    """
    Retrieve the balance of a wallet.

    Args:
        wallet_id (str): The ID of the wallet.

    Returns:
        dict: Response containing the balance of the wallet.
    """
    try:
        balance = await WalletBalanceQueryService().execute(wallet_id=wallet_id)
        return BaseResponse(
            data={"balance": balance},
            message="",
            status=status.HTTP_200_OK,
            success=True,
        )
    except Exception as e:
        return BaseResponse(
            data=e.args,
            message="Failed to retrieve balance.",
            status=status.HTTP_400_BAD_REQUEST,
            success=False,
        )


@app.get("/transactions/{wallet_id}/")
async def wallet_transactions(wallet_id: str) -> List[dict] | dict:
    """
    Retrieve the transactions of a wallet.

    Args:
        wallet_id (str): The ID of the wallet.

    Returns:
        Union[List[dict], dict]: List of transactions or error response.
    """

    try:
        transactions: list = await WalletTransactionQueryService().execute(wallet_id)
        return transactions
    except Exception as e:
        return {
            "data": e.args,
            "message": "Failed to retrieve transactions.",
            "status": status.HTTP_400_BAD_REQUEST,
        }


@app.get("/events/{wallet_id}/")
async def reply_events(wallet_id: str, from_date: str, to_date: str) -> dict:
    """
    Retrieve events for a wallet within the specified date range.

    Args:
        wallet_id (str): The ID of the wallet.
        from_date (str): Start date of the date range (format: YYYY-MM-DD).
        to_date (str): End date of the date range (format: YYYY-MM-DD).

    Returns:
        dict: Response containing the events within the specified date range.
    """

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
