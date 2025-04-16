import json
import re
from config import PAGE_TYPE_MAPPING
from bs4 import BeautifulSoup
from utils.embedding import Embedding
from website_cloner.folder_manager import FolderManager

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
                'Sản phẩm theo CTKM (Nhập wrapper CTKM + Wrapper danh sách sản phẩm)',
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
                        self.get_home_page_content(main_wrapper, menu_choice, product_wrapper)
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
                        self.get_home_page_content(wrapper_classes, menu_choice, None, options)
                    else:
                        print('Nhập đủ ID(class) wrapper')
                        continue


    def get_home_page_content(self, wrapper_classes, choice_selected, item_classes = None, options = None):
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
                        question = 'Chương trình promotion'
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

    def detect_block_fill_code(self, template_content, wrapper_classes, question, type=None, options = None):
        object_ebd = Embedding(self.base_dir)
        content_soup = object_ebd.detect_position_html(wrapper_classes, template_content, question,type, options)
        if content_soup:
            object_file = FolderManager(self.base_dir)
            object_file.save_file(self.file_path,content_soup)

    def detect_block_promotion(self, template_content, main_wrapper, product_wrapper, question):
        section_header = self.detect_position_home_promotion_section(main_wrapper, product_wrapper,template_content, question, 'home_promotion_details')
        if section_header:
            if section_header.get('list_product'):
                question = "Sản phẩm trong chương trình khuyến mãi"
                result_promotion = self.detect_position_home_promotion_products(product_wrapper, section_header.get('list_product'), section_header.get('htmp_soup'), question,
                                                             'home_products_promotion_details')
                if result_promotion:
                    object_file = FolderManager(self.base_dir)
                    object_file.save_file(self.file_path,result_promotion)

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

