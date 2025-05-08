import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, Union

from config import PAGE_TYPE_MAPPING, GITHUB_ACCESS_TOKEN, GITHUB_REPO_FULLNAME, BASE_BRANCH
from github import Github
from utils.detect_html import DetectHtml
from website_cloner.folder_manager import FolderManager

from session import current_folder_path, normalize_github_path

router = APIRouter(
    prefix="/agent/home-page",
    tags=["agent"],
    responses={404: {"description": "Not found"}},
)


class HomePageRequest(BaseModel):
    folder_name: str = None
    menu_choice: int
    wrapper_classes: str
    item_classes: str = None
    options: Optional[Dict[str, Union[str, int]]] = None


class HomePageProductTypeRequest(BaseModel):
    folder_name: str
    wrapper_classes: str
    options: Optional[Dict[str, Union[str, int]]] = None


@router.post("/")
async def home_page_options():
    """Returns available options for the home page agent"""
    options = [
        {'id': 1, 'name': 'Banner không giới hạn số lượng'},
        {'id': 2, 'name': 'Banner giới hạn số lượng'},
        {'id': 3, 'name': 'Sản phẩm trang chủ'},
        {'id': 4, 'name': 'Sản phẩm theo CTKM (Nhập wrapper CTKM + Wrapper danh sách sản phẩm)'},
        {'id': 5, 'name': 'Danh sách bài viết tin tức'},
        {'id': 6, 'name': 'Danh sách bài viết album'},
        {'id': 7, 'name': 'Danh thương hiệu'},
        {'id': 8, 'name': 'Danh mục sản phẩm'},
        {'id': 9, 'name': 'Danh sách mã voucher'},
    ]

    return {"status": "success", "options": options}


@router.post("/product-types")
async def product_type_options():
    """Returns available product type options"""
    product_options = [
        {'id': 1, 'name': 'Sản phẩm tick hot', 'value': 'showHot'},
        {'id': 2, 'name': 'Sản phẩm tick trang chủ', 'value': 'showHome'},
        {'id': 3, 'name': 'Sản phẩm tick mới', 'value': 'showNew'},
    ]

    return {"status": "success", "options": product_options}


@router.post("/process")
async def process_home_page(request: HomePageRequest):
    """Process the home page with the selected option"""

    if request.menu_choice < 1 or request.menu_choice > 9:
        raise HTTPException(status_code=400, detail="Invalid menu choice")

    if not request.wrapper_classes:
        raise HTTPException(status_code=400, detail="wrapper_classes is required")

    folder_name = current_folder_path
    if request.folder_name:
        folder_name = request.folder_name
    home_page = HomePage(folder_name)

    if not home_page.base_dir:
        raise HTTPException(status_code=400, detail="base_dir is required")

    try:
        if request.menu_choice == 4 and (not request.item_classes or len(request.item_classes) < 1):
            raise HTTPException(status_code=400, detail="item_classes is required for menu choice 4")

        result = home_page.get_home_page_content(
            request.wrapper_classes,
            request.menu_choice,
            request.item_classes,
            request.options,
        )

        return {"status": "success", "message": f"Processed home page option {request.menu_choice}", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.post("/product")
async def process_home_products(request: HomePageProductTypeRequest):
    """Process the home page products with the selected product type"""

    if not request.wrapper_classes:
        raise HTTPException(status_code=400, detail="wrapper_classes is required")

    folder_name = current_folder_path
    if request.folder_name:
        folder_name = request.folder_name
    home_page = HomePage(folder_name)

    if not home_page.base_dir:
        raise HTTPException(status_code=400, detail="base_dir is required")

    try:
        menu_choice = 3  # Corresponding to products
        result = home_page.get_home_page_content(
            request.wrapper_classes,
            menu_choice,
            None,
                request.options
        )

        return {"status": "success", "message": f"Processed home page products", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


class HomePage:
    def __init__(self, base_dir , base_branch=BASE_BRANCH):
        self.base_dir = base_dir
        self.template_mapping = json.loads(PAGE_TYPE_MAPPING)
        self.file_path = normalize_github_path(self.base_dir + "/" + self.template_mapping['homepage'])

        self.github_token = GITHUB_ACCESS_TOKEN
        self.github_repo_name = GITHUB_REPO_FULLNAME
        self.base_branch = base_branch
        self.github = Github(self.github_token)
        self.repo = self.github.get_repo(self.github_repo_name)

    def get_home_page_content(self, wrapper_classes, choice_selected, item_classes=None, options=None):

        if not self.base_dir:
            return {"success": False, "message": "Base directory not provided"}
        try:
            file_content = self.repo.get_contents(self.file_path, ref=self.base_branch)
            template_content = file_content.decoded_content.decode('utf-8')
            if not template_content:
                return {"success": False, "message": "Base directory not provided"}
            match choice_selected:
                case 1:
                    question = "Banner website có thể hiểu là những ô vuông trên đó có slogan"
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'banner_block')
                case 2:
                    question = "Banner giới hạn số lượng trang chủ"
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'banner_block',
                                                         options)
                case 3:
                    question = "Có 3 dạng tick để hiển thị sản phẩm trên trang chủ: tick trang chủ, tick mới hoặc tick hot"
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'home_products_list_block', options)
                case 4:
                    question = 'Chương trình khuyến mãi và có đếm ngược theo ID của chương trình khuyến mãi đang chạy'
                    result = self.detect_block_promotion(template_content, wrapper_classes, item_classes, question)
                case 5:
                    question = 'Lấy ra danh sách các bài viết tin tức để hiển thị trên website'
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'home_article_news',
                                                         options)
                case 6:
                    question = 'Bộ sưu tập album ảnh'
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question, 'home_album',
                                                         options)
                case 7:
                    question = 'Danh sách thương hiệu'
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question, 'home_brands',
                                                         options)
                case 8:
                    question = 'Giúp người dùng dễ dàng chọn đúng nhóm sản phẩm họ quan tâm'
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'home_product_category')
                case 9:
                    question = 'Danh sách mã voucher'
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'home_voucher_list')
                case _:
                    return {"success": False, "message": "Invalid choice selected"}

            return result or {"success": True, "message": "Processing completed"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def detect_block_fill_code(self, template_content, wrapper_classes, question, type=None, options=None):
        detect = DetectHtml(self.base_dir)
        index_name = "home_tranning"
        content_soup = detect.detect_position_html(wrapper_classes, template_content, question, type, options, index_name)
        if content_soup:
            object_file = FolderManager(self.base_dir)
            save_result = object_file.save_file(self.file_path, content_soup)
            return {"success": True, "message": "Content detected and saved", "content_info": str(save_result)}
        return {"success": False, "message": "No content detected"}

    def detect_block_promotion(self, template_content, main_wrapper, product_wrapper, question):
        detect = DetectHtml(self.base_dir)
        promotion_block = detect.detect_position_home_promotion_section(main_wrapper, product_wrapper, template_content,
                                                                        question, 'home_promotion_details')
        if promotion_block:
            object_file = FolderManager(self.base_dir)
            save_result = object_file.save_file(self.base_dir, promotion_block)
            return {"success": True, "message": "Promotion block detected and saved", "content_info": str(save_result)}
        return {"success": False, "message": "No promotion block detected"}