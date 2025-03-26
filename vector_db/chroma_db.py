import chromadb

class ChromaDB:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="data_training")
