import asyncio
import json

import aio_pika

from utils.loger import save_log_to_elk


async def process_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            await save_log_to_elk(data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")


async def main() -> None:
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/",
    )

    async with connection:
        # Creating channel
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        queue_name = "trnsx_logs"

        queue = await channel.declare_queue(queue_name)

        await queue.consume(process_message)

        try:
            # Wait until terminate
            await asyncio.Future()
        finally:
            await connection.close()

asyncio.run(main())