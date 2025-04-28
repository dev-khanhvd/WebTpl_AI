import json
from config import PAGE_TYPE_MAPPING
from utils.detect_html import DetectHtml
from website_cloner.folder_manager import FolderManager

class ProductDetailPage:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.template_mapping = json.loads(PAGE_TYPE_MAPPING)
        self.file_path = self.base_dir + '\\' + self.template_mapping['product']

    def menu_agent(self):
        while True:
            print("\n=== Fill code logic cho chi tiết sản phẩm ===")
            options = [
                'Ảnh sản phẩm',
                'Thuộc tính màu sắc',
                'Thuộc tính kích cỡ',
                'Sản phẩm liên quan',
                'Sản phẩm cùng danh mục',
                'Sản phẩm đã xem',
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
                if menu_choice in [2,3]:
                    wrapper_classes = [cls.strip() for cls in class_input.split(',')]
                    if len(wrapper_classes) > 1:
                        main_wrapper = [wrapper_classes[0] if len(wrapper_classes) > 0 else ""]
                        product_wrapper = [wrapper_classes[1] if len(wrapper_classes) > 1 else ""]
                        self.get_product_page_content(main_wrapper, menu_choice, product_wrapper)
                    else:
                        print('Nhập đủ ID và class wrapper')
                        continue
                elif menu_choice in [4,5,6]:
                    wrapper_classes = [cls.strip() for cls in class_input.split(',')]
                    if len(wrapper_classes) > 0:
                        number_limit = input(
                            f"Nhập số lượng lấy ra cho '{selected_option}' : ").strip()
                        options = {}
                        if number_limit.isdigit():
                            options = {
                                'limit': int(number_limit),
                            }
                        self.get_product_page_content(wrapper_classes, menu_choice, None, options)
                    else:
                        print('Nhập đủ ID(class) wrapper')
                        continue
                else:
                    wrapper_classes = [cls.strip() for cls in class_input.split(',')]
                    if len(wrapper_classes) > 0:
                        self.get_product_page_content(wrapper_classes, menu_choice, None)
                    else:
                        print('Nhập đủ ID(class) wrapper')
                        continue


    def get_product_page_content(self, wrapper_classes:str, choice_selected:int, item_classes=None, options=None):
        if self.base_dir:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                match choice_selected:
                    case 1:
                        question = "Danh sách ảnh sản phẩm sẽ lấy ra tất cả ảnh của sản phẩm"
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'product_images_block')
                    case 2:
                        question = "Lấy thuộc tính màu sắc của sản phẩm lên website"
                        self.detect_block_attrs(template_content, wrapper_classes, item_classes, question,'product_color_attr_block')
                    case 3:
                        question = "Lấy thuộc tính kích cỡ của sản phẩm lên website"
                        self.detect_block_attrs(template_content, wrapper_classes, item_classes, question,
                                                'product_size_attr_block')
                    case 4:
                        question = "Lấy ra những sản phẩm upSale của sản phẩm hiện tại"
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'product_upsale_block',options)
                    case 5:
                        question = "Sản phẩm cùng danh mục"
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'product_category_related_block', options)
                    case 6:
                        question = "Sản phẩm đã xem"
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'product_history_block',options)
                    case _:
                        print("Lựa chọn không hợp lệ!")

    def detect_block_fill_code(self, template_content, wrapper_classes:str, question:str, type=None, options=None):
        detect = DetectHtml(self.base_dir)
        content_soup = detect.detect_position_home_promotion_section(wrapper_classes, template_content, question, type, options)
        if content_soup:
            object_file = FolderManager(self.base_dir)
            object_file.save_file(self.file_path, content_soup)

    def detect_block_attrs(self, template_content, main_wrapper:str, product_wrapper:str, question:str, type=None):
        detect = DetectHtml(self.base_dir)
        attrs_block = detect.detect_position_product_attributes_section(main_wrapper, product_wrapper, template_content,
                                                                       question, type)
        if attrs_block:
            object_file = FolderManager(self.base_dir)
            object_file.save_file(self.file_path, attrs_block)
