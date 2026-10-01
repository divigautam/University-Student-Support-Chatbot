# 🎓 ChatBot - University Student Support

![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-00a393.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5.6--luna-412991.svg)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6B6B.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Overview

**ChatBot** is an AI-powered, production-quality student support system for **ABES Engineering College, Ghaziabad**. It is designed to assist students with queries regarding academics, schedules, college policies, and general campus life. By leveraging an advanced Retrieval-Augmented Generation (RAG) pipeline on official college documents, it provides highly accurate and context-aware responses.

## Features

- **Context-Aware AI Chat:** Powered by OpenAI's `gpt-5.6-luna` model combined with a robust RAG pipeline using ChromaDB.
- **Role-Based Access Control (RBAC):** Distinct roles for Students and Administrators.
- **Secure Authentication:** JWT-based authentication with bcrypt password hashing. Domain-restricted student registration (`@abes.ac.in`).
- **Admin Dashboard:** Comprehensive admin panel for document management, ingestion, and chatbot analytics.
- **Feedback Loop:** Users can rate responses (1-5), helping admins track and improve quality.
- **Modern Backend:** Built on FastAPI with asynchronous SQLAlchemy (aiosqlite).
- **Responsive Frontend:** Vanilla HTML/CSS/JS frontend served directly from the backend.

## Architecture

The system uses a Retrieval-Augmented Generation (RAG) architecture to ground the AI's responses in factual, college-specific documents.

```mermaid
graph TD
    %% User Flow
    User([Student User]) -->|Ask Question| WebUI[Frontend UI<br/>HTML/CSS/JS]
    WebUI -->|POST /chat| API[FastAPI Backend]
    
    %% Admin Flow
    Admin([Administrator]) -->|Upload PDF| AdminUI[Admin Dashboard]
    AdminUI -->|POST /admin/documents| API
    
    %% Backend Services
    API <--> Auth[JWT & RBAC]
    API <--> DB[(SQLite DB<br/>SQLAlchemy Async)]
    
    %% RAG Pipeline
    API --> RAG[RAG Pipeline]
    
    %% Ingestion Flow
    RAG -->|1. Extract Text| PyMuPDF(PyMuPDF)
    PyMuPDF -->|2. Chunk (1000/200)| Chunker(Chunker)
    Chunker -->|3. Embed| Embedding[OpenAI text-embedding-3-small]
    Embedding -->|4. Store| Chroma[(ChromaDB Vector Store)]
    
    %% Query Flow
    RAG -->|A. Embed Query| Embedding
    Embedding -->|B. Vector Search| Chroma
    Chroma -->|C. Retrieve Context| RAG
    RAG -->|D. Generate Response| LLM[OpenAI GPT-5.6-luna]
    LLM --> API
    API --> WebUI
```

## Project Structure

```text
ChatBot/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Pydantic settings
│   ├── database.py          # SQLAlchemy async setup
│   ├── models.py            # DB models (User, Conversation, Message, etc.)
│   ├── auth.py              # JWT + bcrypt auth utilities
│   ├── seed_admin.py        # CLI admin creation script
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   ├── rag/                 # RAG pipeline
│   │   ├── pdf_processor.py # PDF text extraction
│   │   ├── chunker.py       # Document chunking
│   │   ├── embeddings.py    # OpenAI embeddings
│   │   └── retriever.py     # ChromaDB vector search
│   ├── routers/             # API routes
│   │   ├── auth_routes.py   # /auth/* endpoints
│   │   ├── chat.py          # /chat, /conversations
│   │   ├── admin.py         # /admin/* endpoints
│   │   ├── feedback.py      # /feedback endpoints
│   │   └── analytics.py     # /analytics/dashboard
│   ├── middleware/
│   │   └── logging_middleware.py
│   ├── static/              # Frontend
│   │   ├── index.html       # Chat UI
│   │   ├── login.html       # Login/Register
│   │   ├── admin.html       # Admin dashboard
│   │   ├── css/style.css
│   │   └── js/              # api.js, app.js, auth.js, admin.js
│   └── tests/               # Pytest test suite
├── data/
│   └── documents/           # PDF storage
└── README.md
```

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | None | Health check |
| `POST` | `/auth/register` | None | Student registration (requires `@abes.ac.in`) |
| `POST` | `/auth/login` | None | Login, returns JWT |
| `GET` | `/auth/me` | Bearer | Get current user info |
| `POST` | `/chat` | Bearer | Send message, get AI response with document sources |
| `GET` | `/conversations` | Bearer | List current user's conversations |
| `GET` | `/conversations/{id}/messages`| Bearer | Get specific conversation messages |
| `DELETE`| `/conversations/{id}` | Bearer | Delete a conversation |
| `POST` | `/feedback` | Bearer | Submit feedback rating (1-5) for a response |
| `GET` | `/feedback/stats` | Admin | Overall feedback statistics |
| `POST` | `/admin/documents/upload` | Admin | Upload a new PDF for ingestion |
| `GET` | `/admin/documents` | Admin | List ingested documents |
| `DELETE`| `/admin/documents/{id}` | Admin | Delete document & vectors |
| `POST` | `/admin/documents/{id}/reindex`| Admin | Re-run RAG pipeline for document |
| `GET` | `/analytics/dashboard` | Admin | General dashboard usage data |

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd ChatBot
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Copy the example config and add your keys:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in `OPENAI_API_KEY` and `JWT_SECRET_KEY`.

5. **Seed the Admin User:**
   ```bash
   python seed_admin.py --username admin --email admin@abes.ac.in --password <secure_password>
   ```

6. **Run the Application:**
   Start the FastAPI development server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

7. **Access the App:**
   - **Chat UI:** http://localhost:8000
   - **Login:** http://localhost:8000/login.html
   - **API Docs (Swagger):** http://localhost:8000/docs

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Required. Your OpenAI API Key | - |
| `JWT_SECRET_KEY` | Required. Secret for signing JWT tokens | - |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRATION_MINUTES`| Token lifespan in minutes | `1440` (24h) |
| `EMBEDDING_MODEL`| Model for document embeddings | `text-embedding-3-small` |
| `CHAT_MODEL` | Main generation model | `gpt-5.6-luna` |
| `CHUNK_SIZE` | Characters per document chunk | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |
| `CHROMA_DB_PATH` | Local path for vector database | `./chroma_db` |
| `DATABASE_URL` | SQLite connection string | `sqlite+aiosqlite:///./chatbot.db`|
| `DOCUMENTS_PATH` | Directory for PDF storage | `../data/documents` |

## Testing

The project uses `pytest` for unit and integration testing.

To run the test suite:
```bash
# Ensure you are in the backend/ directory
pytest tests/ -v
```

## Deployment Tips

- **Reverse Proxy:** Use Nginx or Caddy to reverse proxy to the application and handle SSL termination.
- **Production Server:** Use `gunicorn` with `uvicorn` workers instead of standard `uvicorn` for production traffic:
  ```bash
  gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
  ```
- **Vector DB:** For a high-traffic production setup, consider deploying ChromaDB as a separate standalone service rather than the embedded local instance.
- **Relational DB:** While SQLite is excellent, consider migrating to PostgreSQL for heavy concurrent writes, updating `DATABASE_URL` accordingly.
