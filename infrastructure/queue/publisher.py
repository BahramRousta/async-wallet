import asyncio
import json

import aio_pika
from aio_pika import ExchangeType


async def publish_trnsx_logs(data: dict):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/",
    )

    routing_key = "trnsx_logs"
    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange("trnsx_logs", type=ExchangeType.DIRECT)

        queue = await channel.declare_queue("trnsx_logs")

        await queue.bind(exchange, routing_key)

        message_body = json.dumps(data)

        # Convert the serialized data to bytes
        message = aio_pika.Message(body=message_body.encode())
        print("send message start.")
        await exchange.publish(message=message, routing_key=routing_key)
        print("send message done.")