import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.future import select

from database import init_db, AsyncSessionLocal
from config import get_settings
# Import models so Base.metadata knows about all tables
import models  # noqa: F401
from routers.auth_routes import router as auth_router
from routers.chat import router as chat_router
from routers.admin import router as admin_router
from routers.feedback import router as feedback_router
from routers.analytics import router as analytics_router
from middleware.logging_middleware import LoggingMiddleware

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and process existing PDFs on startup."""
    await init_db()
    logger.info("Database initialized successfully.")

    # Process any existing PDFs that are not already in the DB
    docs_path = settings.DOCUMENTS_PATH
    if os.path.isdir(docs_path):
        from rag.retriever import ingest_document
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(models.Document))
            existing_docs = {doc.filename for doc in result.scalars().all()}

            for filename in os.listdir(docs_path):
                if filename.lower().endswith(".pdf") and filename not in existing_docs:
                    file_path = os.path.join(docs_path, filename)
                    logger.info(f"Processing existing PDF: {filename}")
                    doc = models.Document(
                        filename=filename,
                        file_path=file_path,
                        status="processing",
                    )
                    session.add(doc)
                    await session.commit()
                    await session.refresh(doc)
                    try:
                        chunk_count = ingest_document(file_path, doc.id)
                        doc.status = "completed"
                        doc.chunk_count = chunk_count
                        await session.commit()
                        logger.info(f"Ingested {filename}: {chunk_count} chunks")
                    except Exception as e:
                        doc.status = "failed"
                        doc.error_message = str(e)
                        await session.commit()
                        logger.error(f"Failed to ingest {filename}: {e}")

    yield


app = FastAPI(
    title="ChatBot - University Student Support",
    description="AI-powered chatbot for university student support",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "project": "ChatBot"
    }


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chat_router, prefix="", tags=["chat"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(feedback_router, prefix="", tags=["feedback"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_FRONTEND_DIR = os.path.join(_BASE_DIR, "..", "frontend")
app.mount("/", StaticFiles(directory=_FRONTEND_DIR, html=True), name="static")