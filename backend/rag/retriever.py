import chromadb
from chromadb.config import Settings as ChromaSettings
from config import get_settings
from rag.pdf_processor import extract_text_from_pdf
from rag.chunker import chunk_document
from rag.embeddings import get_embeddings_batch, get_embedding

settings = get_settings()

client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
collection = client.get_or_create_collection(name='university_documents')

def ingest_document(file_path: str, doc_id: int) -> int:
    filename = file_path.split("/")[-1].split("\\")[-1]
    pages = extract_text_from_pdf(file_path)
    chunks = chunk_document(pages, filename, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    
    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    metadatas = []
    ids = []
    
    for i, c in enumerate(chunks):
        meta = c["metadata"]
        meta["doc_id"] = doc_id
        metadatas.append(meta)
        ids.append(f"doc_{doc_id}_chunk_{i}")

    # Batch embed
    embeddings = get_embeddings_batch(texts)
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=texts
    )
    
    return len(chunks)

def retrieve(query: str, top_k: int = 5) -> list[dict]:
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    retrieved = []
    if results["documents"] and len(results["documents"]) > 0:
        for i in range(len(results["documents"][0])):
            retrieved.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "page": results["metadatas"][0][i]["page"],
                "score": results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
            })
    return retrieved

def delete_document(doc_id: int):
    collection.delete(
        where={"doc_id": doc_id}
    )

def get_collection_stats() -> dict:
    count = collection.count()
    return {
        "total_chunks": count,
        "total_documents": len(set(meta["doc_id"] for meta in collection.get(include=["metadatas"])["metadatas"])) if count > 0 else 0
    }
