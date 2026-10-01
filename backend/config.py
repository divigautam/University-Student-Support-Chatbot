from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION_MINUTES: int = 1440
    EMBEDDING_MODEL: str = 'text-embedding-3-small'
    CHAT_MODEL: str = 'gpt-5.6-luna'
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    CHROMA_DB_PATH: str = './chroma_db'
    DATABASE_URL: str = 'sqlite+aiosqlite:///./chatbot.db'
    DOCUMENTS_PATH: str = '../data/documents'

    model_config = {'env_file': '.env'}

@lru_cache()
def get_settings():
    return Settings()
