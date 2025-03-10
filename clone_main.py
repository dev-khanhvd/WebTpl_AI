from website_cloner.page_manager import fetch_all_pages
from website_cloner.folder_manager import FolderManager
from config import BASE_DIR, FOLDER_STRUCTURE
import json
import os


def main():
    print("\n=== Website Cloner Tool ===")
    print("Tool này sẽ giúp bạn crawl website và tạo template theo cấu trúc.")

    options = [
        'Crawl content của web',
        'Thoát'
    ]

    for i, option in enumerate(options):
        print(f"{i + 1}. {option}")

    while True:
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
                # Create folder structure based on template
                template_structure = json.loads(FOLDER_STRUCTURE)
                folder_manager.create_childs_folder(folder_path, template_structure)

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
                fetch_all_pages(url, folder_path)

                # Show results
                print("\n=== Kết quả crawl ===")
                print(f"✅ Đã crawl xong website: {display_url}")
                print(f"✅ Dữ liệu được lưu tại: {folder_path}")

                # Show template.json location
                template_json_path = os.path.join(folder_path, "template.json")
                if os.path.exists(template_json_path):
                    print(f"✅ Thông tin template được lưu tại: {template_json_path}")

                print("\nHãy kiểm tra nội dung các file đã crawl và điều chỉnh nếu cần.")

        elif menu_choice == 2:
            print("👋 Thoát chương trình!")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng thử lại!")


if __name__ == "__main__":
    main()