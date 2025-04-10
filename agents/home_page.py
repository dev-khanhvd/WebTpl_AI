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
                'Banner không giới hạn số lượng',
                'Banner giới hạn số lượng',
                'Sản phẩm mới',
                'Sản phẩm hot',
                'Sản phẩm trang chủ',
                'Sản phẩm theo CTKM',
                'Danh sách bài viết tin tức',
                'Danh sách bài viết album',
                'Danh thương hiệu',
                'Danh mục sản phẩm',
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
                if menu_choice == 6:
                    wrapper_classes = [cls.strip() for cls in class_input.split(',')]
                    if len(wrapper_classes) > 1:
                        main_wrapper = [wrapper_classes[0] if len(wrapper_classes) > 0 else ""]
                        product_wrapper = [wrapper_classes[1] if len(wrapper_classes) > 1 else ""]
                        self.get_home_page_content2(main_wrapper, menu_choice, product_wrapper)
                    else:
                        print('Nhập đủ ID và class wrapper')
                        continue
                else:
                    wrapper_classes = [cls.strip() for cls in class_input.split(',')]
                    if len(wrapper_classes) > 0:
                        number_limit = input(
                            f"Nhập số lượng lấy ra cho '{selected_option}' : ").strip()
                        options = {}
                        if number_limit.isdigit():
                            options = {
                                'limit': int(number_limit)
                            }
                        self.get_home_page_content2(wrapper_classes, menu_choice, None, options)
                    else:
                        print('Nhập đủ ID(class) wrapper')
                        continue


    def get_home_page_content(self):
        if self.base_dir:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                self.detect_banner_blocks(template_content)
                # self.detect_product_list_home(template_content)

    def get_home_page_content2(self, wrapper_classes, choice_selected, item_classes = None, options = None):
        if self.base_dir:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                match choice_selected:
                    case 1:
                        question = "Banner slide trên trang chủ"
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'banner_block')
                    case 2:
                        question = "Banner limit trên trang chủ"
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'banner_block', options)
                    case 3:
                        question = "Sản phẩm tick mới"
                        self.detect_block_fill_code(template_content, wrapper_classes, question,'home_products_list_block', options)
                    case 4:
                        question = "Sản phẩm hot"
                        self.detect_block_fill_code(template_content, wrapper_classes, question,'home_products_list_block', options)
                    case 5:
                        question = "Sản phẩm được tick trang chủ"
                        self.detect_block_fill_code(template_content, wrapper_classes, question,'home_products_list_block', options)
                    case 6:
                        question = 'Chương trình khuyến mãi?'
                        self.detect_block_promotion(template_content, wrapper_classes, item_classes, question)
                    case 7:
                        question = 'Bài viết tin tức'
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'home_article_news', options)
                    case 8:
                        question = 'Danh sách bộ sưu tập'
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'home_album', options)
                    case 9:
                        question = 'Danh sách thương hiệu'
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'home_brands', options)
                    case 10:
                        question = 'Danh mục sản phẩm'
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'home_product_category')
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

    def detect_block_fill_code(self, template_content, wrapper_classes, question, type=None, options = None):
        content_soup = self.detect_position_home3(wrapper_classes, template_content, question,type, options)
        if content_soup:
            self.update_content_home_page(content_soup)

    def detect_block_promotion(self, template_content, main_wrapper, product_wrapper, question):
        section_header = self.detect_position_home_promotion_section(main_wrapper, product_wrapper,template_content, question, 'home_promotion_details')
        if section_header:
            if section_header.get('list_product'):
                question = "Sản phẩm trong chương trình khuyến mãi"
                result_promotion = self.detect_position_home_promotion_products(product_wrapper, section_header.get('list_product'), section_header.get('htmp_soup'), question,
                                                             'home_promotion_details')
                if result_promotion:
                    self.update_content_home_page(result_promotion)

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

    def detect_position_home3(self, wrapper_pattern, soup, question=None, type=None, options = None):

        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'html.parser')

            # Step 1: Find potential parent wrappers based on patterns
        potential_parents = []
        for pattern in wrapper_pattern:
            # Try to find by ID first, then fall back to class
            elements = soup.find_all(id=re.compile(pattern))
            if not elements:
                elements = soup.find_all(class_=re.compile(pattern))

            if elements:
                potential_parents.extend(elements)


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
            result = embedding.process_question(question, type, item, options)
            if result:
                twig_soup = BeautifulSoup(f"\n{result}\n", "html.parser")
                parent_wrapper.append(twig_soup)

                return soup

        return None

    def detect_position_home_promotion_products2(self, main_wrapper, product_wrapper, soup, question=None, type=None):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'html.parser')

        prd_wrapper = None
        main_product_wrp = None
        found_items = []
        potential_parents = []
        for pattern in main_wrapper:
            elements = soup.find_all(id=re.compile(pattern))
            if not elements:
                elements = soup.find_all(class_=re.compile(pattern))

            potential_parents.extend(elements)

            for parent in potential_parents:
                items = []
                for keyword in product_wrapper:
                    found = soup.find_all(id=re.compile(keyword))
                    if not found:
                        found = soup.find_all(class_=re.compile(keyword))
                    if found:
                        items.extend(found)
                    if items:
                        found_items = items[0].find_all("div", recursive=False)
                        main_product_wrp = items[0].parent
                        prd_wrapper = items[0]
        if found_items:
            prd_wrapper.clear()
            prd_wrapper.append(found_items[0])
            list_prd_promt = main_product_wrp.find()
            main_product_wrp.clear()
            if potential_parents:
                promotion_section = str(potential_parents[0])
                embedings = Embedding(self.base_dir)
                result = embedings.process_question(question, type, promotion_section)
                if result:
                    product_question = "Sản phẩm trong chương trình khuyến mãi"
                    rs_prd = embedings.process_question(product_question, type, list_prd_promt)
                    if rs_prd:
                        section_prd = BeautifulSoup(f"\n{rs_prd}\n", "html.parser")
                        prd_wrapper.append(section_prd)
                    return soup
        return None

    def detect_position_home_promotion_section(self, main_wrapper, product_wrapper, soup, question=None, type=None):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'html.parser')

        prd_wrapper = None
        main_product_wrp = None
        found_items = []
        potential_parents = []
        section_wrp = None
        # Tìm các phần tử tiềm năng theo main_wrapper pattern
        for pattern in main_wrapper:
            elements = soup.find_all(id=re.compile(pattern))
            if not elements:
                elements = soup.find_all(class_=re.compile(pattern))
            potential_parents.extend(elements)
        # Tìm các sản phẩm theo product_wrapper pattern
        for parent in potential_parents:
            items = []
            for keyword in product_wrapper:
                found = soup.find_all(id=re.compile(keyword))
                if not found:
                    found = soup.find_all(class_=re.compile(keyword))
                if found:
                    items.extend(found)

                if items:
                    found_items = items[0].find_all("div", recursive=False)
                    main_product_wrp = items[0].parent
                    prd_wrapper = items[0]
                    break
            if found_items:
                break

        if found_items and prd_wrapper and main_product_wrp and potential_parents:
            # tạo 1 biến chứa list sản phẩm để trả về 1 mảng cùng với soup
            # mục đích: sau khi có data return thì bắt đầu call AI để fill code tiếp vào block này
            list_prd_promt = found_items[0]
            first_products = list_prd_promt.find_all("div", recursive=False)
            prd_wrapper.clear()
            list_prd_promt.clear()
            list_prd_promt.append(first_products[0])

            # Xử lý wrapper CTKM trước
            parent_wrapper = potential_parents[0]
            if parent_wrapper.contents:
                for child in parent_wrapper.contents:
                    if child and not isinstance(child, str) or (isinstance(child, str) and child.strip()):
                        section_wrp = child
                        break

            promotion_section = potential_parents[0]
            promotion_section.clear()
            embedings = Embedding(self.base_dir)
            result = embedings.process_question(question, type, section_wrp)

            if result:
                section_prm = BeautifulSoup(f"\n{result}\n", "html.parser")
                promotion_section.append(section_prm)

                list_items_promotion = {
                    'htmp_soup' : soup,
                    'list_product' : list_prd_promt,
                }
                return list_items_promotion

        return None
    def detect_position_home_promotion_products(self, main_wrapper,product_wrp, soup, question=None, type=None):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'html.parser')

        potential_parents = []
        for pattern in main_wrapper:
            elements = soup.find_all(id=re.compile(pattern))
            if not elements:
                elements = soup.find_all(class_=re.compile(pattern))
            potential_parents.extend(elements)

        if potential_parents:
            section_wrp = potential_parents[0]
            embedings = Embedding(self.base_dir)
            result = embedings.process_question(question, type, product_wrp)
            if result:
                section_prm = BeautifulSoup(f"\n{result}\n", "html.parser")
                section_wrp.append(section_prm)
            return soup
        return None

    def update_content_home_page(self, content):
        if content:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(str(content.prettify(formatter=None)))