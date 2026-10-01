import re

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    # Simplified recursive character splitting
    chunks = []
    
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    paragraphs = re.split(r'\n\s*\n', text)
    current_chunk = ""

    for p in paragraphs:
        if len(current_chunk) + len(p) <= chunk_size:
            current_chunk += p + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
                # overlap logic simplified
                current_chunk = current_chunk[-chunk_overlap:] + p + "\n\n" if chunk_overlap > 0 else p + "\n\n"
            else:
                # If paragraph itself is larger than chunk_size, split by sentences
                sentences = re.split(r'(?<=[.!?])\s+', p)
                for s in sentences:
                    if len(current_chunk) + len(s) <= chunk_size:
                        current_chunk += s + " "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = current_chunk[-chunk_overlap:] + s + " " if chunk_overlap > 0 else s + " "
                        else:
                            # Split by words
                            words = s.split()
                            for w in words:
                                if len(current_chunk) + len(w) <= chunk_size:
                                    current_chunk += w + " "
                                else:
                                    if current_chunk:
                                        chunks.append(current_chunk.strip())
                                    current_chunk = w + " "

    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

def chunk_document(pages: list[dict], filename: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    document_chunks = []
    chunk_index = 0
    
    for page in pages:
        text = page["text"]
        page_num = page["page_number"]
        chunks = chunk_text(text, chunk_size, chunk_overlap)
        
        for c in chunks:
            if not c.strip():
                continue
            document_chunks.append({
                "text": c,
                "metadata": {
                    "source": filename,
                    "page": page_num,
                    "chunk_index": chunk_index
                }
            })
            chunk_index += 1
            
    return document_chunks
