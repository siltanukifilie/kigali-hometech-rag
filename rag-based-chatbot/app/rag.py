import re
from typing import Any

from google import genai
from google.genai import types

from .config import require_api_key, settings
from .embeddings import embed_question
from .store import indexed_chunk_count, search


def _source_label(metadata: dict[str, Any]) -> str:
    page = metadata.get("page")
    return f"{metadata.get('source', 'Unknown document')}, page {page}"


def answer_question(question: str) -> dict[str, Any]:
    require_api_key()
    query_vector = embed_question(question)
    candidates = search(query_vector, settings.top_k * 2)
    matches = []
    seen_pages = set()
    for candidate in candidates:
        metadata = candidate["metadata"]
        key = (metadata.get("path"), metadata.get("page"))
        if key in seen_pages:
            continue
        seen_pages.add(key)
        matches.append(candidate)
        if len(matches) == settings.top_k:
            break

    context_blocks = []
    for index, match in enumerate(matches, start=1):
        label = _source_label(match["metadata"])
        context_blocks.append(f"[Source {index}: {label}]\n{match['text']}")

    prompt = f"""You are the customer-support assistant for Kigali HomeTech Store.

Rules:
- Answer only from the approved document excerpts below.
- If the excerpts do not contain the answer, say: "I do not know from the available business documents."
- Do not invent policies, dates, prices, or conditions.
- Keep the answer clear and concise for a customer.
- Cite each supported claim with one or more evidence numbers such as [Source 1].
- Use only the source numbers provided below. Never invent or combine page numbers.

Customer question:
{question}

Approved document excerpts:
{chr(10).join(context_blocks)}
"""

    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.llm_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=500,
        ),
    )

    answer = response.text or "I do not know from the available business documents."
    sources = []
    labels: dict[int, str] = {}
    for index, match in enumerate(matches, start=1):
        metadata = match["metadata"]
        label = _source_label(metadata)
        labels[index] = label
        sources.append(
            {
                "reference": index,
                "document": metadata.get("source"),
                "path": metadata.get("path"),
                "page": metadata.get("page"),
                "similarity": round(match["similarity"], 4),
            }
        )

    verified_references: set[int] = set()

    def verified_citation(match: re.Match[str]) -> str:
        references = [int(number) for number in re.findall(r"\d+", match.group(0))]
        valid_references = [number for number in references if number in labels]
        verified_references.update(valid_references)
        verified = [labels[number] for number in valid_references]
        return f"[{'; '.join(verified)}]" if verified else ""

    answer = re.sub(
        r"\[Source\s+\d+(?:\s*,\s*Source\s+\d+)*\]",
        verified_citation,
        answer,
    )

    retrieved_evidence = []
    for index, match in enumerate(matches, start=1):
        metadata = match["metadata"]
        text = match["text"].strip()
        retrieved_evidence.append(
            {
                "reference": index,
                "document": metadata.get("source"),
                "page": metadata.get("page"),
                "similarity": round(match["similarity"], 4),
                "snippet": f"{text[:220]}{'…' if len(text) > 220 else ''}",
            }
        )

    trace = {
        "question": {
            "text": question,
            "characters": len(question),
        },
        "embedding": {
            "model": settings.embedding_model,
            "dimensions": len(query_vector),
            "preview": [round(value, 6) for value in query_vector[:8]],
        },
        "search": {
            "database": "ChromaDB",
            "collection": settings.chroma_collection,
            "metric": "cosine similarity",
            "indexed_chunks": indexed_chunk_count(),
            "candidates_returned": len(candidates),
        },
        "retrieval": {
            "unique_pages_selected": len(matches),
            "top_k": settings.top_k,
            "evidence": retrieved_evidence,
        },
        "augmentation": {
            "question_added": True,
            "evidence_blocks_added": len(context_blocks),
            "instruction": "Answer only from approved evidence and cite its source numbers.",
            "prompt_preview": (
                f"Customer question: {question}\n\n"
                f"Approved evidence: {', '.join(labels.values())}"
            ),
        },
        "generation": {
            "model": settings.llm_model,
            "temperature": 0.1,
            "citations_verified": len(verified_references),
            "answer": answer,
        },
    }

    return {
        "answer": answer,
        "sources": sources,
        "trace": trace,
    }
