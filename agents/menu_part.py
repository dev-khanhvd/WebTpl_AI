import json
import re
import os
from config import PAGE_TYPE_MAPPING
from bs4 import BeautifulSoup
from utils.embedding import Embedding

class MenuPart:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.template_mapping = json.loads(PAGE_TYPE_MAPPING)

    def load_menu(self):
        class_input = input(f"Nhập nơi cần xử lý menu (Ví dụ: hompage, header, footer) : ").strip()
        if class_input:
            file_path = os.path.join(self.base_dir, self.template_mapping.get(class_input, ""))
            with open(file_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
            menu_wrapper = input(f"Nhập wrapper menu cho menu vùng '{class_input.lower()}' : ").strip()
            if template_content:
                self.extract_menu(template_content, menu_wrapper, file_path)

    def extract_menu(self, html, wrapper_selector, file_path):
        potential_parents = []
        soup = BeautifulSoup(html, "html.parser")
        elements = soup.find_all(id=re.compile(wrapper_selector))
        if not elements:
            elements = soup.find_all(class_=re.compile(wrapper_selector))

        if elements:
            potential_parents.extend(elements)

        if potential_parents:
            parent_wrapper = potential_parents[0]
            for ul in parent_wrapper.find_all("ul"):
                self.filter_ul(ul)

            embedings = Embedding(self.base_dir)

            menu_html1 = str(parent_wrapper)
            file_path1 = os.path.join(self.base_dir, self.template_mapping.get('menu', ""))
            question1 = 'Danh mục sản phẩm'
            menu_result_1 = embedings.process_question(question1, 'home_menu_product_category', menu_html1)
            with open(file_path1, "w", encoding="utf-8") as f1:
                f1.write(menu_result_1)

            menu_html2 = str(parent_wrapper)
            file_path2 = os.path.join(self.base_dir, self.template_mapping.get('menu_custom', ""))
            question2 = 'Danh mục tự tạo'
            menu_result_2 = embedings.process_question(question2, 'home_menu_product_category', menu_html2)
            with open(file_path2, "w", encoding="utf-8") as f2:
                f2.write(menu_result_2)

            twig_code = """
            {% if(menuIsExisted({'type': 'header' })) %}
                {% include 'other/menu_custom' %}
            {% else %}
                {% include 'other/menu' %}
            {% endif %}
            """.strip()

            parent_wrapper.replace_with(soup.new_string(twig_code))

            with open(file_path, "w", encoding="utf-8") as f3:
                f3.write(str(soup.prettify()))

        return None

    def filter_ul(self, ul_tag):
        if not ul_tag:
            return

        lis = ul_tag.find_all("li", recursive=False)

        kept_li = None
        for li in lis:
            has_sub_ul = li.find("ul", recursive=False)
            if has_sub_ul:
                kept_li = li
                break

        if not kept_li and lis:
            kept_li = lis[0]  # Giữ li đầu tiên nếu không có ul con

        for li in lis:
            if li != kept_li:
                li.decompose()
        # Đệ quy tiếp nếu kept_li có ul con
        if kept_li:
            sub_uls = kept_li.find_all("ul", recursive=False)
            for sub_ul in sub_uls:
                self.filter_ul(sub_ul)