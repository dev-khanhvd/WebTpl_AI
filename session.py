"""
File dùng để lưu trạng thái session hiện tại:
- current_base_dir: thư mục gốc
- current_folder_path: thư mục chứa dữ liệu crawl

Các module khác chỉ cần import từ đây:
    from session import current_base_dir, current_folder_path
"""

current_base_dir: str = None
current_folder_path: str = None

def set_session(base_dir: str, folder_path: str):
    global current_base_dir, current_folder_path
    current_base_dir = base_dir
    current_folder_path = folder_path

def clear_session():
    global current_base_dir, current_folder_path
    current_base_dir = None
    current_folder_path = None


def normalize_github_path(file_path):
    return file_path.replace('\\', '/').lstrip('/')

