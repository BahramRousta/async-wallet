import asyncio
import json
import aio_pika

from infrastructure.els import save_log_to_elk
from infrastructure.queue.base import channel_pool


async def process_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            await save_log_to_elk(data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")


async def consume() -> None:

    async with channel_pool.acquire() as channel:
        await channel.set_qos(10)

        queue = await channel.declare_queue(
            "logs", durable=False, auto_delete=False,
        )

        await queue.consume(process_message, no_ack=False)

        print(" [*] Waiting for messages. To exit press CTRL+C")
        await asyncio.Future()


asyncio.run(consume())