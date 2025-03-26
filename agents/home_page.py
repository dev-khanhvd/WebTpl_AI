import json
import re
from config import PAGE_TYPE_MAPPING
from bs4 import BeautifulSoup
from utils.embedding import Embedding

class HomePage:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.template_mapping = json.loads(PAGE_TYPE_MAPPING)
        self.file_path = self.base_dir + '\\' + self.template_mapping['homepage']

        # Define banner slide home
        self.main_banner_wrapper_patterns = [
            'swiper-wrapper',
        ]
        self.main_banner_item_keywords = [
            'home-slider-item',
        ]

        # Define product home
        self.main_product_wrapper_patterns = [
            'home-product-list',
            'home-product-list-wrapper',
            'home-product-list-slider'
        ]
        self.main_product_item_keywords = [
            'product-item',
        ]

    def get_home_page_content(self):
        if self.base_dir:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                self.detect_banner_blocks(template_content)

    def detect_banner_blocks(self, template_content):
        question = "Banner trên trang chủ website?"
        content_soup = self.detect_position_home(self.main_banner_wrapper_patterns, self.main_banner_item_keywords, template_content, question, 'home_banner_main_block')
        # result = None
        if content_soup:
            # self.detect_product_list_home(content_soup)
            self.update_content_home_page(content_soup)

    def detect_product_list_home(self, template_content):
        question = "How to display products list?"
        # return self.detect_position_home(self.main_product_wrapper_patterns, self.main_product_item_keywords, template_content, question, 'home_products_list_block')
        content_soup = self.detect_position_home(self.main_product_wrapper_patterns, self.main_product_item_keywords, template_content, question, 'home_products_list_block')
        if content_soup:
            self.update_content_home_page(content_soup)

    def detect_position_home(self, wrapper_pattern, item_pattern, soup, question = None, type = None):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'html.parser')

        parent_wrapper = None
        # Step 1: Find potential parent wrappers based on patterns
        potential_parents = []
        for pattern in wrapper_pattern:
            elements = soup.find_all(class_=re.compile(pattern))
            potential_parents.extend(elements)
            # Step 2: For each potential parent, search for banner items
            found_items = []
            for parent in potential_parents:
                # Try to find items directly
                items = []
                for keyword in item_pattern:
                    found = parent.find_all(class_=re.compile(keyword), recursive=False)
                    if found:
                        items.extend(found)
                # If no items found at the direct level, search deeper in the DOM
                if items:
                    found_items = items
                    parent_wrapper = parent
                    break
                # Step 3: If no items found at direct level, search deeper in the DOM
            if not found_items:
                for parent in potential_parents:
                    # Search deeper
                    items = []
                    for keyword in item_pattern:
                        found = parent.find_all(class_=re.compile(keyword))
                        if found:
                            items.extend(found)

                    if items:
                        found_items = items
                        # Get the direct parent of the first item (which should be the wrapper)
                        parent_wrapper = items[0].parent
                        break

                # Step 4: If found items, check for consistent classes and store information
            if found_items:
                items = str(found_items[0])
                parent_wrapper.clear()

                embedings = Embedding(self.base_dir)
                result = embedings.process_question(question, type, items)
                if result:
                    twig_soup = BeautifulSoup(f"\n{result}\n", "html.parser")
                    parent_wrapper.append(twig_soup)

                    return soup
            return None

    def update_content_home_page(self, content):
        if content:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(str(content.prettify(formatter=None)))