from elasticsearch import Elasticsearch


client = Elasticsearch("http://localhost:9200")

# client.indices.create(index="wallet_logs")
