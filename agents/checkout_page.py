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
    prefix="/agent/checkout-page",
    tags=["agent"],
    responses={404: {"description": "Not found"}},
)


class CheckoutRequest(BaseModel):
    folder_name: str = None
    menu_choice: int
    wrapper_classes: str
    item_classes: str = None
    options: Optional[Dict[str, Union[str, int]]] = None

@router.post("/")
async def checkout_page_options():
    """Returns available options for the category page agent"""
    options = [
        {'id': 1, 'name': 'Sản phẩm trong giỏ hàng'}
    ]

    return {"status": "success", "options": options}

@router.post("/process")
async def process_checkout_menu(request: CheckoutRequest):
    """Process the checkout page with the selected option"""

    if request.menu_choice < 1 or request.menu_choice > 5:
        raise HTTPException(status_code=400, detail="Invalid menu choice")

    if not request.wrapper_classes:
        raise HTTPException(status_code=400, detail="wrapper_classes is required")

    folder_name = current_folder_path
    if request.folder_name:
        folder_name = request.folder_name
    checkout_page = CheckoutPage(folder_name)

    if not checkout_page.base_dir:
        raise HTTPException(status_code=400, detail="base_dir is required")

    try:
        wrapper_classes = [cls.strip() for cls in request.wrapper_classes.split(',')]
        item_classes = None
        if request.item_classes:
            item_classes = [cls.strip() for cls in request.item_classes.split(',')]

        result = checkout_page.get_checkout_page_content(
            wrapper_classes,
            request.menu_choice,
            item_classes,
            request.options,
        )

        return {"status": "success", "message": f"Processed checkout page option {request.menu_choice}",
                "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


class CheckoutPage:
    def __init__(self, base_dir, base_branch=BASE_BRANCH):
        self.base_dir = base_dir
        self.template_mapping = json.loads(PAGE_TYPE_MAPPING)
        self.file_path = normalize_github_path(
            self.base_dir + "/" + self.template_mapping['order_checkout'])

        self.github_token = GITHUB_ACCESS_TOKEN
        self.github_repo_name = GITHUB_REPO_FULLNAME
        self.base_branch = base_branch
        self.github = Github(self.github_token)
        self.repo = self.github.get_repo(self.github_repo_name)

    def get_checkout_page_content(self, wrapper_classes: str, choice_selected: int,item_classes=None,options=None):
        if not self.base_dir:
            return {"success": False, "message": "Base directory not provided"}

        try:
            file_content = self.repo.get_contents(self.file_path, ref=self.base_branch)
            template_content = file_content.decoded_content.decode('utf-8')

            if not template_content:
                return {"success": False, "message": "Template content is empty"}

            match choice_selected:
                case 1:
                    question = "Danh sách sản phẩm trang thanh toán"
                    result = self.detect_block_fill_code(template_content, wrapper_classes, question,
                                                         'cart_product_block')

                case _:
                    return {"success": False, "message": "Invalid choice selected"}

            return result or {"success": True, "message": "Processing completed"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}


    def detect_block_fill_code(self, template_content, wrapper_classes: str, question: str, type=None,
                               options=None):
        detect = DetectHtml(self.base_dir)
        index_name = "order_trainning"
        content_soup = detect.detect_position_html(wrapper_classes, template_content, question, type, options,
                                                   index_name)

        if content_soup:
            object_file = FolderManager(self.base_dir)
            save_result = object_file.save_file(self.file_path, content_soup)
            return {"success": True, "message": "Content detected and saved", "content_info": str(save_result)}
        return {"success": False, "message": "No content detected"}
