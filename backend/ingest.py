import os
import chromadb
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

load_dotenv()

TOPICS_DIR = "../data/topics"
CHROMA_PATH = "../chroma_db"

def ingest_documents():
    print("Starting ingestion...")

    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Settings.embed_model = embed_model
    Settings.llm = None

    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection("git_topics")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    topics_path = Path(TOPICS_DIR)
    if not topics_path.exists():
        print(f"Error: {TOPICS_DIR} folder not found")
        return

    txt_files = list(topics_path.glob("*.txt"))
    if not txt_files:
        print("Error: No .txt files found in data/topics/")
        return

    print(f"Found {len(txt_files)} topic files:")
    for f in txt_files:
        print(f"  - {f.name}")

    documents = SimpleDirectoryReader(TOPICS_DIR).load_data()
    print(f"Loaded {len(documents)} document chunks")

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )

    print("Ingestion complete. ChromaDB stored at ../chroma_db")
    return index

if __name__ == "__main__":
    ingest_documents()