import json
from config import PAGE_TYPE_MAPPING
from utils.detect_html import DetectHtml
from website_cloner.folder_manager import FolderManager

class CategoryPage:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.template_mapping = json.loads(PAGE_TYPE_MAPPING)
        self.file_path = self.base_dir + '\\' + self.template_mapping['category']['product_category']

    def menu_agent(self):
        while True:
            print("\n=== Fill code logic cho danh mục sản phẩm ===")
            options = [
                'Bộ lọc danh mục sản phẩm',
                'Bộ lọc thuộc tính',
                'Bộ lọc giá sản phẩm',
                'Bộ lọc thương hiệu',
                'Danh sách sản phẩm theo phân trang',
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
                if menu_choice in (2, 3):
                    wrapper_classes = [cls.strip() for cls in class_input.split(',')]
                    if len(wrapper_classes) > 1:
                        main_wrapper = [wrapper_classes[0] if len(wrapper_classes) > 0 else ""]
                        product_wrapper = [wrapper_classes[1] if len(wrapper_classes) > 1 else ""]
                        type_filter = 'attributes_filter_block'
                        if menu_choice == 3:
                            type_filter = 'price_filter_block'
                        options = {
                            'type': type_filter
                        }
                        self.get_product_page_content(main_wrapper, menu_choice, product_wrapper, options)
                    else:
                        print('Nhập đủ ID và class wrapper')
                        continue
                else:
                    wrapper_classes = [cls.strip() for cls in class_input.split(',')]
                    if len(wrapper_classes) > 0:
                        self.get_product_page_content(wrapper_classes, menu_choice, None)
                    else:
                        print('Nhập đủ ID(class) wrapper')
                        continue

    def get_product_page_content(self, wrapper_classes, choice_selected, item_classes=None, options=None):
        if self.base_dir:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                match choice_selected:
                    case 1:
                        question = "Cây danh mục sản phẩm hiển thị danh mục con của danh mục sản phẩm"
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'category_filter_block')
                    case 2:
                        question = "Bộ lọc thuộc tính cho danh mục"
                        self.get_product_block_attrs(template_content, wrapper_classes, item_classes, question, options)
                    case 3:
                        question = "Bộ lọc giá sản phẩm"
                        self.get_product_block_attrs(template_content, wrapper_classes, item_classes, question, options)
                    case 4:
                        question = "Lấy ra danh sách các thương hiệu theo danh mục sản phẩm"
                        self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                    'brand_filter_block', options)
                    case 5:
                        question = 'Danh sách sản phẩm bao gồm tất cả các sản phẩm có thể bán'
                        self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                    'category_products_list_block', options)

                    case _:
                        print("Lựa chọn không hợp lệ!")

    def detect_block_fill_code(self, template_content, wrapper_classes, question, type=None, options=None):
        detect = DetectHtml(self.base_dir)
        content_soup = detect.detect_position_html(wrapper_classes, template_content, question, type, options)
        if content_soup:
            object_file = FolderManager(self.base_dir)
            object_file.save_file(self.file_path, content_soup)

    def get_product_block_attrs(self, template_content, main_wrapper, product_wrapper, question, options=None):
        detect = DetectHtml(self.base_dir)
        promotion_block = detect.detect_position_product_attributes_section(main_wrapper, product_wrapper, template_content,
                                                                       question, options['type'])
        if promotion_block:
            object_file = FolderManager(self.base_dir)
            object_file.save_file(self.file_path, promotion_block)