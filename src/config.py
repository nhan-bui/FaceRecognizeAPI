import os
from fastapi import FastAPI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

app = FastAPI()

qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)

if not qdrant_client.collection_exists("SEARCH_FACE"):
    qdrant_client.create_collection(
        collection_name="SEARCH_FACE",
        vectors_config=VectorParams(size=512, distance=Distance.COSINE),
    )