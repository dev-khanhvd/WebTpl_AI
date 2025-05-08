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
    prefix="/agent/product-detail",
    tags=["agent"],
    responses={404: {"description": "Not found"}},
)


class ProductDetailRequest(BaseModel):
    folder_name: str = None
    menu_choice: int
    wrapper_classes: str
    item_classes: str = None
    options: Optional[Dict[str, Union[str, int]]] = None


@router.post("/")
async def product_detail_options():
    """Returns available options for the product detail page agent"""
    options = [
        {'id': 1, 'name': 'Ảnh sản phẩm'},
        {'id': 2, 'name': 'Thuộc tính màu sắc'},
        {'id': 3, 'name': 'Thuộc tính kích cỡ'},
        {'id': 4, 'name': 'Sản phẩm liên quan'},
        {'id': 5, 'name': 'Sản phẩm cùng danh mục'},
        {'id': 6, 'name': 'Sản phẩm đã xem'},
    ]

    return {"status": "success", "options": options}


@router.post("/process")
async def process_product_detail(request: ProductDetailRequest):
    """Process the product detail page with the selected option"""

    if request.menu_choice < 1 or request.menu_choice > 6:
        raise HTTPException(status_code=400, detail="Invalid menu choice")

    if not request.wrapper_classes:
        raise HTTPException(status_code=400, detail="wrapper_classes is required")

    folder_name = current_folder_path
    if request.folder_name:
        folder_name = request.folder_name
    product_detail = ProductDetailPage(folder_name)

    if not product_detail.base_dir:
        raise HTTPException(status_code=400, detail="base_dir is required")

    try:
        if request.menu_choice in [2, 3] and (not request.item_classes or len(request.item_classes) < 1):
            raise HTTPException(status_code=400, detail="item_classes is required for menu choices 2 and 3")

        result = product_detail.get_product_page_content(
            request.wrapper_classes,
            request.menu_choice,
            request.item_classes,
            request.options,
        )

        return {"status": "success", "message": f"Processed product detail option {request.menu_choice}",
                "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


class ProductDetailPage:
    def __init__(self, base_dir, base_branch=BASE_BRANCH):
        self.base_dir = base_dir
        self.template_mapping = json.loads(PAGE_TYPE_MAPPING)
        self.file_path = normalize_github_path(self.base_dir + "/" + self.template_mapping['product'])

        self.github_token = GITHUB_ACCESS_TOKEN
        self.github_repo_name = GITHUB_REPO_FULLNAME
        self.base_branch = base_branch
        self.github = Github(self.github_token)
        self.repo = self.github.get_repo(self.github_repo_name)

    def get_product_page_content(self, wrapper_classes, choice_selected, item_classes=None, options=None):
        """Process the product detail page content based on the selected option"""

        if not self.base_dir:
            return {"success": False, "message": "Base directory not provided"}

        try:
            file_content = self.repo.get_contents(self.file_path, ref=self.base_branch)
            template_content = file_content.decoded_content.decode('utf-8')
            if not template_content:
                return {"success": False, "message": "Template content not found"}

            match choice_selected:
                case 1:
                    question = "Danh sách ảnh sản phẩm sẽ lấy ra tất cả ảnh của sản phẩm"
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'product_images_block')
                case 2:
                    question = "Lấy thuộc tính màu sắc của sản phẩm lên website"
                    result = self.detect_block_attrs(template_content, wrapper_classes, item_classes, question,
                                                     'product_color_attr_block')
                case 3:
                    question = "Cho phép người dùng lựa chọn kích cỡ phù hợp"
                    result = self.detect_block_attrs(template_content, wrapper_classes, item_classes, question,
                                                     'product_size_attr_block')
                case 4:
                    question = "Lấy ra những sản phẩm upSale của sản phẩm hiện tại"
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'product_upsale_block', options)
                case 5:
                    question = "Sản phẩm cùng danh mục"
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'product_category_related_block', options)
                case 6:
                    question = "Sản phẩm đã xem"
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'product_history_block', options)
                case _:
                    return {"success": False, "message": "Invalid choice selected"}

            return result or {"success": True, "message": "Processing completed"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def detect_block_fill_code(self, template_content, wrapper_classes, question, type=None, options=None):
        """Detect and fill code for blocks in product detail page"""
        detect = DetectHtml(self.base_dir)
        index_name = "product_detail_tranning"
        content_soup = detect.detect_position_html(wrapper_classes, template_content, question, type, options,
                                                   index_name)

        if content_soup:
            object_file = FolderManager(self.base_dir)
            save_result = object_file.save_file(self.file_path, content_soup)
            return {"success": True, "message": "Content detected and saved", "content_info": str(save_result)}
        return {"success": False, "message": "No content detected"}

    def detect_block_attrs(self, template_content, main_wrapper, attrs_item_wrapper, question, type=None):
        """Detect and fill attribute blocks in product detail page"""
        detect = DetectHtml(self.base_dir)
        attrs_block = detect.detect_position_product_details_attributes_section(main_wrapper, attrs_item_wrapper, template_content,
                                                                        question, type)
        if attrs_block:
            object_file = FolderManager(self.base_dir)
            save_result = object_file.save_file(self.file_path, attrs_block)
            return {"success": True, "message": "Attribute block detected and saved", "content_info": str(save_result)}
        return {"success": False, "message": "No attribute block detected"}