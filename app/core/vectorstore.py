import os
import chromadb
from chromadb.utils import embedding_functions

SCHEMES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "schemes")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")
COLLECTION_NAME = "government_schemes"

_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embedding_fn,
    )
    return collection

def ingest_schemes():
    collection = get_collection()

    files = [f for f in os.listdir(SCHEMES_DIR) if f.endswith(".txt")]
    documents, metadatas, ids = [], [], []

    for filename in files:
        filepath = os.path.join(SCHEMES_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        documents.append(text)
        metadatas.append({"source": filename})
        ids.append(filename)

    # upsert = safe to re-run without creating duplicates
    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
    print(f"Ingested {len(documents)} scheme documents into Chroma.")
    return len(documents)

def retrieve_schemes(query_text, n_results=5):
    collection = get_collection()
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
    )

    candidates = []
    for doc_id, document, distance in zip(
        results["ids"][0], results["documents"][0], results["distances"][0]
    ):
        candidates.append({
            "source": doc_id,
            "content": document,
            "distance": distance,
        })
    return candidates

def get_scheme_document(scheme_name: str):
    """
    Exact lookup by scheme_name (filename without .txt), no embedding search needed.
    Returns the document text, or None if not found.
    """
    collection = get_collection()
    doc_id = f"{scheme_name}.txt"
    result = collection.get(ids=[doc_id])

    if not result["documents"]:
        return None
    return result["documents"][0]

if __name__ == "__main__":
    ingest_schemes()


