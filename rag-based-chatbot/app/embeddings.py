from google import genai
from google.genai import types

from .config import require_api_key, settings


def _client() -> genai.Client:
    require_api_key()
    return genai.Client(api_key=settings.gemini_api_key)


def _content(text: str) -> types.Content:
    return types.Content(parts=[types.Part.from_text(text=text)])


def embed_documents(items: list[tuple[str, str]]) -> list[list[float]]:
    """Embed (title, text) pairs in small batches."""
    client = _client()
    vectors: list[list[float]] = []
    batch_size = settings.embedding_batch_size

    for start in range(0, len(items), batch_size):
        batch = items[start : start + batch_size]
        contents = [
            _content(f"title: {title or 'none'} | text: {text}")
            for title, text in batch
        ]
        response = client.models.embed_content(
            model=settings.embedding_model,
            contents=contents,
            config=types.EmbedContentConfig(
                output_dimensionality=settings.embedding_dimensions
            ),
        )
        if not response.embeddings or len(response.embeddings) != len(batch):
            raise RuntimeError("Gemini returned an unexpected number of embeddings.")
        vectors.extend([list(item.values or []) for item in response.embeddings])

    return vectors


def embed_question(question: str) -> list[float]:
    client = _client()
    response = client.models.embed_content(
        model=settings.embedding_model,
        contents=f"task: question answering | query: {question}",
        config=types.EmbedContentConfig(
            output_dimensionality=settings.embedding_dimensions
        ),
    )
    if not response.embeddings:
        raise RuntimeError("Gemini did not return a query embedding.")
    return list(response.embeddings[0].values or [])
