from typing import Any

import chromadb

from .config import settings
from .documents import Chunk


def _client() -> chromadb.PersistentClient:
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(settings.chroma_path))


def collection():
    return _client().get_or_create_collection(
        name=settings.chroma_collection,
        metadata={"hnsw:space": "cosine"},
    )


def indexed_chunk_count() -> int:
    return collection().count()


def replace_all(chunks: list[Chunk], embeddings: list[list[float]]) -> int:
    if len(chunks) != len(embeddings):
        raise ValueError("Every chunk must have exactly one embedding.")

    client = _client()
    try:
        client.delete_collection(settings.chroma_collection)
    except Exception:
        pass

    target = collection()
    target.add(
        ids=[chunk.id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        embeddings=embeddings,
        metadatas=[
            {
                "source": chunk.source,
                "path": chunk.path,
                "page": chunk.page,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ],
    )
    return target.count()


def search(vector: list[float], limit: int) -> list[dict[str, Any]]:
    target = collection()
    if target.count() == 0:
        raise RuntimeError("The document index is empty. Run document ingestion first.")

    result = target.query(
        query_embeddings=[vector],
        n_results=min(limit, target.count()),
        include=["documents", "metadatas", "distances"],
    )
    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    return [
        {
            "text": document,
            "metadata": metadata,
            "distance": float(distance),
            "similarity": max(0.0, 1.0 - float(distance)),
        }
        for document, metadata, distance in zip(documents, metadatas, distances)
    ]
