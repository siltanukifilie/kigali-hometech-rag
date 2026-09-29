from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import settings
from .indexer import index_documents
from .rag import answer_question
from .store import collection


app = FastAPI(
    title="Kigali HomeTech RAG API",
    description="A small teaching API that answers from approved business documents.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "indexed_chunks": collection().count(),
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
    }


@app.post("/ingest")
def ingest() -> dict[str, object]:
    try:
        return {"status": "ready", **index_documents()}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, object]:
    try:
        return answer_question(request.question.strip())
    except RuntimeError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
