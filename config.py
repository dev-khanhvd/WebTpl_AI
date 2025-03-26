import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FOLDER_STRUCTURE = os.getenv("FOLDER_STRUCTURE")
BASE_DIR = os.getenv("BASE_DIR")
CONTENT_TEMPLATE_JSON = os.getenv("CONTENT_TEMPLATE_JSON")

TEMPLATE_JSON = os.getenv("TEMPLATE_JSON")
PAGE_TYPE_MAPPING = os.getenv("PAGE_TYPE_MAPPING")

VECTOR_DB_PATH = "./vector_db/chroma_db"

MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0
MAX_TOKEN = 500