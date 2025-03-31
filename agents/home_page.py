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
            'swiper-slide',
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

    def menu_agent(self):

        while True:
            print("\n=== Fill code logic cho trang chủ ===")
            options = [
                'Banner chính',
                'Sản phẩm mới',
                'Sản phẩm hot',
                'Sản phẩm trang chủ',
                # 'Sản phẩm theo CTKM',
                'Danh sách bài viết tin tức',
                'Danh sách bài viết album',
            ]

            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")

            menu_choice = input("\nNhập số thứ tự trên menu để thao tác (hoặc 'exit' để thoát): ").strip()

            if menu_choice.lower() == "exit" or menu_choice == "":
                print("👋 Thoát chương trình!")
                break

            menu_choice = int(menu_choice)
            selected_option = options[menu_choice - 1]

            # Nhập class wrapper và class item nếu có
            class_input = input(
                f"Nhập ID(class) wrapper cho '{selected_option}' : ").strip()

            if class_input:
                wrapper_classes = [cls.strip() for cls in class_input.split(',')]
                if len(wrapper_classes) > 0:
                    self.get_home_page_content2(wrapper_classes, menu_choice)
                else:
                    print('Nhập đủ id(class) wrapper và items')
                    continue


    def get_home_page_content(self):
        if self.base_dir:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                self.detect_banner_blocks(template_content)
                # self.detect_product_list_home(template_content)

    def get_home_page_content2(self, wrapper_classes, choice_selected):
        if self.base_dir:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                match choice_selected:
                    case 1:
                        question = "Banner trên trang chủ"
                        self.detect_block_fill_code(template_content, wrapper_classes, question)
                    case 2:
                        question = "Sản phẩm tick mới"
                        self.detect_block_fill_code(template_content, wrapper_classes, question)
                    case 3:
                        question = "Sản phẩm tick hot"
                        self.detect_block_fill_code(template_content, wrapper_classes, question)
                    case 4:
                        question = "Sản phẩm tick trang chủ"
                        self.detect_block_fill_code(template_content, wrapper_classes, question)
                    # case 5:
                    #     question = "Sản phẩm chương trình promotion"
                    #     self.detect_block_fill_code(template_content, wrapper_classes, question)
                    case 5:
                        question = 'Danh sách Tin tức'
                        self.detect_block_fill_code(template_content, wrapper_classes, question)
                    case 6:
                        question = 'Danh sách bộ sưu tập'
                        self.detect_block_fill_code(template_content, wrapper_classes, question)
                    case _:
                        print("Lựa chọn không hợp lệ!")


    def detect_banner_blocks(self, template_content, question):
        question = "Banner trên trang chủ website?"
        content_soup = self.detect_position_home(self.main_banner_wrapper_patterns, self.main_banner_item_keywords, template_content, question, 'home_banner_main_block')
        # result = None
        # if content_soup:
        #     self.detect_product_list_home(content_soup)

    def detect_product_list_home(self, template_content):
        question = "Sản phẩm mới trên trang chủ website?"
        # return self.detect_position_home(self.main_product_wrapper_patterns, self.main_product_item_keywords, template_content, question, 'home_products_list_block')
        content_soup = self.detect_position_home(self.main_product_wrapper_patterns, self.main_product_item_keywords, template_content, question, 'home_products_list_block')
        if content_soup:
            self.update_content_home_page(content_soup)

    def detect_block_fill_code(self, template_content, wrapper_classes, question):
        content_soup = self.detect_position_home3(wrapper_classes, template_content, question, 'home_products_list_block')
        if content_soup:
            self.update_content_home_page(content_soup)

    def detect_position_home(self, wrapper_pattern, soup, question = None, type = None):
        return self.detect_position_home3(wrapper_pattern, soup, question, type)
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

    def detect_position_home3(self, wrapper_pattern, soup, question=None, type=None):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'html.parser')

            # Step 1: Find potential parent wrappers based on patterns
        potential_parents = []
        for pattern in wrapper_pattern:
            # Try to find by ID first, then fall back to class
            id_elements = soup.find_all(id=re.compile(pattern))
            class_elements = soup.find_all(class_=re.compile(pattern))
            potential_parents.extend(id_elements)
            potential_parents.extend(class_elements)

        parent_wrapper = None
        if potential_parents:
            parent_wrapper = potential_parents[0]
            item = None
            if parent_wrapper.contents:
                for child in parent_wrapper.contents:
                    if child and not isinstance(child, str) or (isinstance(child, str) and child.strip()):
                        item = child
                        break
            if not item:
                item = parent_wrapper.find()

            parent_wrapper.clear()

            embedding = Embedding(self.base_dir)
            result = embedding.process_question(question, type, item)
            if result:
                twig_soup = BeautifulSoup(f"\n{result}\n", "html.parser")
                parent_wrapper.append(twig_soup)

                return soup

        return None

    def update_content_home_page(self, content):
        if content:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(str(content.prettify(formatter=None)))