from rag.document_loader import load_documents


def chunk_text(text, chunk_size=300, overlap=50):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]
        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


documents = load_documents()

for document in documents:
    chunks = chunk_text(document["content"])

    print(f"\nDocument: {document['filename']}")
    print(f"Number of chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i + 1} ---")
        print(chunk)