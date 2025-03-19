import chromadb

class ChromaDB:
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="data_training")

    def __init__(self, base_dir):
        self.base_dir = base_dir
    def chroma_collection(self):
        return self.collection