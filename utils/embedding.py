import json
import uuid
import re
import os

from config import USER_NAME,PASSWORD,MODEL_NAME_4o_MINI, MODEL_NAME_4o, MAX_TOKEN, OPENAI_API_KEY, TEMPERATURE
from vector_db.elastic_search_db import ElasticsearchDB
from openai import OpenAI
from utils.token_optimizer import TokenOptimizer
from sentence_transformers import SentenceTransformer

class Embedding:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data = "./data"
        self.client = OpenAI(
            api_key=OPENAI_API_KEY
        )
        self.model = SentenceTransformer('all-mpnet-base-v2')

        # We'll initialize collections dict to store multiple ES instances
        self.collections = {}

    def save_embeddings(self):
        """
        Save embeddings for markdown files to separate indices in Elasticsearch,
        using the filename (without extension) as the index name
        """
        # Ensure data directory exists
        if not os.path.exists(self.data):
            print(f"Data directory {self.data} does not exist.")
            return

        total_sections = 0

        # Process each markdown file separately
        for filename in os.listdir(self.data):
            if not filename.endswith('.md'):
                continue

            # Create index name from filename (without extension)
            index_name = os.path.splitext(filename)[0].lower()

            # Create a new ElasticsearchDB instance for this file
            es_db = ElasticsearchDB(base_dir=self.base_dir, index_name=index_name,username=USER_NAME,password=PASSWORD)
            self.collections[index_name] = es_db

            print(f"Processing file: {filename} -> index: {index_name}")

            file_path = os.path.join(self.data, filename)
            sections = self.extract_sections(file_path)

            # Track documents for batch processing
            batch_size = 100
            documents = []
            metadatas = []
            ids = []

            for section in sections:
                if not section['title'] or not section['description']:
                    continue

                section['description'] = section['description'].replace('```', '')

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

                # Process in batches
                if len(documents) >= batch_size:
                    embeddings = self.model.encode(documents).tolist()
                    es_db.add(
                        embeddings=embeddings,
                        metadatas=metadatas,
                        ids=ids,
                        documents=documents
                    )
                    total_sections += len(documents)
                    documents = []
                    metadatas = []
                    ids = []

            # Process the final batch for this file
            if len(documents) > 0:
                embeddings = self.model.encode(documents).tolist()
                es_db.add(
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids,
                    documents=documents
                )
                total_sections += len(documents)

            print(f"✅ Added {len(sections)} sections to index '{index_name}'")

        print(f"✅ Total: Saved {total_sections} sections across {len(self.collections)} indices in Elasticsearch")

    def extract_sections(self, file_path: str):
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
        """Delete all indices created by this class"""
        # Get all indices from Elasticsearch that match our pattern
        # We'll use a simple approach - delete all indices that match the filenames in data directory
        deleted_count = 0
        for filename in os.listdir(self.data):
            if not filename.endswith('.md'):
                continue

            index_name = os.path.splitext(filename)[0].lower()
            try:
                # Create a temporary ES instance for this index
                es_db = ElasticsearchDB(base_dir=self.base_dir, index_name=index_name,username=USER_NAME,password=PASSWORD)
                es_db.delete_collection()
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting index {index_name}: {str(e)}")

        print(f"✅ Deleted {deleted_count} indices from Elasticsearch.")
        # Clear our collections dictionary
        self.collections = {}

    def get_embeddings(self, index_name=None):
        """Get all embeddings, optionally from a specific index"""
        if index_name:
            # Get embeddings from a specific index
            if index_name not in self.collections:
                # Create temporary instance if needed
                es_db = ElasticsearchDB(base_dir=self.base_dir, index_name=index_name,username=USER_NAME,password=PASSWORD)
            else:
                es_db = self.collections[index_name]

            all_items = es_db.get()
            return json.dumps(all_items, indent=2)
        else:
            # Get embeddings from all indices
            all_results = {}
            for filename in os.listdir(self.data):
                if not filename.endswith('.md'):
                    continue

                index_name = os.path.splitext(filename)[0].lower()
                try:
                    es_db = ElasticsearchDB(base_dir=self.base_dir, index_name=index_name,username=USER_NAME,password=PASSWORD)
                    all_results[index_name] = es_db.get()
                except Exception as e:
                    print(f"Error getting embeddings from {index_name}: {str(e)}")

            return json.dumps(all_results, indent=2)

    def process_question(self, user_question: str, type=None, items=None, options=None, index_name=None):
        """
        Process a question, optionally restricting to a specific index.
        If index_name is None, search across all indices.
        """
        print(f"🔍 Processing question: {user_question}")

        best_match = self.get_answer_with_details(user_question, index_name)
        pattern = r"```(?:twig)?\n([\s\S]*?)```"

        if best_match:
            print(f"✅ The best answer has been found: {best_match['question']}")
            generated_code = self.generate_code_with_llama(best_match, type, items, options)
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

    def generate_code_with_llama(self, best_match=None, type=None, items=None, options=None):
        # Existing implementation remains the same
        if options is None:
            options = {}

        type_map = {
            "banner_block": "banner",
            "home_products_list_block": "sản phẩm",
            "home_product_category": "danh mục sản phẩm",
            "home_menu_product_category": "menu danh mục sản phẩm",
            "home_promotion_details": "chương trình khuyến mãi",
            "home_article_news": "bài viết tin tức",
            "home_brands": "thương hiệu",
            "home_album": "bộ sưu tập",
            "home_voucher_list": "danh sách mã voucher",
            "category_filter_block": "bộ lọc danh mục",
            "attributes_filter_block": "bộ lọc thuộc tính",
            "price_filter_block": "bộ lọc giá",
            "brand_filter_block": "bộ lọc thương hiệu theo danh mục",
            "category_products_list_block": "danh sách sản phẩm",
            "product_category_related_block": "sản phẩm cùng danh mục",
            "product_upsale_block": "sản phẩm liên quan",
            "product_history_block": "sản phẩm đã xem",
            "product_images_block": "ảnh sản phẩm",
            "product_price_block": "giá sản phẩm",
            "product_color_attr_block": "thuộc tính màu sắc",
            "product_size_attr_block": "thuộc tính kích cỡ",
            "product_child_block": "sản phẩm con",
            "cart_product_block": "sản phẩm trong giỏ hàng",
            "order_list_block": "danh sách đơn hàng",
            "address_order_block": "địa chỉ nhận hàng",
            "album_items_block": "danh sách bài viết album",
            "album_image_items_block": "danh sách ảnh trong album",
            "album_product_items_block": "danh sách sản phẩm được tag trong album",
            "news_items_block": "danh sách bài viết tin tức",
            "news_related_items_block": "danh sách bài viết liên quan",
            "news_tag_block": "tag tin tức",
        }
        text = type_map.get(type, "nội dung")

        text_limit = ""
        if "limit" in options:
            text_limit += f"với số lượng {options['limit']} {text} "

        if 'product_type' in options:
            text_limit += f"với param {options['product_type']}"

        if type_map.get(type) == 'menu danh mục sản phẩm':
            text = "menu danh mục sản phẩm và lấy ra các danh mục con (nếu có)"

        if not best_match:
            return "🚫 No matching logic found."

        prompt = f"""Dựa trên thông tin sau, hãy tạo mã Twig để hiển thị {text} {text_limit}:
                 - Ví dụ: {best_match['example']}
                 {best_match['guide']}
                 {items}
                  Sử dụng twig với mã logic ở trên, không thay đổi mã html """
        print("Processing, please wait a moment!")

        model_name = MODEL_NAME_4o_MINI
        if type_map.get(type) in ('chương trình khuyến mãi', 'bộ lọc thuộc tính'):
            model_name = MODEL_NAME_4o

        optimizer = TokenOptimizer(model_name)
        prompt = optimizer.optimize_prompt(prompt)
        if optimizer.count_tokens(prompt) > MAX_TOKEN:
            prompt = optimizer.truncate_text(prompt, MAX_TOKEN)

        # print(prompt)
        completion = self.client.chat.completions.create(
            model=model_name,
            store=True,
            max_tokens=MAX_TOKEN,
            temperature=TEMPERATURE,
            messages=[
                {
                    "role": "user",
                    "content": f"""{prompt}"""
                }
            ]
        )
        if completion:
            object_completion_message = completion.choices[0].message
            return {type: object_completion_message.content}

    def get_answer_with_details(self, question: str, index_name=None):
        """
        Get answer with details, optionally restricting to a specific index.
        If index_name is provided, only search that index.
        Otherwise, search all indices and return the best match.
        """
        if not question:
            return None

        if index_name:
            # Search in a specific index
            indices = [index_name]
        else:
            # Search all indices derived from markdown files
            indices = []
            for filename in os.listdir(self.data):
                if filename.endswith('.md'):
                    indices.append(os.path.splitext(filename)[0].lower())

        if not indices:
            return None

        query_embedding = self.model.encode(question).tolist()
        best_result = None
        best_score = -float('inf')

        # Search each index and find the best match
        for idx in indices:
            try:
                es_db = self.collections.get(idx)
                if not es_db:
                    es_db = ElasticsearchDB(base_dir=self.base_dir, index_name=idx,username=USER_NAME,password=PASSWORD)
                    self.collections[idx] = es_db

                # Skip empty indices
                if es_db.count() == 0:
                    continue

                results = es_db.query(
                    query_embedding=query_embedding,
                    n_results=5
                )

                # Extract top result from this index
                if (not results.get("documents") or
                        not results["documents"][0]):
                    continue

                matched_docs = results["documents"][0]
                matched_metas = results["metadatas"][0]
                matched_distances = results["distances"][0]

                for i, doc in enumerate(matched_docs):
                    relevant_section = self.extract_relevant_section(doc, question)
                    if relevant_section:
                        score = 1 - matched_distances[i]  # Convert distance to similarity score
                        if score > best_score:
                            best_score = score
                            best_result = {
                                "document": relevant_section,
                                "metadata": matched_metas[i],
                                "distance": matched_distances[i],
                                "index": idx
                            }
            except Exception as e:
                print(f"Error searching index {idx}: {str(e)}")
                continue

        # No relevant results found
        if best_result is None:
            print("❌ No relevant content found in any index!")
            return None

        # Prepare answer data
        metadata = best_result["metadata"]
        answer_data = {
            "question": question,
            "answer": metadata.get("answer", best_result["document"]),
            "relevance_score": 1 - best_result["distance"],
            "metadata": {
                "example": metadata.get("example", ""),
                "source": metadata.get("source", "Unknown"),
                "title": metadata.get("title", ""),
                "type": metadata.get("type", ""),
                "index": best_result["index"]
            }
        }

        # Parse additional optional fields
        try:
            answer_data["logic"] = json.loads(metadata.get("logic", "[]"))
        except (json.JSONDecodeError, TypeError):
            answer_data["logic"] = []

        answer_data["example"] = metadata.get("example", "")
        answer_data["guide"] = metadata.get("guide", "")

        return answer_data

    def extract_relevant_section(self, document, question: str):
        headers = re.findall(r"(### .+)", document)

        if not headers:
            return document

        # Find most relevant header
        best_header = None
        for header in headers:
            if any(word in header.lower() for word in question.lower().split()):
                best_header = header
                break

        # If no suitable header found, return entire content
        if not best_header:
            return document

        # Extract content from matching header
        sections = document.split(best_header)
        if len(sections) < 2:
            return document

        relevant_section = sections[1].split("### ")[0]  # Get content before next header
        return f"{best_header}\n{relevant_section}"