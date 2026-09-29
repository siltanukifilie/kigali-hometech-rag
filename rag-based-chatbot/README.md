# RAG backend

The backend extracts and chunks the files in `data/`, creates Gemini embeddings, stores them in ChromaDB, retrieves evidence, and asks Gemini Flash Lite to answer with citations.

For the full installation, architecture, commands, and troubleshooting guide, read the [project README](../README.md).

Quick start from this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add GEMINI_API_KEY to .env
python ingest.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
