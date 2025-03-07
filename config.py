import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FOLDER_STRUCTURE = os.getenv("FOLDER_STRUCTURE")
BASE_DIR = os.getenv("BASE_DIR")
CONTENT_TEMPLATE_JSON = os.getenv("CONTENT_TEMPLATE_JSON")
VECTOR_DB_PATH = "./vector_db/chroma_db"

MODEL_NAME = "DeepSeek-R1-Distill-Qwen-7B"
TEMPERATURE = 0.28
MAX_TOKEN = 100
API_URL = "http://localhost:4891/v1/chat/completions"