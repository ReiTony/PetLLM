from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings 
import chromadb
import os
print("USING CHROMADB VERSION:", chromadb.__version__)
print("CHROMADB MODULE PATH:", chromadb.__file__)

persist_path = os.path.abspath("./petpal_chromadb")

embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

collection = Chroma(
    persist_directory=persist_path,
    embedding_function=embedding_function,
    collection_name="pet_memories"
)

def add_to_vector_store(user_id: str, pet_id: str, text: str, doc_id: str):
    collection.add_texts(
        texts=[text],
        ids=[doc_id],
        metadatas=[{"user_id": user_id, "pet_id": pet_id}]
    )

def query_similar_memories(user_id: str, pet_id: str, query: str, top_k=3) -> list:
    results = collection.similarity_search(
        query=query,
        k=top_k,
        filter={
            "user_id": user_id,
            "pet_id": pet_id
        }
    )
    return [doc.page_content for doc in results] if results else []
