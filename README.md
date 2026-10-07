# Kigali HomeTech RAG Chatbot

Kigali HomeTech RAG Chatbot is a customer-support demonstration project. It answers questions about returns, warranty, delivery, payments, and product use by searching approved company documents first. It does not answer from general knowledge alone: each answer is grounded in retrieved document pages and shown with its sources.

## Presentation summary

**Problem:** Customers need quick, consistent answers, but policies and manuals are spread across several files.

**Solution:** This project turns approved PDF and TXT documents into a searchable knowledge base. When a customer asks a question, the backend finds the most relevant document pages, gives them to Gemini as evidence, and returns a concise answer with source pages.

**Key value:** The assistant can explain *where* an answer came from and says it does not know when the documents do not contain the answer.

```text
Approved documents
      ↓
Text extraction and chunking
      ↓
Gemini embeddings (768 numbers per chunk)
      ↓
ChromaDB vector database
      ↓
Customer question → relevant evidence → grounded Gemini answer + page sources
```

## What the project demonstrates

- Retrieval-Augmented Generation (RAG) using real business documents.
- Semantic search: it finds similar meanings, not only exact keywords.
- Evidence-based answers with document names and page numbers.
- A transparent view of the retrieval and answer process.
- Safe PDF upload and automatic re-indexing.
- A Docker setup that runs the backend and web interface together.

## Technology used

| Area | Technology | Role in the project |
| --- | --- | --- |
| API backend | Python + FastAPI | Receives questions, indexes documents, and returns answers. |
| PDF reading | pypdf | Extracts text while preserving page numbers. |
| Embeddings | Gemini `gemini-embedding-2` | Changes text into numeric meaning vectors. |
| Vector size | 768 dimensions | A practical balance of search quality, speed, and storage. |
| Vector database | ChromaDB | Stores vectors and finds the closest document chunks. |
| Answer model | Gemini `gemini-3.5-flash-lite` | Writes the final answer from the retrieved evidence. |
| Web interface | React + Vite | Lets users ask questions, upload PDFs, and inspect sources. |
| Containers | Docker Compose | Starts the backend and frontend with one command. |

## Backend process — step by step

This is the most important part of the project to explain in a presentation.

### A. Building the knowledge index

The index is built when the user clicks **Rebuild document index**, uploads a new PDF, or runs the ingestion script.

1. **Read approved documents** — The backend reads every `.pdf` and `.txt` file in `rag-based-chatbot/data/`.
2. **Extract text by page** — PDF text is extracted page by page, so the final answer can name the correct page.
3. **Split text into chunks** — Long pages are divided into small, overlapping pieces. The default chunk size is 350 units with an overlap of 60, helping the system preserve meaning at chunk boundaries.
4. **Create embeddings** — Gemini converts each chunk into a vector of 768 numbers. These numbers represent the meaning of the text.
5. **Store in ChromaDB** — ChromaDB saves the vector, original chunk text, document name, file path, page number, and chunk number.

```text
PDF / TXT file → page text → overlapping chunks → 768-number embeddings → ChromaDB
```

### B. Answering a customer question

For example, a customer asks: **“Can I return a blender after 14 days?”**

1. **Receive and validate the question** — FastAPI accepts a question between 2 and 1,000 characters.
2. **Embed the question** — Gemini changes the question into another 768-number vector.
3. **Search by meaning** — ChromaDB compares the question vector with stored document vectors using cosine similarity.
4. **Select evidence** — The backend retrieves candidates, removes duplicate document pages, and keeps the best four unique pages.
5. **Build a controlled prompt** — The question and numbered evidence excerpts are sent to Gemini with rules: use only the evidence, do not invent information, and say “I do not know from the available business documents” if evidence is missing.
6. **Generate and check the answer** — Gemini answers with evidence references. The backend verifies that each reference is one of the retrieved sources.
7. **Return answer and trace** — The API sends the clean answer, source metadata, and a safe trace for the Transparency panel.

```text
Customer question → question embedding → ChromaDB search
                  → best document pages → controlled Gemini prompt
                  → verified answer + page sources
```

### Why 768 dimensions?

