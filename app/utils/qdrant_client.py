# app/utils/qdrant_client.py
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
qdrant = QdrantClient(url=QDRANT_URL)

def ensure_collection(collection_name: str, vector_size: int):
    # create collection if not exists (simple config)
    try:
        # Try to get the collection info to check if it exists
        qdrant.get_collection(collection_name=collection_name)
    except Exception:
        # Collection doesn't exist, create it
        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config={"size": vector_size, "distance": "Cosine"}
        )
