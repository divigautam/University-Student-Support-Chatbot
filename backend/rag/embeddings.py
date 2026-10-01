import time
from openai import OpenAI
from config import get_settings

settings = get_settings()
client = OpenAI(base_url="http://localhost:11434/v1/", api_key="ollama")

def get_embedding(text: str, model: str = None) -> list[float]:
    model = model or "nomic-embed-text"
    retries = 3
    for attempt in range(retries):
        try:
            response = client.embeddings.create(input=[text], model=model)
            return response.data[0].embedding
        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(2 ** attempt)

def get_embeddings_batch(texts: list[str], model: str = None) -> list[list[float]]:
    model = model or "nomic-embed-text"
    retries = 3
    for attempt in range(retries):
        try:
            response = client.embeddings.create(input=texts, model=model)
            return [data.embedding for data in response.data]
        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(2 ** attempt)
