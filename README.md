# RAG Chat Agent — Backend

## What this does

This service lets a user upload a document and then ask questions about it in a chat interface. Instead of a generic AI answer, the assistant reads the uploaded document and answers using only what's actually in it — reducing made-up ("hallucinated") answers and giving traceable, document-grounded responses.

## Tech stack

FastAPI (API server) + sentence-transformers (embeddings) + PyTorch.

## Setup

### 1. Prerequisites

- Python 3.10+
- A Google API key (for the LLM) and a Hugging Face token (for the embedding model)

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in this folder:

```
GOOGLE_API_KEY=your_google_api_key
HF_TOKEN=your_huggingface_token
```

### 5. Run the server

```bash
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`.

## Notes

- `.env` and `venv/` are gitignored — never commit them.
- After pulling new changes, re-run `pip install -r requirements.txt` in case dependencies changed.
