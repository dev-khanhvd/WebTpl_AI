import json
import os
import platform
import subprocess

from website_cloner.page_manager import fetch_all_pages
from website_cloner.folder_manager import FolderManager
from utils.embedding import Embedding
from config import BASE_DIR, FOLDER_STRUCTURE
from website_cloner.website_rule.haravan_rule import HaravanRule
from website_cloner.website_rule.sapo_rule import SapoRule


def main():

    auto_embedding = Embedding(BASE_DIR)
    auto_embedding.save_embeddings()
    # auto_embedding.delete_embeddings(['id_0', 'id_1'])
    # test = auto_embedding.get_embeddings()
    # print(test)
    #
    # print("\n=== Website Cloner Tool ===")
    #
    options = [
        'Crawl content của web',
        'Fill code logic theo từng trang',
    ]

    folder_url = ''
    while True:
        clear_screen()

        print("\n=== Website Cloner Tool ===")
        for i, option in enumerate(options):
            print(f"{i + 1}. {option}")

        menu_choice = input("\nNhập số thứ tự trên menu để thao tác (hoặc 'exit' để thoát): ").strip()

        if menu_choice.lower() == "exit" or menu_choice == "":
            print("👋 Thoát chương trình!")
            break

        if not menu_choice.isdigit():
            print("Lỗi: Vui lòng nhập một số hợp lệ!")
            continue

        menu_choice = int(menu_choice)

        if menu_choice == 1:
            # Create folder structure
            folder_manager = FolderManager(BASE_DIR)
            folder_path = folder_manager.create_main_folder()
            if folder_path:
                folder_url = folder_path
                # Create folder structure based on template
                template_structure = json.loads(FOLDER_STRUCTURE)
                folder_manager.create_childs_folder(folder_path, template_structure)

                print("\n=== Website Cloner Rules ===")
                website_rules = [
                    'Lấy website từ Haravan',
                    'Lấy website từ Sapo',
                    'Nếu đã có sẵn thì thao tác (hoặc "exit" để thoát)'
                ]
                for i, option in enumerate(website_rules):
                    print(f"{i + 1}. {option}")

                while True:
                    menu_rule = input("\nNhập số thứ tự trên menu để thao tác (hoặc 'exit' để thoát): ").strip()

                    if menu_rule.lower() == "exit" or menu_rule == "":
                        print("Quay lại menu chính...")
                        break

                    if not menu_rule.isdigit():
                        print("Lỗi: Vui lòng nhập một số hợp lệ!")
                        continue

                    menu_rule = int(menu_rule)
                    if menu_rule == 1:
                        haravan_rule = HaravanRule()
                        page_rules = haravan_rule.get_rules()
                    elif menu_rule == 2:
                        sapo_rule = SapoRule()
                        page_rules = sapo_rule.sapo_types
                    else:
                        print("Lựa chọn không hợp lệ. Vui lòng thử lại!")
                        continue

                    if page_rules:
                        # Get URL to crawl
                        url = input("Nhập URL cần crawl (vd: example.com): ").strip()

                        # Remove protocol if present for cleaner display
                        if url.startswith(('http://', 'https://')):
                            display_url = url.split('://', 1)[1]
                        else:
                            display_url = url

                        print(f"\nBắt đầu crawl website: {display_url}")
                        print("Quá trình này có thể mất vài phút. Vui lòng đợi...")

                        # Start crawling
                        fetch_all_pages(url, folder_path, page_rules)
                        #
                        # Show results
                        print("\n=== Kết quả crawl ===")
                        print(f"✅ Đã crawl xong website: {display_url}")
                        print(f"✅ Dữ liệu được lưu tại: {folder_path}")

                        # Show template.json location
                        template_json_path = os.path.join(folder_path, "template.json")
                        if os.path.exists(template_json_path):
                            print(f"✅ Thông tin template được lưu tại: {template_json_path}")

                        print("\nHãy kiểm tra nội dung các file đã crawl và điều chỉnh nếu cần.")

                        break
        elif menu_choice == 2:
            from agents.base_agent import BaseAgent
            base_agent = BaseAgent(folder_url)
            base_agent.menu_agent()
            # if folder_url:
            #     from agents.base_agent import BaseAgent
            #     base_agent = BaseAgent(folder_url)
            #     base_agent.menu_agent()
            # else:
            #     print("Lỗi: Chưa crawl website nào. Vui lòng chọn tùy chọn 1 trước!")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng thử lại!")

def clear_screen():
    """Clear the terminal screen based on the operating system."""
    if platform.system() == "Windows":
        subprocess.call('cls', shell=True)
    else:  # For Linux and MacOS
        subprocess.call('clear', shell=True)


if __name__ == "__main__":
    main()