An embedding is a list of numbers representing meaning. `768` means every chunk and question becomes a list of 768 numbers. It provides good semantic-search quality without making this small learning project unnecessarily slow or large. All vectors in one ChromaDB collection must use the same size, so changing `EMBEDDING_DIMENSIONS` requires rebuilding the index.

## Frontend overview

The frontend is intentionally simple. It provides:

- A chat box for customer questions.
- Suggested example questions.
- Source badges showing the supporting document and page.
- A **Transparency** panel that shows the question, embedding preview, search details, selected evidence, prompt summary, and answer verification.
- Buttons to rebuild the knowledge index or upload a text-readable PDF.

The backend remains responsible for document processing, retrieval, validation, and Gemini calls. The frontend only presents the results clearly.

## Project structure

```text
kigali-hometech-rag/
├── docker-compose.yml               # Starts backend and frontend together
├── rag-based-chatbot/
│   ├── Dockerfile                   # Backend container instructions
│   ├── app/
│   │   ├── config.py                # Environment settings
│   │   ├── documents.py             # Read files and split text into chunks
│   │   ├── embeddings.py            # Gemini embedding calls
│   │   ├── indexer.py               # Builds the knowledge index
│   │   ├── store.py                 # ChromaDB storage and search
│   │   ├── rag.py                   # Retrieval, prompting, and citation checks
│   │   └── main.py                  # FastAPI routes
│   ├── data/                        # Approved PDFs and TXT documents
│   ├── ingest.py                    # Command-line indexing entry point
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile                   # Frontend container instructions
│   └── src/                         # React interface
├── TEST_QUESTIONS.md                # Manual test checklist
└── README.md
```

## Run the project with Docker

### 1. Create your private environment file

```bash
cp rag-based-chatbot/.env.example rag-based-chatbot/.env
```

Open `rag-based-chatbot/.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Keep this file private. It is ignored by Git and must not be shared or uploaded.

### 2. Start the application

```bash
docker compose up --build
```

Open these addresses in a browser:

| Address | Purpose |
| --- | --- |
| <http://localhost:5174> | Chatbot web interface |
| <http://localhost:8000/health> | Backend status check |
| <http://localhost:8000/docs> | Interactive FastAPI documentation |

`http://localhost:8000/` returning **Not Found** is normal; the backend has no homepage route.

### 3. Build the index

On first use, open the web interface and click **Rebuild document index**. The system will process the documents and store the vectors in the Docker ChromaDB volume.

To stop the application, press `Ctrl + C`. To run it in the background:

```bash
docker compose up -d
```

To remove containers and the saved vector index, then start fresh:

```bash
docker compose down -v
```

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Shows backend status, model names, document count, and indexed chunks. |
| `POST` | `/ingest` | Rebuilds the index from all approved documents. |
| `POST` | `/documents/upload` | Validates, saves, and indexes one PDF up to 10 MB. |
| `POST` | `/chat` | Answers a customer question with sources and a transparency trace. |

Example request:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Can I return a blender after 14 days?"}'
```

## Test the demonstration

Use the questions in [TEST_QUESTIONS.md](TEST_QUESTIONS.md). Good presentation examples include:

- “Can I return a blender after 14 days?”
- “How long does delivery take in Kigali?”
- “How do I claim a warranty?”
- “How should I clean the SmartBlend 500?”
- “Does the store sell laptops?” — this should produce the safe unknown-answer message if no document supports it.

For each test, confirm that the answer is clear, the source badges match the relevant document pages, and the Transparency panel shows the real backend process.

## Adding documents

Use either option:

1. In the interface, select **Add a new PDF**. The backend accepts text-readable PDFs up to 10 MB and rebuilds the index automatically.
2. Put a `.pdf` or `.txt` file in `rag-based-chatbot/data/`, then rebuild the index from the interface or call `POST /ingest`.

Scanned PDFs without extractable text need OCR before upload. Duplicate filenames, empty files, invalid PDFs, and PDFs larger than 10 MB are rejected.

## Important notes

- Never place `GEMINI_API_KEY` in frontend code or GitHub.
- The assistant is designed for approved training documents, not confidential production data.
- Sources make answers traceable, but important business, legal, warranty, or payment decisions should still be reviewed by a person.
- Before production use, add authentication, access control, rate limiting, monitoring, automated tests, and a production data strategy.
