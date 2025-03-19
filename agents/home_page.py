import json
from config import PAGE_TYPE_MAPPING
from bs4 import BeautifulSoup
from utils.embedding import Embedding

class HomePage:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.template_mapping = json.loads(PAGE_TYPE_MAPPING)
        self.file_path = self.base_dir + '\\' + self.template_mapping['homepage']

        # Define banner slide home
        self.main_banner_container_identifiers = [
            {'class_contains': 'home-slider'},
            {'class_contains': 'slider-home'},
            {'id_contains': 'home-slider'},
            {'id_contains': 'slider-home'}
        ]
        self.main_wrapper_identifiers = [
            {'class_contains': '-wrapper'},
            {'class_contains': 'wrapper'},
        ]
        self.main_item_identifiers = [
            {'class_contains': '-item'},
            {'class_contains': '-items'},
            {'class_contains': 'item'},
            {'class_contains': 'items'},
        ]

        # Define product home
        self.main_product_list_container_identifiers = [
            {'class_contains': '-product-list'},
            {'class_contains': 'product-list'},
            {'id_contains': '-product-list'},
            {'id_contains': 'product-list'}
        ]
        self.main_product_item_identifiers = [
            {'class_contains': '-items'},
            {'class_contains': 'product-items'},
            {'class_contains': 'product-items'},
        ]

    def get_home_page_content(self):
        if self.base_dir:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                # self.detect_banner_blocks(template_content)
                self.detect_product_list_home(template_content)

    def detect_banner_blocks(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        banner_container = None
        for rule in self.main_banner_container_identifiers:
            if 'class_contains' in rule:
                elements = soup.find_all(class_=lambda c: c and rule['class_contains'] in c)
                if elements:
                    banner_container = elements[0]
                    break
            elif 'id_contains' in rule:
                elements = soup.find_all(id=lambda i: i and rule['id_contains'] in i)
                if elements:
                    banner_container = elements[0]
                    break

        if not banner_container:
            return None

        wrapper = None
        for rule_wrapper in self.main_wrapper_identifiers:
            elements = banner_container.find_all(class_=lambda c: c and rule_wrapper['class_contains'] in c)
            if elements:
                wrapper = elements[0]
                break

        if not wrapper:
            # If no wrapper found, use the container itself as wrapper
            wrapper = banner_container

        # Find items
        items = []
        for rule_item in self.main_item_identifiers:
            elements = wrapper.find_all(class_=lambda c: c and rule_item['class_contains'] in c)
            if elements:
                items = elements
                break

        if not items or len(items) == 0:
            return None

        # Extract one representative item
        banner_item = str(items[0])
        wrapper.clear()

        question = "How to display banner list?"
        embedings = Embedding(self.base_dir)
        result = embedings.process_question(question, 'home_banner_main_block', banner_item)
        if result:
            twig_soup = BeautifulSoup(f"\n{result}\n", "html.parser")
            wrapper.insert_before(twig_soup)

        self.detect_product_list_home(soup)

    def detect_product_list_home(self, soup):
        product_container = None
        for rule in self.main_product_list_container_identifiers:
            if 'class_contains' in rule:
                elements = soup.find_all(class_=lambda c: c and rule['class_contains'] in c)
                if elements:
                    product_container = elements[0]
                    break
            elif 'id_contains' in rule:
                elements = soup.find_all(id=lambda i: i and rule['id_contains'] in i)
                if elements:
                    product_container = elements[0]
                    break
        if not product_container:
            return None

        items = []
        for rule_item in self.main_product_item_identifiers:
            elements = product_container.find_all(class_=lambda c: c and rule_item['class_contains'] in c)
            if elements:
                items = elements
                break

        if not items or len(items) == 0:
            return None

        # Extract one representative item
        list_product_items = str(items[0])
        print(list_product_items)

    def update_content_home_page(self, content):
        if content:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(str(content.prettify()))




