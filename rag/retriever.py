import faiss
from sentence_transformers import SentenceTransformer

from rag.document_loader import load_documents
from rag.chunker import chunk_text


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Load documents
documents = load_documents()


# Create chunks
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

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

index.add(embeddings)


def retrieve(query, top_k=3):
    """Retrieve relevant document chunks with their distances."""

    if not all_chunks:
        return []

    query_embedding = model.encode([query])
    distances, indices = index.search(
        query_embedding,
        min(top_k, len(all_chunks))
    )

    results = []

    for distance, i in zip(distances[0], indices[0]):
        if i == -1:
            continue

        if distance > 1.2:
            continue

        result = all_chunks[i].copy()
        result["distance"] = float(distance)
        results.append(result)

    return results



if __name__ == "__main__":

    query = input("Enter your question: ")

    results = retrieve(query)

    print("\nSearch Results:\n")

    for result in results:
        print("---", result["filename"], "---")
        print(result["content"])
        print()