from fastapi import APIRouter, HTTPException
import platform
import subprocess
from pydantic import BaseModel

from agents.category_page import CategoryPage
from agents.home_page import HomePage
from agents.menu_part import MenuPart
from agents.product_detail_page import ProductDetailPage

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
    responses={404: {"description": "Not found"}},
)


class BaseAgent:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def clear_screen(self):
        """Clear the terminal screen based on the operating system."""
        if platform.system() == "Windows":
            subprocess.call('cls', shell=True)
        else:  # For Linux and MacOS
            subprocess.call('clear', shell=True)