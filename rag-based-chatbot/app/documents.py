import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from .config import settings


TOKEN_PATTERN = re.compile(r"\w+(?:['’-]\w+)*|[^\w\s]", re.UNICODE)


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    path: str
    page: int
    chunk_index: int


def _display_name(path: Path) -> str:
    return path.stem.replace("_", " ")


def _lightweight_tokens(text: str) -> list[str]:
    """Return word/punctuation units for transparent beginner-friendly chunking."""
    return TOKEN_PATTERN.findall(text)


def _join_tokens(tokens: list[str]) -> str:
    text = " ".join(tokens)
    return re.sub(r"\s+([.,;:!?%)\]])", r"\1", text).strip()


def split_text(text: str, size: int, overlap: int) -> list[str]:
    if size <= 0:
        raise ValueError("CHUNK_SIZE must be greater than zero.")
    if overlap < 0 or overlap >= size:
        raise ValueError("CHUNK_OVERLAP must be between 0 and CHUNK_SIZE - 1.")

    tokens = _lightweight_tokens(re.sub(r"\s+", " ", text).strip())
    if not tokens:
        return []

    chunks: list[str] = []
    step = size - overlap
    for start in range(0, len(tokens), step):
        piece = tokens[start : start + size]
        if not piece:
            break
        chunks.append(_join_tokens(piece))
        if start + size >= len(tokens):
            break
    return chunks


def _read_pages(path: Path) -> list[tuple[int, str]]:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(path)
        return [
            (number, page.extract_text() or "")
            for number, page in enumerate(reader.pages, start=1)
        ]
    return [(1, path.read_text(encoding="utf-8"))]


def load_chunks() -> list[Chunk]:
    paths = sorted(settings.data_path.rglob("*.pdf")) + sorted(
        settings.data_path.rglob("*.txt")
    )
    chunks: list[Chunk] = []

    for path in paths:
        relative_path = path.relative_to(settings.data_path).as_posix()
        source = _display_name(path)
        for page_number, page_text in _read_pages(path):
            for index, text in enumerate(
                split_text(page_text, settings.chunk_size, settings.chunk_overlap),
                start=1,
            ):
                safe_path = relative_path.replace("/", "-").replace(" ", "_")
                chunks.append(
                    Chunk(
                        id=f"{safe_path}-p{page_number}-c{index}",
                        text=text,
                        source=source,
                        path=relative_path,
                        page=page_number,
                        chunk_index=index,
                    )
                )

    if not chunks:
        raise RuntimeError(f"No readable PDF or TXT documents found in {settings.data_path}")
    return chunks
