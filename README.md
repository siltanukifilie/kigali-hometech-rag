# Kigali HomeTech RAG Chatbot

A small, beginner-friendly Retrieval-Augmented Generation (RAG) project. The chatbot searches approved Kigali HomeTech Store documents before asking Gemini to answer, and it returns the document names and page numbers used as evidence.

## What this project demonstrates

1. Read PDF and text documents.
2. Split long pages into overlapping chunks.
3. Convert every chunk into a 768-number embedding with Gemini.
4. Store the text, embeddings, and source metadata in ChromaDB.
5. Convert a customer's question into an embedding.
6. Retrieve the most relevant chunks and keep four unique source pages.
7. Add those chunks to a controlled prompt.
8. Ask Gemini Flash Lite to answer only from that evidence.
9. Show the answer together with document and page sources.

```text
Documents → Text → Chunks → Gemini Embeddings → ChromaDB
                                                    ↓
Customer question → Query embedding → Relevant chunks
                                                    ↓
                         Prompt + Gemini LLM → Answer + sources
```

## Technology choices

| Part | Choice | Why |
| --- | --- | --- |
| Backend | Python + FastAPI | Small, readable API with automatic documentation |
| PDF extraction | pypdf | Simple local PDF text extraction |
| Embeddings | `gemini-embedding-2` | Converts meaning into vectors for semantic search |
| Embedding dimensions | 768 | Good balance of quality, speed, and storage |
| Vector database | ChromaDB | Easy local persistent database for a learning project |
| LLM | `gemini-3.5-flash-lite` | Fast and suitable for a small demonstration |
| Frontend | Vanilla JavaScript + Vite | Lightweight interface with very little code |

This project originally planned to use `gemini-2.5-flash-lite`. During the live test, the Gemini API reported that this model is unavailable to new accounts and directed new projects to `gemini-3.5-flash-lite`. The project therefore uses the current stable Flash-Lite model.

## Verified development result

The complete flow was tested on September 29, 2026:

- All five PDFs were confirmed to contain five pages each.
- The five PDFs and one FAQ file produced 27 chunks across 26 source pages.
- Gemini successfully generated 768-dimensional embeddings.
- ChromaDB persisted and retrieved the 27 chunks.
- A return-policy question produced a grounded answer with verified page citations.
- An unsupported CEO-salary question returned: `I do not know from the available business documents.`
- The FastAPI health endpoint returned HTTP 200 with 27 indexed chunks.
- The browser CORS check passed for the frontend on port `5174`.
- The Vite frontend production build completed successfully.

## Folder structure

```text
kigali-hometech-rag/
├── rag-based-chatbot/
│   ├── app/
│   │   ├── config.py       # Reads environment settings
│   │   ├── documents.py    # Extracts and chunks document text
│   │   ├── embeddings.py   # Calls the Gemini Embedding API
│   │   ├── indexer.py      # Coordinates document indexing
│   │   ├── store.py        # Saves and searches ChromaDB
│   │   ├── rag.py          # Builds the prompt and calls the LLM
│   │   └── main.py         # FastAPI endpoints
│   ├── data/               # Approved sample business documents
│   ├── .env.example
│   ├── ingest.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── .env.example
│   ├── index.html
│   └── package.json
├── .gitignore
└── README.md
```

## 1. Get the project

```bash
git clone https://github.com/siltanukifilie/kigali-hometech-rag.git
cd kigali-hometech-rag
```

If it is already cloned:

```bash
cd ~/kigali-hometech-rag
git pull
```

## 2. Configure the backend

```bash
cd rag-based-chatbot
cp .env.example .env
```

Open `.env` and add the API key created in Google AI Studio:

```env
GEMINI_API_KEY=your_private_key_here
```

The complete backend configuration is:

```env
GEMINI_API_KEY=
LLM_MODEL=gemini-3.5-flash-lite
EMBEDDING_MODEL=gemini-embedding-2
EMBEDDING_DIMENSIONS=768
EMBEDDING_BATCH_SIZE=10
CHUNK_SIZE=350
CHUNK_OVERLAP=60
TOP_K=4
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION=kigali_hometech_documents
HOST=127.0.0.1
PORT=8000
CORS_ORIGINS=http://127.0.0.1:5174,http://localhost:5174
```

