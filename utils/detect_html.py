import re
from bs4 import BeautifulSoup
from utils.embedding import Embedding

class DetectHtml:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def detect_position_html(self, wrapper_pattern, soup, question=None, type=None, options = None):

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

            embedings = Embedding(self.base_dir)
            result = embedings.process_question(question, type, item, options)
            if result:
                twig_soup = BeautifulSoup(f"\n{result}\n", "html.parser")
                parent_wrapper.append(twig_soup)

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
