import re
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pypdf import PdfReader

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


MAX_PDF_BYTES = 10 * 1024 * 1024


def document_count() -> int:
    return len(list(settings.data_path.rglob("*.pdf"))) + len(
        list(settings.data_path.rglob("*.txt"))
    )


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "indexed_chunks": collection().count(),
        "indexed_documents": document_count(),
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
    }


@app.post("/ingest")
def ingest() -> dict[str, object]:
    try:
        return {"status": "ready", **index_documents()}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.post("/documents/upload")
def upload_document(file: UploadFile = File(...)) -> dict[str, object]:
    original_name = Path(file.filename or "").name
    if Path(original_name).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF documents are allowed.")

    contents = file.file.read(MAX_PDF_BYTES + 1)
    file.file.close()
    if not contents:
        raise HTTPException(status_code=400, detail="The selected PDF is empty.")
    if len(contents) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="The PDF must be 10 MB or smaller.")
    if not contents.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The selected file is not a valid PDF.")

    try:
        reader = PdfReader(BytesIO(contents))
        readable_pages = sum(bool((page.extract_text() or "").strip()) for page in reader.pages)
    except Exception as error:
        raise HTTPException(status_code=400, detail="The PDF could not be read.") from error
    if readable_pages == 0:
        raise HTTPException(
            status_code=400,
            detail="The PDF has no readable text. Scanned PDFs need OCR before upload.",
        )

    safe_stem = re.sub(r"[^A-Za-z0-9_-]+", "_", Path(original_name).stem).strip("_")
    destination = settings.data_path / f"{safe_stem or 'uploaded_document'}.pdf"
    if destination.exists():
        raise HTTPException(
            status_code=409,
            detail=f"{destination.name} already exists. Rename the PDF before uploading it.",
        )

    destination.write_bytes(contents)
    try:
        result = index_documents()
    except Exception as error:
        destination.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail=f"The PDF was valid, but indexing failed: {error}",
        ) from error

    return {
        "status": "ready",
        "filename": destination.name,
        "uploaded_pages": len(reader.pages),
        **result,
    }


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, object]:
    try:
        return answer_question(request.question.strip())
    except RuntimeError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
