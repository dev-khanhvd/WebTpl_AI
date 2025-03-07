from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

def get_retriever():
    vector_store = Chroma(persist_directory="./vector_db/chroma_db", embedding_function=OpenAIEmbeddings())
    return vector_store.as_retriever()