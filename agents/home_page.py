import json
from config import PAGE_TYPE_MAPPING
from utils.detect_html import DetectHtml
from website_cloner.folder_manager import FolderManager


class HomePage:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.template_mapping = json.loads(PAGE_TYPE_MAPPING)
        self.file_path = self.base_dir + '\\' + self.template_mapping['homepage']

    def menu_agent(self):

        while True:
            print("\n=== Fill code logic cho trang chủ ===")
            options = [
                'Banner không giới hạn số lượng',
                'Banner giới hạn số lượng',
                'Sản phẩm trang chủ',
                'Sản phẩm theo CTKM (Nhập wrapper CTKM + Wrapper danh sách sản phẩm)',
                'Danh sách bài viết tin tức',
                'Danh sách bài viết album',
                'Danh thương hiệu',
                'Danh mục sản phẩm',
                'Danh sách mã voucher',
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
                if menu_choice == 3:
                    print("\n=== Chọn kiểu sản phẩm ===")
                    product_options = [
                        'Sản phẩm tick hot',
                        'Sản phẩm tick trang chủ',
                        'Sản phẩm tick mới',
                    ]
                    product_type_map = {
                        1: "showHot",
                        2: "showHome",
                        3: "showNew"
                    }

                    for i, product_option in enumerate(product_options, 1):
                        print(f"{i}. {product_option}")

                    product_choice = input("\nNhập số thứ tự loại sản phẩm: ").strip()

                    if not product_choice.isdigit() or int(product_choice) not in product_type_map:
                        print("❌ Lựa chọn loại sản phẩm không hợp lệ!")
                        continue

                    product_type = product_type_map[int(product_choice)]
                    wrapper_classes = [cls.strip() for cls in class_input.split(',')]
                    if len(wrapper_classes) > 0:
                        number_limit = input(
                            f"Nhập số lượng lấy ra cho '{selected_option}' : ").strip()
                        options = {}
                        if number_limit.isdigit():
                            options = {
                                'limit': int(number_limit),
                                'product_type': product_type
                            }
                        self.get_home_page_content(wrapper_classes, menu_choice, None, options)
                    else:
                        print('Nhập đủ ID(class) wrapper')
                        continue
                elif menu_choice == 4:
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
                        options = {}
                        if menu_choice not in [1,9]:
                            number_limit = input(
                                f"Nhập số lượng lấy ra cho '{selected_option}' : ").strip()
                            if number_limit.isdigit():
                                options = {
                                    'limit': int(number_limit)
                                }
                        self.get_home_page_content(wrapper_classes, menu_choice, None, options)
                    else:
                        print('Nhập đủ ID(class) wrapper')
                        continue

    def get_home_page_content(self, wrapper_classes, choice_selected, item_classes=None, options=None):
        if self.base_dir:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                match choice_selected:
                    case 1:
                        question = "Banner website có thể hiểu là những ô vuông trên đó có slogan"
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'banner_block')
                    case 2:
                        question = "Banner giới hạn số lượng trang chủ"
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'banner_block',
                                                    options)
                    case 3:
                        question = "Có 3 dạng tick để hiển thị sản phẩm trên trang chủ: tick trang chủ, tick mới hoặc tick hot"
                        self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                    'home_products_list_block', options)
                    case 4:
                        question = 'Chương trình promotion'
                        self.detect_block_promotion(template_content, wrapper_classes, item_classes, question)
                    case 5:
                        question = 'Bài viết tin tức'
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'home_article_news',
                                                    options)
                    case 6:
                        question = 'Danh sách bộ sưu tập'
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'home_album', options)
                    case 7:
                        question = 'Danh sách thương hiệu'
                        self.detect_block_fill_code(template_content, wrapper_classes, question, 'home_brands', options)
                    case 8:
                        question = 'Danh mục sản phẩm'
                        self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                    'home_product_category')
                    case 9:
                        question = 'Danh sách mã voucher'
                        self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                    'home_voucher_list')
                    case _:
                        print("Lựa chọn không hợp lệ!")

    def detect_block_fill_code(self, template_content, wrapper_classes, question, type=None, options=None):
        detect = DetectHtml(self.base_dir)
        content_soup = detect.detect_position_html(wrapper_classes, template_content, question, type, options)
        if content_soup:
            object_file = FolderManager(self.base_dir)
            object_file.save_file(self.file_path, content_soup)

    def detect_block_promotion(self, template_content, main_wrapper, product_wrapper, question):
        detect = DetectHtml(self.base_dir)
        promotion_block = detect.detect_position_home_promotion_section(main_wrapper, product_wrapper, template_content,
                                                                       question, 'home_promotion_details')
        if promotion_block:
            object_file = FolderManager(self.base_dir)
            object_file.save_file(self.file_path, promotion_block)


