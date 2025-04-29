import os
import json
from config import CONTENT_TEMPLATE_JSON
import requests
from urllib.parse import urlparse, urljoin
import uuid

class FolderManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.content_template = json.loads(CONTENT_TEMPLATE_JSON)

    def create_main_folder(self, folder_name=None):
        """
        Create the main project folder
        If folder_name is provided, use it; otherwise generate a unique name
        """
        if not folder_name:
            # Generate a unique folder name if none provided
            folder_name = f"PROJECT_{str(uuid.uuid4())[:8].upper()}"

        folder_path = os.path.join(self.base_dir, folder_name.upper())

        # Create folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Đã tạo folder {folder_name}.")
        else:
            print(f"Folder {folder_name} đã tồn tại.")

        return folder_path

    def create_childs_folder(self, base_path, structure):
        """Create child folders and files based on template structure"""
        if not base_path:
            return False

        # Recursively create the folder structure
        for key, value in structure.items():
            if key == "config":
                # Handle special config file
                file_path = os.path.join(base_path, value)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                flag = self.check_file_exist(file_path)
                if flag:
                    # Create and initialize template.json file
                    with open(file_path, "w", encoding="utf-8") as ft:
                        json.dump(self.content_template, ft, ensure_ascii=False, indent=4)
                    print(f"Đã tạo file cấu hình: {file_path}")
            else:
                # Create folder
                folder_path = os.path.join(base_path, key)
                os.makedirs(folder_path, exist_ok=True)
                print(f"Đã tạo thư mục: {folder_path}")

                # Handle sub-items (files or folders)
                if isinstance(value, dict):
                    # Recursive create sub-folders
                    self.create_childs_folder(folder_path, value)
                elif isinstance(value, list):
                    # Create empty files
                    for file in value:
                        file_path = os.path.join(folder_path, file)
                        flag = self.check_file_exist(file_path)
                        if flag:
                            # Create parent directories if needed
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            # Create the empty file
                            open(file_path, "w").close()
                            print(f"Đã tạo file: {file_path}")
        return True

    def check_file_exist(self, file_path):
        flag_content = True
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    flag_content = False

        return flag_content

    def create_css_files(self, output_folder, content):
        save_path = os.path.join(output_folder, 'css')
        os.makedirs(save_path, exist_ok=True)
        css_links = [link.get("href") for link in content.find_all("link", rel="stylesheet") if link.get("href")]
        parsed_base_url = urlparse(self.base_dir)
        base_url = 'https'
        if parsed_base_url.scheme:
            base_url = parsed_base_url.scheme

        for css_link in css_links:
            if css_link.startswith("//"):
                css_url = base_url + ':' + css_link
            else:
                css_url = urljoin(base_url, css_link)
            css_name = os.path.basename(urlparse(css_url).path)

            try:
                response = requests.get(css_url)
                response.raise_for_status()
                with open(os.path.join(save_path, css_name), "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"Đã tải CSS: {css_name}")

            except requests.RequestException:
                print(f"Lỗi tải CSS: {css_url}")

    def save_file(self, file_path, content):
        if content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(content.prettify(formatter=None)))