import json
import base64
from github import Github
from config import CONTENT_TEMPLATE_JSON, GITHUB_ACCESS_TOKEN, GITHUB_REPO_FULLNAME, BASE_BRANCH
import requests
from urllib.parse import urlparse, urljoin
import uuid


class FolderManager:
    def __init__(self, base_branch=BASE_BRANCH):

        self.g = Github(GITHUB_ACCESS_TOKEN)
        self.repo = self.g.get_repo(GITHUB_REPO_FULLNAME)
        self.base_branch = base_branch
        self.content_template = json.loads(CONTENT_TEMPLATE_JSON)

        try:
            self.repo.get_branch(base_branch)
        except Exception:
            self.base_branch = self.repo.default_branch
            print(f"Using default branch: {self.base_branch}")

    def create_main_folder(self, folder_name=None, remove_folder=False):
        """
        Create the main project folder
        If folder_name is provided, use it; otherwise generate a unique name
        """
        if not folder_name:
            # Generate a unique folder name if none provided
            folder_name = f"PROJECT_{str(uuid.uuid4())[:8].upper()}"

        folder_path = folder_name.upper()

        if remove_folder:
            return self.delete_directory(folder_path)

        # Check if folder exists in repo
        try:
            self.repo.get_contents(folder_path)
            print(f"Folder {folder_name} đã tồn tại.")

        except Exception:
            # Create an empty file to create the folder
            self.repo.create_file(
                f"{folder_path}/.gitkeep",
                f"Create project folder {folder_name}",
                "",
                branch=self.base_branch
            )
            print(f"Đã tạo folder {folder_name}.")

        return folder_path

    def create_childs_folder(self, base_path, structure):
        """Create child folders and files based on template structure in GitHub repo"""
        if not base_path:
            return False

        # Recursively create the folder structure
        for key, value in structure.items():
            if key == "config":
                # Handle special config file
                file_path = f"{base_path}/{value}"

                flag = self.check_file_exist(file_path)
                if flag:
                    # Create and initialize template.json file
                    config_content = json.dumps(self.content_template, ensure_ascii=False, indent=4)
                    try:
                        self.repo.create_file(
                            file_path,
                            f"Create config file at {file_path}",
                            config_content,
                            branch=self.base_branch
                        )
                        print(f"Đã tạo file cấu hình: {file_path}")
                    except Exception as e:
                        print(f"Error creating config file: {e}")
            else:
                # Create folder
                folder_path = f"{base_path}/{key}"

                # Create folder by adding a .gitkeep file
                try:
                    self.repo.create_file(
                        f"{folder_path}/.gitkeep",
                        f"Create folder {key} in {base_path}",
                        "",
                        branch=self.base_branch
                    )
                    print(f"Đã tạo thư mục: {folder_path}")
                except Exception:
                    # Folder might already exist
                    pass

                # Handle sub-items (files or folders)
                if isinstance(value, dict):
                    # Recursive create sub-folders
                    self.create_childs_folder(folder_path, value)
                elif isinstance(value, list):
                    # Create empty files
                    for file in value:
                        file_path = f"{folder_path}/{file}"
                        flag = self.check_file_exist(file_path)
                        if flag:
                            try:
                                self.repo.create_file(
                                    file_path,
                                    f"Create file {file} in {folder_path}",
                                    "",
                                    branch=self.base_branch
                                )
                                print(f"Đã tạo file: {file_path}")
                            except Exception as e:
                                print(f"Error creating file {file_path}: {e}")
        return True

    def check_file_exist(self, file_path):
        """
        Check if a file exists and has content in GitHub repo
        Returns True if file doesn't exist or is empty
        """
        try:
            content = self.repo.get_contents(file_path, ref=self.base_branch)
            # Check if file exists but is empty
            decoded_content = base64.b64decode(content.content).decode('utf-8').strip()
            return not bool(decoded_content)  # Return True if content is empty
        except Exception:
            return True

    def create_css_files(self, output_folder, content):
        """Download and save CSS files from a webpage to GitHub repo"""
        save_path = f"{output_folder}/css"

        # Create CSS folder
        try:
            self.repo.create_file(
                f"{save_path}/.gitkeep",
                f"Create CSS folder in {output_folder}",
                "",
                branch=self.base_branch
            )
        except Exception:
            # Folder might already exist
            pass

        css_links = [link.get("href") for link in content.find_all("link", rel="stylesheet") if link.get("href")]
        parsed_base_url = urlparse(self.repo.html_url)
        base_url = 'https'
        if parsed_base_url.scheme:
            base_url = parsed_base_url.scheme

        for css_link in css_links:
            if css_link.startswith("//"):
                css_url = base_url + ':' + css_link
            elif css_link.startswith('http'):
                css_url = css_link
            else:
                css_url = urljoin(base_url, css_link)

            css_name = urlparse(css_url).path.split('/')[-1]

            if not css_name:
                continue
            try:
                response = requests.get(css_url)
                response.raise_for_status()

                file_path = f"{save_path}/{css_name}"
                try:
                    contents = self.repo.get_contents(file_path, ref=self.base_branch)
                    # File exists, so update it
                    self.repo.update_file(
                        contents.path,
                        f"Update CSS file: {css_name}",
                        response.text,
                        contents.sha,
                        branch=self.base_branch
                    )
                    print(f"Updated CSS: {css_name}")
                except Exception:
                    self.repo.create_file(
                        file_path,
                        f"Add CSS file: {css_name}",
                        response.text,
                        branch=self.base_branch
                    )
                    print(f"Added CSS: {css_name}")

            except requests.RequestException:
                print(f"Lỗi tải CSS: {css_url}")
            except Exception as e:
                print(f"Error creating CSS file: {e}")

    def save_file(self, file_path, content):
        """Save content to a file in GitHub repo"""
        if content:
            try:
                self.repo.create_file(
                    file_path,
                    f"Create file at {file_path}",
                    str(content.prettify(formatter=None)),
                    branch=self.base_branch
                )
            except Exception as e:
                # File might already exist, try to update it
                try:
                    contents = self.repo.get_contents(file_path, ref=self.base_branch)
                    self.repo.update_file(
                        contents.path,
                        f"Update file at {file_path}",
                        str(content.prettify(formatter=None)),
                        contents.sha,
                        branch=self.base_branch
                    )
                except Exception as e:
                    print(f"Error saving file {file_path}: {e}")