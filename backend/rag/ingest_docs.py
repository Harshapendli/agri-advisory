import asyncio
import os
import glob

async def ingest():
    from rag.embeddings import EmbeddingModel
    from rag.qdrant_client import QdrantManager

    docs_dir = os.path.join(os.path.dirname(__file__), "../docs")
    files = glob.glob(os.path.join(docs_dir, "*.txt")) + glob.glob(os.path.join(docs_dir, "*.pdf"))

    if not files:
        print(f"No documents found in {docs_dir}")
        print("Add .txt or .pdf agricultural documents there first.")
        print("A sample file (sample_advisory_docs.txt) is included by default.")
        return

    print(f"Found {len(files)} document(s)")
    all_chunks = []

    for path in files:
        if path.endswith(".pdf"):
            try:
                from pypdf import PdfReader
                reader = PdfReader(path)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception as e:
                print(f"Skipping {path}: {e}")
                continue
        else:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

        chunk_size, overlap = 512, 50
        words = text.split()
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                all_chunks.append({"text": chunk, "source": os.path.basename(path), "chunk_index": len(all_chunks)})

    print(f"Created {len(all_chunks)} chunks")

    embedding_model = EmbeddingModel()
    texts = [c["text"] for c in all_chunks]
    print("Generating embeddings...")
    embeddings = embedding_model.encode_batch(texts)

    qdrant = QdrantManager()
    await qdrant.ensure_collection()
    count = await qdrant.upsert_documents(all_chunks, embeddings)
    print(f"\nIngested {count} chunks into Qdrant collection 'agri_knowledge'")
    print("Knowledge base ready for GraphRAG!")

if __name__ == "__main__":
    asyncio.run(ingest())
