from sentence_transformers import SentenceTransformer
import faiss

from rag.document_loader import load_documents
from rag.chunker import chunk_text


# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Load documents
documents = load_documents()

all_chunks = []

for document in documents:
    chunks = chunk_text(document["content"])

    for chunk in chunks:
        all_chunks.append({
            "filename": document["filename"],
            "content": chunk
        })


# Create embeddings
texts = [chunk["content"] for chunk in all_chunks]

embeddings = model.encode(texts)

print(f"Created {len(embeddings)} embeddings.")


# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

print(f"FAISS index contains {index.ntotal} vectors.")



def search_documents(query, k=3):
    """Return the most relevant document chunks for a query."""
    if not all_chunks:
        return []

    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, min(k, len(all_chunks)))

    results = []

    for distance, idx in zip(distances[0], indices[0]):
        if idx < 0:
            continue

        chunk = all_chunks[idx].copy()
        chunk["distance"] = float(distance)
        results.append(chunk)

    return results
