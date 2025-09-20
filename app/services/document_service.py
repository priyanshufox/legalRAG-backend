# app/services/document_service.py
import os
from sqlalchemy.orm import Session
from ..models import models
from ..utils.chunker import simple_text_extractor, chunk_text
from ..utils.embeddings_client import get_embedding
from ..utils.qdrant_client import qdrant, ensure_collection
import uuid

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

def save_uploaded_file(fileobj, filename: str, db: Session, owner: str = None):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    path = os.path.join(UPLOAD_DIR, unique_name)
    with open(path, "wb") as f:
        f.write(fileobj.read())
    doc = models.Document(filename=filename, filepath=path, owner=owner)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    # process doc -> chunks -> embeddings
    text = simple_text_extractor(path)
    chunks = chunk_text(text)
    # prepare qdrant collection per user (or single collection)
    collection = f"user_{owner or 'global'}"
    # embed first chunk to get vector size
    if len(chunks) == 0:
        return doc, []
    emb0 = get_embedding(chunks[0])
    ensure_collection(collection, len(emb0))
    points = []
    chunk_objs = []
    for i, chunk in enumerate(chunks):
        emb = get_embedding(chunk)
        point_id = str(uuid.uuid4())  # Generate UUID for point ID
        points.append({"id": point_id, "vector": emb, "payload": {"doc_id": doc.id, "text": chunk}})
        # store chunk metadata in local DB
        c = models.Chunk(doc_id=doc.id, text=chunk, qdrant_point_id=point_id)
        db.add(c)
        chunk_objs.append(c)
    db.commit()
    # upsert to qdrant
    qdrant.upsert(collection_name=collection, points=points)
    return doc, chunk_objs
