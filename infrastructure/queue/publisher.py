import json
import aio_pika
from aio_pika import ExchangeType, DeliveryMode

from infrastructure.queue.base import channel_pool

queue_name = "logs"


async def publish_logs(data: dict) -> None:
    routing_key = "logs"
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(
            "logs",
            type=ExchangeType.DIRECT
        )

        queue = await channel.declare_queue(queue_name)

        await queue.bind(exchange, routing_key)

        message_body = json.dumps(data)
        message = aio_pika.Message(
            body=message_body.encode(),
            delivery_mode=DeliveryMode.PERSISTENT
        )

        print("send message start.")
        await exchange.publish(message=message, routing_key=routing_key)
        print("send message done.")
