import platform
import subprocess

from agents.category_page import CategoryPage
from agents.home_page import HomePage
from agents.menu_part import MenuPart
from agents.product_detail_page import ProductDetailPage


class BaseAgent:
    def __init__(self, base_dir):
        self.base_dir = base_dir
    def menu_agent(self):
        options = [
            'Trang chủ',
            'Danh mục sản phẩm',
            'Menu trang chủ',
            'Chi tiết sản phẩm',
            'Giỏ hàng',
            'Thanh toán',
            'Thanh toán thành công',
        ]
        while True:
            self.clear_screen()
            print("\n=== Menu xử lý fill logic website ===")
            for i, option in enumerate(options):
                print(f"{i + 1}. {option}")

            menu_choice = input("Nhập số thứ tự trên menu để thao tác (hoặc 'exit' để thoát): ").strip()

            if menu_choice.lower() == "exit" or not menu_choice:
                print("👋 Thoát module xử lý logic!")
                break

            if not menu_choice.isdigit():
                print("Lỗi: Vui lòng nhập một số hợp lệ!")
                continue

            menu_choice = int(menu_choice)

            if menu_choice == 1:
                home_page = HomePage(self.base_dir)
                home_page.menu_agent()
                break
            elif menu_choice == 2:
                category_page = CategoryPage(self.base_dir)
                category_page.menu_agent()
                continue
            elif menu_choice == 3:
                menu_part = MenuPart(self.base_dir)
                menu_part.load_menu()
                continue
            elif menu_choice == 4:
                product_page = ProductDetailPage(self.base_dir)
                product_page.menu_agent()
                continue
            elif menu_choice == 5:
                continue
            elif menu_choice == 6:
                continue
            else:
                break


    def clear_screen(self):
        """Clear the terminal screen based on the operating system."""
        if platform.system() == "Windows":
            subprocess.call('cls', shell=True)
        else:  # For Linux and MacOS
            subprocess.call('clear', shell=True)