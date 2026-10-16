from pathlib import Path

print("GeoPulse document loader started")

DOCUMENTS_DIR = Path(__file__).parent.parent / "documents"

print("Documents folder:", DOCUMENTS_DIR)
print("Folder exists:", DOCUMENTS_DIR.exists())


def load_documents():
    documents = []

    for file_path in DOCUMENTS_DIR.glob("*.txt"):
        print("Found:", file_path.name)

        text = file_path.read_text(encoding="utf-8")

        documents.append({
            "filename": file_path.name,
            "content": text
        })

    return documents


documents = load_documents()

print(f"Loaded {len(documents)} document(s).")

for document in documents:
    print("\n---", document["filename"], "---")
    print(document["content"])