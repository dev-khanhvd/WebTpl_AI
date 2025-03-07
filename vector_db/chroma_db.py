import chromadb
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE
client = OpenAI(
    api_key = OPENAI_API_KEY,
)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")

def add_document(text, doc_id):
    embedding = client.embeddings.create(
        model="text-embedding-ada-002", input=text
    ).data[0].embedding

    collection.add(ids=[doc_id], embeddings=[embedding], metadatas=[{"text": text}])

def search_documents(query):
    query_embedding = client.embeddings.create(
        model="text-embedding-ada-002", input=query
    ).data[0].embedding

    results = collection.query(query_embeddings=[query_embedding], n_results=2)
    return results["metadatas"]