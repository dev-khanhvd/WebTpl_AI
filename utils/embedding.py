import json
import uuid
import re
import os
from config import MODEL_NAME, MAX_TOKEN, OPENAI_API_KEY, TEMPERATURE
from vector_db.chroma_db import ChromaDB
from openai import OpenAI
from utils.token_optimizer import TokenOptimizer

class Embedding:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data_json = "./data/data_training.json"
        self.data = "./data"
        self.client = OpenAI(
            api_key=OPENAI_API_KEY
        )
        self.model = 'text-embedding-3-small'
        # Create ChromaDB instance
        chroma_db = ChromaDB(self.base_dir)

        # Directly assign client and collection
        self.chroma_client = chroma_db.chroma_client
        self.collection = chroma_db.collection

        self.types = [
            'home_banner_main_block',
            'home_products_list_block'
            'home_promotion_details'
            'home_product_category'
        ]
    def save_embeddings(self):
        """
        Save embeddings for markdown files in the specified directory
        with support for different content types
        """
        # Ensure data directory exists
        if not os.path.exists(self.data):
            print(f"Data directory {self.data} does not exist.")
            return

        # Track documents for batch processing
        batch_size = 100
        documents = []
        metadatas = []
        ids = []
        for filename in os.listdir(self.data):
            if not filename.endswith('.md'):
                continue

            file_path = os.path.join(self.data, filename)
            sections = self.extract_sections(file_path)

            for section in sections:
                # print(section)
                if not section['title'] or not section['description']:
                    continue

                # Create metadata
                metadata = {
                    'source': filename,
                    'title': section['title'],
                    'example': section['example'] or "",
                    'guide': section['guide'] or "",
                    'type': 'section'
                }

                # Use description as the main document
                documents.append(section['description'])
                metadatas.append(metadata)
                ids.append(str(uuid.uuid4()))

                # Xử lý theo batch
                if len(documents) >= batch_size:
                    response = self.client.embeddings.create(
                        model=self.model,
                        input=documents
                    )
                    embeddings = [item.embedding for item in response.data]
                    self.collection.add(
                        embeddings=embeddings,
                        metadatas=metadatas,
                        ids=ids,
                        documents=documents
                    )
                    documents = []
                    metadatas = []
                    ids = []

        # Process the final batch
        if len(documents) > 0:
            response = self.client.embeddings.create(
                model=self.model,
                input=documents
            )
            embeddings = [item.embedding for item in response.data]
            self.collection.add(
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids,
                documents=documents
            )

        print(f"Đã lưu {len(self.collection.get()['ids'])} sections vào ChromaDB")

    def extract_sections(self,file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        sections = []
        current_section = {'title': None, 'example': None, 'description': [], 'guide': []}
        in_raw_block = False
        example_content = []

        for line in content.split('\n'):
            # Process section titles
            if line.startswith('### '):
                # Save previous section if it has content
                if current_section['title'] or current_section['description'] or current_section['example'] or \
                        current_section['guide']:
                    sections.append(current_section)

                current_section = {
                    'title': line[4:].strip(),
                    'example': None,
                    'description': [],
                    'guide': []
                }
                continue

            if line.strip().startswith('* '):
                current_section['guide'].append(line.strip())
                continue
            elif line.strip().startswith('  * ') or line.strip().startswith('    * '):
                # This handles nested bullet points with different indentation levels
                current_section['guide'].append(line.strip())
                continue

            if '{% raw %}' in line or in_raw_block:
                if not in_raw_block and '{% raw %}' in line:
                    in_raw_block = True
                    example_content = []
                    line = line.split('{% raw %}')[-1]

                if '{% endraw %}' in line:
                    in_raw_block = False
                    example_content.append(line.split('{% endraw %}')[0])
                    current_section['example'] = '\n'.join(example_content).strip()
                    example_content = []
                    continue

                if in_raw_block:
                    example_content.append(line)
                    continue

                # Process description
            if current_section['title']:
                current_section['description'].append(line.strip())

        # Add the last section
        if current_section['title'] or current_section['description'] or current_section['example'] or current_section[
            'guide']:
            sections.append(current_section)

        # Clean description and convert to string
        for section in sections:
            section['description'] = '\n'.join([line for line in section['description'] if line]).strip()
            # Remove empty lines in example
            if section['example']:
                section['example'] = re.sub(r'\n\s*\n', '\n', section['example'])

            if section['guide']:
                section['guide'] = '\n'.join(section['guide'])
            else:
                section['guide'] = ""  # Make sure it's an empty string instead of an empty list

        return sections

    def delete_embeddings(self):
        self.chroma_client.delete_collection("data_training")
        # self.collection.delete(ids=ids)
        print("✅ Deleted all data in ChromaDB.")

    def get_embeddings(self):
        all_items = self.collection.get()
        return json.dumps(all_items, indent=2)

    def process_question(self, user_question, type = None, items = None, options = None):
        print(f"🔍 Processing question: {user_question}")
        best_match = self.get_answer_with_details(user_question)
        pattern = r"```(?:twig)?\n([\s\S]*?)```"
        if best_match:
            print(f"✅ The best answer has been found: {best_match['question']}")
            generated_code = self.generate_code_with_llama(best_match,type ,items, options)
            content = re.search(pattern, generated_code[type])
            if content:
                return content.group(1)
            return None

        else:
            print("❌ No matching logic found.")
            return {
                "success": False,
                "message": "No matching logic found."
            }

    def generate_code_with_llama(self, best_match = None, type = None, items = None, options = None):

        if options is None:
            options = {}

        type_map = {
            "banner_block": "banner",
            "home_products_list_block": "sản phẩm",
            "home_product_category": "danh mục sản phẩm",
            "home_promotion_details": "chương trình khuyến mãi",
            "home_article_news": "bài viết tin tức",
            "home_brands": "thương hiệu",
            "home_album": "album"
        }
        text = type_map.get(type, "nội dung")

        text_limit = ""
        if "limit" in options:
            text_limit = f"với số lượng {options['limit']} {text}"

        if not best_match:
            return "🚫 No matching logic found."

        prompt = f"""Dựa trên thông tin sau, hãy tạo mã Twig để hiển thị {text} {text_limit}:
                               - Ví dụ: {best_match['example']}
                               {best_match['guide']}
                               {items}
                                Sử dụng twig với mã logic ở trên, không thay đổi mã html 
                          """
        print("Processing, please wait a moment!")

        optimizer = TokenOptimizer()
        prompt = optimizer.optimize_prompt(prompt)
        if optimizer.count_tokens(prompt) > MAX_TOKEN:
            prompt = optimizer.truncate_text(prompt, MAX_TOKEN)

        print(prompt)

        # completion = client.chat.completions.create(
        #     model= MODEL_NAME,
        #     store=True,
        #     max_tokens=MAX_TOKEN,
        #     temperature=TEMPERATURE,
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": f"""{prompt}"""
        #         }
        #     ]
        # )
        # if completion:
        #     object_completion_message = completion.choices[0].message
        #     return {type: object_completion_message.content}

    def get_answer_with_details(self, question):
        # Check if collection is empty
        if self.collection.count() == 0:
            return None

        response = self.client.embeddings.create(
            model= self.model,
            input=question
        )
        # Perform semantic search
        results = self.collection.query(
            query_embeddings=[response.data[0].embedding],
            n_results=5,
            include=["documents", "metadatas", "distances"]
        )
        # Validate search results
        if (not results.get("documents") or
                not results["documents"][0]):
            return None

        # Extract top result
        matched_docs = results["documents"][0]
        matched_metas = results["metadatas"][0]
        matched_distances = results["distances"][0]
        selected_doc = None

        print(matched_docs)
        for i, doc in enumerate(matched_docs):
            relevant_section = self.extract_relevant_section(doc, question)
            if relevant_section:
                selected_doc = {
                    "document": relevant_section,
                    "metadata": matched_metas[i],
                    "distance": matched_distances[i]
                }
                break

        # Prepare answer data with fallback values
        if selected_doc is None:
            print("❌ Không tìm thấy phần nội dung phù hợp!")
            return None

        metadata = selected_doc["metadata"]
        answer_data = {
            "question": question,
            "answer": metadata.get("answer", selected_doc["document"]),
            "relevance_score": 1 - selected_doc["distance"],
            "metadata": {
                "example": metadata.get("example", ""),
                "source": metadata.get("source", "Unknown"),
                "title": metadata.get("title", ""),
                "type": metadata.get("type", "")
            }
        }
        # Parse additional optional fields with robust error handling
        try:
            # Parse logic if available
            answer_data["logic"] = json.loads(metadata.get("logic", "[]"))
        except (json.JSONDecodeError, TypeError):
            answer_data["logic"] = []
        # Add example if available
        answer_data["example"] = metadata.get("example", "")
        answer_data["guide"] = metadata.get("guide", "")

        # Modify add_training_data to handle simple data types
        # if answer_data:
        #     training_data = {
        #         "question": answer_data["question"],
        #         "answer": answer_data["answer"],
        #         "source": answer_data["metadata"].get("source", "Unknown")
        #     }
        #     self.add_training_data(question, training_data)

        return answer_data

    def extract_relevant_section(self, document, question):

        headers = re.findall(r"(### .+)", document)

        if not headers:
            return document

        # Tìm tiêu đề phù hợp nhất
        best_header = None
        for header in headers:
            if any(word in header.lower() for word in question.lower().split()):
                best_header = header
                break

        # Nếu không tìm thấy tiêu đề phù hợp, trả về toàn bộ nội dung
        if not best_header:
            return document

        # Cắt nội dung từ tiêu đề đã tìm được
        sections = document.split(best_header)
        if len(sections) < 2:
            return document  # Nếu không chia được, trả về toàn bộ


        relevant_section = sections[1].split("### ")[0]  # Lấy phần trước tiêu đề tiếp theo
        return f"{best_header}\n{relevant_section}"

    def add_training_data(self, document, metadata=None):
        if metadata is None:
            metadata = {}

        if "answer" not in metadata:
            metadata["answer"] = document

        response  = self.client.embeddings.create(
            model=self.model,
            input=document
        )
        embedding = response.data[0].embedding
        doc_id = f"doc_{abs(hash(document))}"

        # Add to collection
        self.collection.add(
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata],
            ids=[doc_id]
        )
