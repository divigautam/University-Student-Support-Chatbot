"""Shared test fixtures for the ChatBot test suite."""
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# ---------- Test database setup ----------

TEST_DB_URL = "sqlite+aiosqlite:///./test_chatbot.db"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


# ---------- DB override ----------

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


# ---------- Session-scoped fixtures ----------

@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables once at the start, drop them at the end."""
    from database import Base
    # Import models so Base.metadata knows about all tables
    import models  # noqa: F401

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


# ---------- Per-test cleanup ----------

@pytest_asyncio.fixture(autouse=True)
async def cleanup_tables():
    """Truncate all tables between tests to ensure isolation."""
    yield
    async with TestingSessionLocal() as session:
        for table in ["feedback", "messages", "conversations", "documents",
                       "analytics_events", "users"]:
            await session.execute(
                __import__("sqlalchemy").text(f"DELETE FROM {table}")
            )
            await session.commit()


# ---------- Mock external services ----------

@pytest.fixture(autouse=True)
def mock_openai_chat():
    """Mock the OpenAI client used in routers/chat.py."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is a test AI response."

    with patch("routers.chat.client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        yield mock_client


@pytest.fixture(autouse=True)
def mock_rag_retrieve():
    """Mock the RAG retriever so no ChromaDB or OpenAI embeddings are needed."""
    with patch("routers.chat.retrieve") as mock_ret:
        mock_ret.return_value = [
            {
                "text": "Academic calendar info: exams start Jan 15.",
                "source": "Academic Calender Session-2026-27.pdf",
                "page": 1,
                "score": 0.92,
            }
        ]
        yield mock_ret


@pytest.fixture(autouse=True)
def mock_chroma_ingest():
    """Mock the RAG ingest/delete functions used in admin routes."""
    with patch("routers.admin.ingest_document", return_value=5) as m_ingest, \
         patch("routers.admin.remove_from_chroma") as m_delete:
        yield m_ingest, m_delete


@pytest.fixture(autouse=True)
def mock_chroma_stats():
    """Mock ChromaDB stats used in analytics."""
    with patch("routers.analytics.get_collection_stats",
               return_value={"total_chunks": 42, "total_documents": 1}):
        yield


# ---------- Client fixture ----------

@pytest_asyncio.fixture
async def client():
    """Async HTTP client that talks to the FastAPI app with test overrides."""
    from database import get_db
    from main import app

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()


# ---------- Auth helper fixtures ----------

@pytest_asyncio.fixture
async def auth_headers(client):
    """Register a student user and return auth headers."""
    reg_resp = await client.post("/auth/register", json={
        "username": "teststudent",
        "email": "teststudent@abes.ac.in",
        "password": "testpass123",
    })
    assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
    token = reg_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(client):
    """Create an admin user directly in DB and return auth headers."""
    from models import User
    from auth import hash_password

    async with TestingSessionLocal() as session:
        admin = User(
            username="testadmin",
            email="testadmin@abes.ac.in",
            hashed_password=hash_password("adminpass123"),
            role="admin",
        )
        session.add(admin)
        await session.commit()

    login_resp = await client.post("/auth/login", json={
        "email": "testadmin@abes.ac.in",
        "password": "adminpass123",
    })
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
