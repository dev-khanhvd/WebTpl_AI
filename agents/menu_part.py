import json
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, Union

from config import PAGE_TYPE_MAPPING, GITHUB_ACCESS_TOKEN, GITHUB_REPO_FULLNAME, BASE_BRANCH
from github import Github
from bs4 import BeautifulSoup
from utils.embedding import Embedding

from session import current_folder_path, normalize_github_path

router = APIRouter(
    prefix="/agent/menu-part",
    tags=["agent"],
    responses={404: {"description": "Not found"}},
)


class MenuPartRequest(BaseModel):
    folder_name: str = None
    menu_area: str  # homepage, header, footer
    wrapper_selector: str
    options: Optional[Dict[str, Union[str, int]]] = None


@router.post("/")
async def menu_part_options():
    """Returns available options for the menu part agent"""
    options = [
        {'id': 'homepage', 'name': 'Homepage Menu'},
        {'id': 'header', 'name': 'Header Menu'},
        {'id': 'footer', 'name': 'Footer Menu'},
    ]

    return {"status": "success", "options": options}


@router.post("/process")
async def process_menu_part(request: MenuPartRequest):
    """Process the menu part with the selected option"""

    if not request.menu_area or not request.wrapper_selector:
        raise HTTPException(status_code=400, detail="menu_area and wrapper_selector are required")

    folder_name = current_folder_path
    if request.folder_name:
        folder_name = request.folder_name
    menu_part = MenuPart(folder_name)

    try:
        result = menu_part.extract_menu(request.menu_area, request.wrapper_selector, request.options)
        return {"status": "success", "message": f"Processed menu for {request.menu_area}", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


class MenuPart:
    def __init__(self, base_dir, base_branch=BASE_BRANCH):
        self.base_dir = base_dir
        self.template_mapping = json.loads(PAGE_TYPE_MAPPING)

        self.github_token = GITHUB_ACCESS_TOKEN
        self.github_repo_name = GITHUB_REPO_FULLNAME
        self.base_branch = base_branch
        self.github = Github(self.github_token)
        self.repo = self.github.get_repo(self.github_repo_name)

    def extract_menu(self, menu_area, wrapper_selector, options=None):
        """Extract menu from the specified area and apply transformations"""

        if not self.base_dir:
            return {"success": False, "message": "Base directory not provided"}

        try:
            # Get the file path based on the selected menu area
            file_path = normalize_github_path(self.base_dir + "/" + self.template_mapping.get(menu_area, ""))

            # Get content from GitHub
            file_content = self.repo.get_contents(file_path, ref=self.base_branch)
            template_content = file_content.decoded_content.decode('utf-8')

            if not template_content:
                return {"success": False, "message": "Template content not found"}

            # Process the menu
            result = self.process_menu(template_content, wrapper_selector, file_path, 'home_tranning')
            return result or {"success": True, "message": "Processing completed"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def process_menu(self, html, wrapper_selector, file_path, index_name=None):
        """Process the menu HTML and create menu files"""
        potential_parents = []
        soup = BeautifulSoup(html, "html.parser")

        # Find elements by ID or class that match the wrapper selector
        elements = soup.find_all(id=re.compile(wrapper_selector))
        if not elements:
            elements = soup.find_all(class_=re.compile(wrapper_selector))

        if elements:
            potential_parents.extend(elements)

        if not potential_parents:
            return {"success": False, "message": "No menu wrapper found"}

        parent_wrapper = potential_parents[0]

        # Process all UL elements in the wrapper
        for ul in parent_wrapper.find_all("ul"):
            self.filter_ul(ul)

        # Create embedding instance
        embedding = Embedding(self.base_dir)

        # Process product category menu
        menu_html1 = str(parent_wrapper)
        menu_file_path1 = normalize_github_path(self.base_dir + "/" + self.template_mapping.get('menu', ""))
        # question1 = 'Danh mục sản phẩm'
        question1 = 'Danh mục tự tạo'
        menu_result_1 = embedding.process_question(question1, 'home_menu_product_category', menu_html1,None, index_name)

        #Save the product category menu file
        menu_file1 = self.repo.get_contents(menu_file_path1, ref=self.base_branch)
        self.repo.update_file(
            menu_file_path1,
            "Update product category menu",
            menu_result_1,
            menu_file1.sha,
            branch=self.base_branch
        )

        # Process custom menu
        menu_html2 = str(parent_wrapper)
        menu_file_path2 = normalize_github_path(self.base_dir + "/" + self.template_mapping.get('menu_custom', ""))
        question2 = 'Danh mục tự tạo'
        menu_result_2 = embedding.process_question(question2, 'home_menu_product_category', menu_html2,None, index_name)

        # Save the custom menu file
        menu_file2 = self.repo.get_contents(menu_file_path2, ref=self.base_branch)
        self.repo.update_file(
            menu_file_path2,
            "Update custom menu",
            menu_result_2,
            menu_file2.sha,
            branch=self.base_branch
        )

        # Replace the original menu with a Twig include statement
        twig_code = """
        {% if(menuIsExisted({'type': 'header' })) %}
            {% include 'other/menu_custom' %}
        {% else %}
            {% include 'other/menu' %}
        {% endif %}
        """.strip()

        parent_wrapper.replace_with(soup.new_string(twig_code))

        # Update the original file
        file_content = self.repo.get_contents(file_path, ref=self.base_branch)
        self.repo.update_file(
            file_path,
            "Update menu include",
            str(soup.prettify()),
            file_content.sha,
            branch=self.base_branch
        )

        return {
            "success": True,
            "message": "Menu processed successfully",
            "details": {
                "product_menu_path": menu_file_path1,
                "custom_menu_path": menu_file_path2,
                "original_file_updated": file_path
            }
        }

    def filter_ul(self, ul_tag):
        if not ul_tag:
            return

        lis = ul_tag.find_all("li", recursive=False)

        kept_li = None
        for li in lis:
            has_sub_ul = li.find("ul", recursive=False)
            if has_sub_ul:
                kept_li = li
                break

        if not kept_li and lis:
            kept_li = lis[0]  # Giữ li đầu tiên nếu không có ul con

        for li in lis:
            if li != kept_li:
                li.decompose()
        # Đệ quy tiếp nếu kept_li có ul con
        if kept_li:
            sub_uls = kept_li.find_all("ul", recursive=False)
            for sub_ul in sub_uls:
                self.filter_ul(sub_ul)