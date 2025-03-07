from website_cloner.page_manager import *
from website_cloner.folder_manager import *
from config import BASE_DIR

if __name__ == "__main__":
    print("\nMenu xử lý web:")
    options = [
        'Crawl content của web',
        'Fill code logic theo từng trang'
    ]
    for i, option in enumerate(options):
        print(f"{i + 1}. {option}")

    while True:
        menu_choice = input("Nhập số thứ tự trên menu để thao tác (hoặc 'exit' để thoát): ").strip()
        if menu_choice.lower() == "exit" or menu_choice == "":
            print("👋 Thoát chương trình!")
            break
        if not menu_choice.isdigit():
            print("Lỗi: Vui lòng nhập một số hợp lệ!")
            continue
        menu_choice = int(menu_choice)
        if menu_choice == 1:
            folder_path = create_main_folder(BASE_DIR)
            if folder_path:
                create_folders(folder_path, template_structure)
                url = input("Nhập URL cần crawl: ")
                contentRaw = download_page(url)
                if contentRaw:
                    while True:
                        main_choice = input("Chọn phần cần lấy (body | layout | css): ").strip().lower()
                        if main_choice == "exit" or main_choice == "":
                            break
                        body_choice = None
                        if main_choice == "body":
                            while True:
                                body_choice = input("Chọn phần trong body (header | footer | content - Enter): ").strip().lower() or None
                                if body_choice == "" or body_choice.lower() == "exit":
                                    break
                                else:
                                    content = extract_content(contentRaw, main_choice, body_choice)
                                    if content:
                                        save_to_file(content, folder_path, template_structure)
                        elif main_choice == "layout":
                            content = extract_content(contentRaw, "layout")
                            if content:
                                save_to_file(content, folder_path, template_structure)
                        elif main_choice == "css":
                            create_css_files(contentRaw, url, folder_path)
                        else:
                            print("Không tìm thấy nội dung phù hợp!")
        else:
            import agent_main
            agent_main.run()
