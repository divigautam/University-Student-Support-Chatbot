from pathlib import Path
import chromadb
import requests


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENTS_FOLDER = BASE_DIR / "data" / "documents"
CHROMA_FOLDER = BASE_DIR / "data" / "chroma_db"


# ============================================================
# OLLAMA SETTINGS
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text"


# ============================================================
# CHUNKING
# ============================================================

def create_chunks(text, chunk_size=1000, overlap=200):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


# ============================================================
# CREATE OLLAMA EMBEDDING
# ============================================================

def create_embedding(text):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": EMBEDDING_MODEL,
            "prompt": text
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["embedding"]


# ============================================================
# FIND TEXT FILES
# ============================================================

text_files = list(
    DOCUMENTS_FOLDER.glob("*.txt")
)

if not text_files:

    print("❌ No .txt files found!")

    print(
        "Looking in:",
        DOCUMENTS_FOLDER
    )

    exit()


print(
    f"Found {len(text_files)} text document(s)"
)

print("=" * 60)


# ============================================================
# READ DOCUMENTS
# ============================================================

documents = []
metadatas = []
ids = []


for text_file in text_files:

    print(
        f"\n📄 Reading: {text_file.name}"
    )

    text = text_file.read_text(
        encoding="utf-8"
    )

    chunks = create_chunks(text)

    print(
        f"   Chunks created: {len(chunks)}"
    )

    for chunk_index, chunk in enumerate(chunks):

        documents.append(chunk)

        ids.append(
            f"{text_file.stem}_chunk_{chunk_index}"
        )

        metadatas.append({
            "source": text_file.name,
            "chunk": chunk_index
        })


if not documents:

    print("❌ No chunks created!")

    exit()


print("\n" + "=" * 60)

print(
    f"📝 Total chunks: {len(documents)}"
)


# ============================================================
# CREATE EMBEDDINGS
# ============================================================

print("\n🧠 Creating Ollama embeddings...")

embeddings = []


for index, document in enumerate(documents):

    print(
        f"   Embedding {index + 1}/{len(documents)}..."
    )

    embedding = create_embedding(
        document
    )

    embeddings.append(embedding)


print(
    f"✅ Created {len(embeddings)} embeddings"
)


# ============================================================
# CHROMADB
# ============================================================

print("\n💾 Connecting to ChromaDB...")


client = chromadb.PersistentClient(
    path=str(CHROMA_FOLDER)
)


# Delete old collection

try:

    client.delete_collection(
        name="university_documents"
    )

    print("🗑️ Old collection removed.")

except Exception:

    pass


# Create new collection

collection = client.create_collection(
    name="university_documents"
)


# ============================================================
# STORE DATA
# ============================================================

collection.add(

    ids=ids,

    documents=documents,

    embeddings=embeddings,

    metadatas=metadatas

)


# ============================================================
# RESULT
# ============================================================

print("\n" + "=" * 60)

print("🎉 OLLAMA RAG INGESTION COMPLETED!")

print("=" * 60)

print(
    f"📄 Documents: {len(text_files)}"
)

print(
    f"📝 Chunks: {len(documents)}"
)

print(
    f"🧠 Embeddings: {len(embeddings)}"
)

print(
    f"💾 ChromaDB count: {collection.count()}"
)

print(
    f"📁 Database: {CHROMA_FOLDER}"
)

print("=" * 60)