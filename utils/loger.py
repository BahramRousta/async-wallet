from infrastructure.els import client as elk


async def save_log_to_elk(data: dict) -> None:
    elk.index(
        index=data["index"],
        document={
            "message": data["message"],
            "success": data["success"],
            "wallet_id": data["wallet_id"],
            "amount": data["amount"],
            "timestamp": data["timestamp"]
        }
    )