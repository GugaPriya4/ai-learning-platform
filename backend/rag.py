import os
import chromadb
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

load_dotenv()

CHROMA_PATH = "../chroma_db"

def get_retriever():
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Settings.embed_model = embed_model
    Settings.llm = None

    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection("git_topics")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context
    )
    return index.as_retriever(similarity_top_k=3)

def retrieve_context(topic: str) -> str:
    try:
        retriever = get_retriever()
        nodes = retriever.retrieve(topic)
        if not nodes:
            return f"No content found for topic: {topic}"
        context = "\n\n".join([node.text for node in nodes])
        return context
    except Exception as e:
        return f"Error retrieving context: {str(e)}"

if __name__ == "__main__":
    result = retrieve_context("git commit")
    print("Retrieved context:")
    print(result[:500])