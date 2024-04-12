from elasticsearch import AsyncElasticsearch


elk = AsyncElasticsearch("http://localhost:9200",maxsize=10)


async def save_log_to_elk(data: dict) -> None:
    await elk.index(
        index=data["index"],
        document=data["document"]
    )

