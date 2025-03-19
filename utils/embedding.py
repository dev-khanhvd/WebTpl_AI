import json
import uuid
import re
from sentence_transformers import SentenceTransformer

from vector_db.chroma_db import ChromaDB
from llama_cpp import Llama
from bs4 import BeautifulSoup

class Embedding:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.data_json = "./data/data_training.json"
        chroma_db = ChromaDB(self.base_dir)
        self.collection = chroma_db.chroma_collection()
        self.types = [
            'home_banner_main_block'
        ]
    def save_embeddings(self):
        with open(self.data_json, "r", encoding="utf-8") as file:
            training_data = json.load(file)

        if self.collection.count() == 0:
            questions = []
            embeddings = []
            metadata_list = []
            ids = []

            for i, item in enumerate(training_data):
                question = item["question"]
                embedding = self.model.encode(item["question"])
                if embedding is None:
                    print(f"🚨 Lỗi: Không thể tạo embedding cho câu hỏi: {question}")
                    continue

                metadata = {
                    "answer": item["answer"]
                }
                if "logic" in item and item["logic"]:
                    metadata["logic"] = json.dumps(item["logic"])

                if "example" in item and item["example"]:
                    metadata["example"] = item["example"]

                questions.append(question)
                embeddings.append(embedding.tolist())
                metadata_list.append(metadata)
                ids.append(str(uuid.uuid4()))

                if questions:
                    self.collection.add(
                        documents=questions,
                        embeddings=embeddings,
                        metadatas=metadata_list,
                        ids=ids
                    )
                    print(f"✅ Đã thêm {len(questions)} câu hỏi vào cơ sở dữ liệu.")
                else:
                    print("⚠️ Không có câu hỏi nào được thêm vào.")
            else:
                # Normal processing for adding new items
                for i, item in enumerate(training_data):
                    question = item["question"]
                    if self.is_question_exist(question):
                        print(f"🔍 Câu hỏi đã tồn tại: {question}")
                        continue

                    embedding = self.model.encode(item["question"])
                    if embedding is None:
                        print(f"🚨 Lỗi: Không thể tạo embedding cho câu hỏi: {question}")
                        continue

                    metadata = {
                        "answer": item["answer"]
                    }
                    if "logic" in item and item["logic"]:
                        metadata["logic"] = json.dumps(item["logic"])

                    if "example" in item and item["example"]:
                        metadata["example"] = item["example"]

                    self.collection.add(
                        documents=[question],
                        embeddings=[embedding.tolist()],
                        metadatas=[metadata],
                        ids=[f"id_{len(self.collection.get()['ids']) + i}"]
                    )

    def load_training_data(self):
        with open(self.data_json, "r", encoding="utf-8") as file:
            return json.load(file)

    def delete_embeddings(self, ids):
        self.collection.delete(
            ids=ids)  # Xóa tất cả
        print("✅ Đã xóa toàn bộ dữ liệu trong ChromaDB.")

    def get_embeddings(self):
        all_items = self.collection.get()
        return json.dumps(all_items, indent=2)

    def process_question(self, user_question, type, items = None):
        print(f"🔍 Đang xử lý câu hỏi: {user_question}")
        best_match = self.get_answer_with_details(user_question)
        pattern = r"```(?:twig)?\n([\s\S]*?)```"
        if best_match:
            print(f"✅ Đã tìm thấy câu trả lời phù hợp: {best_match['question']}")
            generated_code = self.generate_code_with_llama(best_match,type ,items)
            if type == 'home_banner_main_block':
                content = re.search(pattern, generated_code[type])
                if content:
                    return content.group(1)
                return None

        else:
            print("❌ Không tìm thấy câu trả lời phù hợp.")
            return {
                "success": False,
                "message": "Không tìm thấy câu trả lời phù hợp."
            }

    def generate_code_with_llama(self, best_match, type, items = None):
        model_path = "C:\\Users\\phogu\\AppData\\Local\\nomic.ai\\GPT4All\\mistral_7b_0-3_oh-dcft-v3.1-claude-3-5-sonnet-20241022-Q4_0.gguf"
        llm = Llama(
            model_path=model_path,
            n_ctx=4096,  # Context size
            n_gpu_layers=32)

        if not best_match:
                return "🚫 Không tìm thấy logic phù hợp."

        prompt = f"""Dựa trên thông tin sau, hãy tạo mã Twig để hiển thị banner:
                    - Logic: {best_match['logic']}
                    - Example: {best_match['example']}
                   Use twig to loop {items} with the logic code above, no code description.
                    """

        print("Đang xử lý, vui lòng chờ trong giây lát!")

        response = llm(prompt, max_tokens=1000)

        return {type : response["choices"][0]["text"]}

    def is_question_exist(self, question):
        if self.collection.count() == 0:
            return False

        # Check if question exists
        results = self.collection.query(
            query_texts=[question],
            n_results=min(1, self.collection.count())
        )

        if not results["documents"] or not results["documents"][0]:
            return False

        return results["documents"][0][0] == question

    def get_answer_with_details(self, question):
        if self.collection.count() == 0:
            return None

        results = self.collection.query(
            query_texts=[question],
            n_results=1
        )

        if not results["documents"] or not results["documents"][0]:
            return None

        metadata = results["metadatas"][0][0]
        answer_data = {
            "question": results["documents"][0][0],
            "answer": metadata["answer"]
        }

        # Parse logic field if available
        if "logic" in metadata:
            answer_data["logic"] = json.loads(metadata["logic"])
        else:
            answer_data["logic"] = []

        # Add example if available
        if "example" in metadata:
            answer_data["example"] = metadata["example"]
        else:
            answer_data["example"] = ""

        return answer_data