Never commit `.env`. The repository's `.gitignore` protects it.

## 3. Install backend dependencies

Use a virtual environment so the packages are isolated from the rest of the computer:

```bash
cd ~/kigali-hometech-rag/rag-based-chatbot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Index the documents

Run this once after adding or changing documents:

```bash
python ingest.py
```

What happens during indexing:

1. `pypdf` extracts text page by page so page numbers are preserved.
2. The text is split into approximately 350 word/punctuation units.
3. Consecutive chunks overlap by 60 units so information at a boundary is not lost.
4. Every chunk is sent to `gemini-embedding-2` using the document-search format.
5. Gemini returns 768 numbers for each chunk.
6. ChromaDB stores the vector, original text, filename, page, and chunk number.
7. The local database is saved in `rag-based-chatbot/chroma_db/`.

Re-running ingestion safely rebuilds this learning project's collection from the current documents.

## 5. Start the backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Useful addresses:

- API status: <http://127.0.0.1:8000/health>
- Interactive API documentation: <http://127.0.0.1:8000/docs>

The backend endpoints are:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Check the API and indexed chunk count |
| POST | `/ingest` | Rebuild the document index |
| POST | `/chat` | Ask a question and receive an answer with sources |

Example API question:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Can I return a blender after 14 days?"}'
```

## 6. Start the frontend

Open a second terminal:

```bash
cd ~/kigali-hometech-rag/frontend
cp .env.example .env
npm install
npm run dev
```

Open <http://127.0.0.1:5174>.

Port `5173` was already occupied on the development computer, so this project uses:

- Backend: `8000`
- Frontend: `5174`

## How one question is answered

For the question **“Can I return a blender after 14 days?”**:

1. The backend formats it as a question-answering search query.
2. Gemini converts it to a 768-dimensional query embedding.
3. ChromaDB compares that vector with all stored document vectors using cosine distance.
4. ChromaDB returns candidate chunks; the backend removes duplicate pages and keeps the four best unique pages.
5. The backend creates a prompt containing numbered evidence blocks with filenames and pages.
6. The prompt tells Gemini to use only the excerpts and say it does not know when evidence is missing.
7. Gemini cites evidence numbers, and the backend replaces them with verified document/page labels.
8. The API separately returns the retrieved source metadata for the frontend source badges.

## Test questions

- Can I return a blender after 14 days?
- What proof do I need for a return?
- How long does delivery take in Kigali?
- How do I claim a warranty?
- Which payment methods are accepted?
- How should I clean the SmartBlend 500?
- What should I do before using the CoolHome 200 refrigerator?
- What is the store's policy about something not covered by the documents?

The final question is useful for checking that the chatbot says it does not know instead of inventing an answer.

## Updating documents

1. Put new `.pdf` or `.txt` files inside `rag-based-chatbot/data/`.
2. Remove old or duplicate files.
3. Activate the backend virtual environment.
4. Run `python ingest.py` again.
5. Test representative customer questions and verify the cited pages.

## Security and quality notes

- The Gemini key belongs only in the backend `.env` file.
- Never place an API key in frontend JavaScript or GitHub.
- The free Gemini tier is suitable for fictional training data, not confidential business documents.
- Source citations improve traceability but do not guarantee correctness.
- Important warranty, payment, or legal decisions should still receive human review.
- Before production, add authentication, access control, monitoring, rate limiting, automated tests, and a production database strategy.

## Troubleshooting

### `GEMINI_API_KEY is missing`

Add the key to `rag-based-chatbot/.env`, not `frontend/.env`.

### `The document index is empty`

Activate the virtual environment and run `python ingest.py`.

### The frontend says `API offline`

Start FastAPI on port `8000` and confirm <http://127.0.0.1:8000/health> opens.

### The browser reports a CORS error

Confirm the frontend uses port `5174` and both `http://127.0.0.1:5174` and `http://localhost:5174` are allowed in `CORS_ORIGINS`.

### The embedding model changes

Rebuild the Chroma collection by running `python ingest.py`. Embeddings from different models or dimensions must not be mixed.
