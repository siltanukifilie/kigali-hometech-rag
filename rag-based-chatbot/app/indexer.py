from .documents import load_chunks
from .embeddings import embed_documents
from .store import replace_all


def index_documents() -> dict[str, int]:
    chunks = load_chunks()
    vectors = embed_documents([(chunk.source, chunk.text) for chunk in chunks])
    stored = replace_all(chunks, vectors)
    return {
        "documents": len({chunk.path for chunk in chunks}),
        "pages": len({(chunk.path, chunk.page) for chunk in chunks}),
        "chunks": stored,
    }
