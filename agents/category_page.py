import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Union, Any

from config import PAGE_TYPE_MAPPING, GITHUB_ACCESS_TOKEN, GITHUB_REPO_FULLNAME, BASE_BRANCH
from github import Github
from utils.detect_html import DetectHtml
from website_cloner.folder_manager import FolderManager

from session import current_folder_path, normalize_github_path

router = APIRouter(
    prefix="/agent/category-page",
    tags=["agent"],
    responses={404: {"description": "Not found"}},
)


class CategoryPageRequest(BaseModel):
    folder_name: str = None
    menu_choice: int
    wrapper_classes: str
    item_classes: str = None
    options: Optional[Dict[str, Union[str, int]]] = None


class AttributesFilterRequest(BaseModel):
    folder_name: str = None
    wrapper_classes: str
    item_classes: str
    options: Optional[Dict[str, Union[str, int]]] = None


class FilterRequest(BaseModel):
    folder_name: str = None
    wrapper_classes: str
    options: Optional[Dict[str, Union[str, int]]] = None


@router.post("/")
async def category_page_options():
    """Returns available options for the category page agent"""
    options = [
        {'id': 1, 'name': 'Bộ lọc danh mục sản phẩm'},
        {'id': 2, 'name': 'Bộ lọc thuộc tính'},
        {'id': 3, 'name': 'Bộ lọc giá sản phẩm'},
        {'id': 4, 'name': 'Bộ lọc thương hiệu'},
        {'id': 5, 'name': 'Danh sách sản phẩm theo phân trang'},
    ]

    return {"status": "success", "options": options}


