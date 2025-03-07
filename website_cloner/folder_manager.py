import os
import requests
import json
from urllib.parse import urljoin, urlparse
from config import FOLDER_STRUCTURE, CONTENT_TEMPLATE_JSON

template_structure = json.loads(FOLDER_STRUCTURE)
content_template = json.loads(CONTENT_TEMPLATE_JSON)

# Tạo folder template
def create_main_folder(base_path):
    while True:
        create_folder_name = input("Nhập tên folder: ").strip().upper()
        folder_path = os.path.join(base_path, create_folder_name)
        if create_folder_name == "" or create_folder_name == "EXIT":
            break
        elif os.path.exists(folder_path):
            return folder_path
        else:
            os.makedirs(folder_path)
            return folder_path

# Tạo các folder con theo cây thư mục được khai báo ở env
def create_folders(base_path, structure):
    for key, value in structure.items():
        if key == "config":
            file_path = os.path.join(base_path, value)
            open(file_path, "w").close()
            if content_template:
                with open(file_path, "w", encoding="utf-8") as ft:
                    # Cần convert định dang dict sang json để lưu file template.json
                    json.dump(content_template, ft, ensure_ascii=False, indent=4)
        else:
            folder_path = os.path.join(base_path, key)
            os.makedirs(folder_path, exist_ok=True)
            if isinstance(value, dict):
                create_folders(folder_path, value)
            elif isinstance(value, list):
                for file in value:
                    open(os.path.join(folder_path, file), "w").close()

# Xử lý lưu nội dung theo từng file
def save_to_file(content, base_path, structure):
    print("\nChọn file để lưu nội dung vào:")
    options = []

    def traverse(struct, path=""):
        for key, value in struct.items():
            current_path = os.path.join(path, key)
            if isinstance(value, dict):
                traverse(value, current_path)
            elif isinstance(value, list):
                for file in value:
                    options.append(os.path.join(current_path, file))

    traverse(structure)

    for i, option in enumerate(options):
        print(f"{i + 1}. {option}")

    while True:
        choice = input("Nhập số file bạn muốn lưu (hoặc 'exit' để thoát): ").strip()
        if choice.lower() == "exit" or choice == "":
            return

        if not choice.isdigit():
            print("Lỗi: Vui lòng nhập một số hợp lệ!")
            continue

        choice = int(choice) - 1
        if 0 <= choice < len(options):
            file_path = os.path.join(base_path, options[choice])
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Đã lưu vào {file_path}")
            break
        else:
            print("Lựa chọn không hợp lệ!")

# Tải file css, sau đó lưu vào folder /css của tpl hiện tại
def create_css_files(content, url_crawl , folder_path):
    save_path = folder_path + '\\css\\'
    os.makedirs(save_path, exist_ok=True)
    css_links = [link.get("href") for link in content.find_all("link", rel="stylesheet") if link.get("href")]
    parsed_base_url = urlparse(url_crawl)
    base_url = 'https'
    if parsed_base_url.scheme:
        base_url = parsed_base_url.scheme

    for css_link in css_links:
        if css_link.startswith("//"):
            css_url = base_url+':' + css_link
        else:
            css_url = urljoin(base_url, css_link)
        css_name = os.path.basename(urlparse(css_url).path)
        css_name = css_name.replace("scss.css", "css")

        try:
            response = requests.get(css_url)
            response.raise_for_status()
            with open(os.path.join(save_path, css_name), "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Đã tải CSS: {css_name}")

        except requests.RequestException:
            print(f"Lỗi tải CSS: {css_url}")
