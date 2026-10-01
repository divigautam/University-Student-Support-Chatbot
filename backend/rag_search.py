from pathlib import Path
import chromadb
import json
import math
import re
from collections import Counter


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_FOLDER = BASE_DIR / "data" / "chroma_db"
VOCABULARY_FILE = BASE_DIR / "data" / "vocabulary.json"


# ============================================================
# LOAD VOCABULARY
# ============================================================

with open(
    VOCABULARY_FILE,
    "r",
    encoding="utf-8"
) as file:

    vocabulary = json.load(file)


# ============================================================
# TOKENIZE
# ============================================================

def tokenize(text):

    return re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text.lower()
    )


# ============================================================
# CREATE QUERY EMBEDDING
# ============================================================

def create_embedding(text):

    words = tokenize(text)

    word_counts = Counter(words)

    total_words = max(len(words), 1)

    vector = []

    for word in vocabulary:

        value = word_counts[word] / total_words

        vector.append(value)

    magnitude = math.sqrt(
        sum(value * value for value in vector)
    )

    if magnitude == 0:

        return vector

    return [
        value / magnitude
        for value in vector
    ]


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=str(CHROMA_FOLDER)
)

collection = client.get_collection(
    name="university_documents"
)


# ============================================================
# ASK QUESTION
# ============================================================

question = input(
    "\n🎓 Ask your university question: "
)


# ============================================================
# CREATE QUERY VECTOR
# ============================================================

query_embedding = create_embedding(
    question
)


# ============================================================
# SEARCH
# ============================================================

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 60)

print("🔍 MOST RELEVANT INFORMATION")

print("=" * 60)


documents = results["documents"][0]

metadatas = results["metadatas"][0]

distances = results["distances"][0]


for i, document in enumerate(documents):

    print(f"\n📌 Result {i + 1}")

    print(
        f"Source: {metadatas[i]['source']}"
    )

    print(
        f"Chunk: {metadatas[i]['chunk']}"
    )

    print(
        f"Distance: {distances[i]:.4f}"
    )

    print("\nContent:")

    print(document)

    print("-" * 60)