@router.post("/process")
async def process_category_page(request: CategoryPageRequest):
    """Process the category page with the selected option"""

    if request.menu_choice < 1 or request.menu_choice > 5:
        raise HTTPException(status_code=400, detail="Invalid menu choice")

    if not request.wrapper_classes:
        raise HTTPException(status_code=400, detail="wrapper_classes is required")

    folder_name = current_folder_path
    if request.folder_name:
        folder_name = request.folder_name
    category_page = CategoryPage(folder_name)

    if not category_page.base_dir:
        raise HTTPException(status_code=400, detail="base_dir is required")

    try:
        if request.menu_choice in [2, 3] and (not request.item_classes or len(request.item_classes) < 1):
            raise HTTPException(status_code=400, detail="item_classes is required for menu choice 2 and 3")

        wrapper_classes = [cls.strip() for cls in request.wrapper_classes.split(',')]
        item_classes = None
        if request.item_classes:
            item_classes = [cls.strip() for cls in request.item_classes.split(',')]

        result = category_page.get_product_page_content(
            wrapper_classes,
            request.menu_choice,
            item_classes,
            request.options,
        )

        return {"status": "success", "message": f"Processed category page option {request.menu_choice}",
                "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.post("/category-filter")
async def category_filter(request: FilterRequest):
    """Process category filter"""
    if not request.wrapper_classes:
        raise HTTPException(status_code=400, detail="wrapper_classes is required")

    folder_name = current_folder_path
    if request.folder_name:
        folder_name = request.folder_name
    category_page = CategoryPage(folder_name)

    if not category_page.base_dir:
        raise HTTPException(status_code=400, detail="base_dir is required")

    try:
        wrapper_classes = [cls.strip() for cls in request.wrapper_classes.split(',')]
        result = category_page.get_product_page_content(
            wrapper_classes,
            1,
            None,
            request.options
        )

        return {"status": "success", "message": "Processed category filter", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.post("/attributes-filter")
async def attributes_filter(request: AttributesFilterRequest):
    """Process attributes filter"""
    if not request.wrapper_classes or not request.item_classes:
        raise HTTPException(status_code=400, detail="wrapper_classes and item_classes are required")

    folder_name = current_folder_path
    if request.folder_name:
        folder_name = request.folder_name
    category_page = CategoryPage(folder_name)

    if not category_page.base_dir:
        raise HTTPException(status_code=400, detail="base_dir is required")

    try:
        wrapper_classes = [cls.strip() for cls in request.wrapper_classes.split(',')]
        item_classes = [cls.strip() for cls in request.item_classes.split(',')]

        options = request.options or {"type": "attributes_filter_block"}
        if "type" not in options:
            options["type"] = "attributes_filter_block"

        result = category_page.get_product_page_content(
            wrapper_classes,
            2,
            item_classes,
            options
        )

        return {"status": "success", "message": "Processed attributes filter", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.post("/price-filter")
async def price_filter(request: AttributesFilterRequest):
    """Process price filter"""
    if not request.wrapper_classes or not request.item_classes:
        raise HTTPException(status_code=400, detail="wrapper_classes and item_classes are required")

    folder_name = current_folder_path
    if request.folder_name:
        folder_name = request.folder_name
    category_page = CategoryPage(folder_name)

    if not category_page.base_dir:
        raise HTTPException(status_code=400, detail="base_dir is required")

    try:
        wrapper_classes = [cls.strip() for cls in request.wrapper_classes.split(',')]
        item_classes = [cls.strip() for cls in request.item_classes.split(',')]

        options = request.options or {"type": "price_filter_block"}
        if "type" not in options:
            options["type"] = "price_filter_block"

        result = category_page.get_product_page_content(
            wrapper_classes,
            3,
            item_classes,
            options
        )

        return {"status": "success", "message": "Processed price filter", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.post("/brand-filter")
async def brand_filter(request: FilterRequest):
    """Process brand filter"""
    if not request.wrapper_classes:
        raise HTTPException(status_code=400, detail="wrapper_classes is required")

    folder_name = current_folder_path
    if request.folder_name:
        folder_name = request.folder_name
    category_page = CategoryPage(folder_name)

    if not category_page.base_dir:
        raise HTTPException(status_code=400, detail="base_dir is required")

    try:
        wrapper_classes = [cls.strip() for cls in request.wrapper_classes.split(',')]
        result = category_page.get_product_page_content(
            wrapper_classes,
            4,
            None,
            request.options
        )

        return {"status": "success", "message": "Processed brand filter", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.post("/products-list")
async def products_list(request: FilterRequest):
    """Process products list"""
    if not request.wrapper_classes:
        raise HTTPException(status_code=400, detail="wrapper_classes is required")

    folder_name = current_folder_path
    if request.folder_name:
        folder_name = request.folder_name
    category_page = CategoryPage(folder_name)

    if not category_page.base_dir:
        raise HTTPException(status_code=400, detail="base_dir is required")

    try:
        wrapper_classes = [cls.strip() for cls in request.wrapper_classes.split(',')]
        result = category_page.get_product_page_content(
            wrapper_classes,
            5,
            None,
            request.options
        )

        return {"status": "success", "message": "Processed products list", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


class CategoryPage:
    def __init__(self, base_dir, base_branch=BASE_BRANCH):
        self.base_dir = base_dir
        self.template_mapping = json.loads(PAGE_TYPE_MAPPING)
        self.file_path = normalize_github_path(self.base_dir + "/" + self.template_mapping['category']['product_category'])

        self.github_token = GITHUB_ACCESS_TOKEN
        self.github_repo_name = GITHUB_REPO_FULLNAME
        self.base_branch = base_branch
        self.github = Github(self.github_token)
        self.repo = self.github.get_repo(self.github_repo_name)

    def get_product_page_content(self, wrapper_classes: str, choice_selected: int, item_classes=None,
                                 options=None):
        if not self.base_dir:
            return {"success": False, "message": "Base directory not provided"}

        try:
            file_content = self.repo.get_contents(self.file_path, ref=self.base_branch)
            template_content = file_content.decoded_content.decode('utf-8')

            if not template_content:
                return {"success": False, "message": "Template content is empty"}

            match choice_selected:
                case 1:
                    question = "Cây danh mục sản phẩm hiển thị danh mục con của danh mục sản phẩm"
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'category_filter_block')
                case 2:
                    question = "Bộ lọc thuộc tính cho danh mục"
                    result = self.get_product_block_attrs(template_content, wrapper_classes, item_classes, question,
                                                          options)
                case 3:
                    question = "Bộ lọc giá sản phẩm"
                    result = self.get_product_block_attrs(template_content, wrapper_classes, item_classes, question,
                                                          options)
                case 4:
                    question = "Lấy ra danh sách các thương hiệu theo danh mục sản phẩm"
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'brand_filter_block', options)
                case 5:
                    question = 'Danh sách sản phẩm bao gồm tất cả các sản phẩm có thể bán'
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'category_products_list_block', options)
                case _:
                    return {"success": False, "message": "Invalid choice selected"}

            return result or {"success": True, "message": "Processing completed"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def detect_block_fill_code(self, template_content, wrapper_classes: str, question: str, type=None,
                               options=None):
        detect = DetectHtml(self.base_dir)
        index_name = "product_category_tranning"
        content_soup = detect.detect_position_html(wrapper_classes, template_content, question, type, options,
                                                   index_name)

        if content_soup:
            object_file = FolderManager(self.base_dir)
            save_result = object_file.save_file(self.file_path, content_soup)
            return {"success": True, "message": "Content detected and saved", "content_info": str(save_result)}
        return {"success": False, "message": "No content detected"}

    def get_product_block_attrs(self, template_content, main_wrapper: str, item_wrapper: str,
                                question: str, options=None):
        detect = DetectHtml(self.base_dir)

        attr_block = detect.detect_position_product_attributes_section(main_wrapper, item_wrapper, template_content,
                                                                       question, options['type'])
        if attr_block:
            object_file = FolderManager(self.base_dir)
            save_result = object_file.save_file(self.file_path, attr_block)
            return {"success": True, "message": "Attribute block detected and saved", "content_info": str(save_result)}
        return {"success": False, "message": "No attribute block detected"}