from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict
import json

from website_cloner.page_manager import fetch_all_pages
from website_cloner.folder_manager import FolderManager
from utils.embedding import Embedding
from config import BASE_DIR, FOLDER_STRUCTURE
from website_cloner.website_rule.haravan_rule import HaravanRule
from website_cloner.website_rule.sapo_rule import SapoRule
from session import set_session

# Import the routers from the agent modules
from agents.base_agent import router as base_agent_router
from agents.home_page import router as home_page_router
from agents.category_page import router as category_page_router
from agents.menu_part import router as menu_part_router
from agents.product_detail_page import router as product_detail_router
from agents.cart_page import router as cart_page_router
from agents.checkout_page import router as checkout_page_router
from agents.order_page import router as order_page_router
from agents.album_page import router as album_page_router
from agents.news_page import router as news_page_router
app = FastAPI(
    title="Website Cloner API",
    description="API for cloning websites, filling code logic, and updating training data",
    version="1.0.0"
)


# Storage for active jobs and their status
active_jobs = {}

app.include_router(base_agent_router)
app.include_router(home_page_router)
app.include_router(category_page_router)
app.include_router(menu_part_router)
app.include_router(product_detail_router)
app.include_router(cart_page_router)
app.include_router(checkout_page_router)
app.include_router(order_page_router)
app.include_router(album_page_router)
app.include_router(news_page_router)

class CrawlRequest(BaseModel):
    folder_name: str
    url: str
    rule_type: str  # "haravan" or "sapo"


class AgentRequest(BaseModel):
    folder_path: str


class CrawlResponse(BaseModel):
    job_id: str
    status: str
    folder_path: Optional[str] = None
    message: str

@app.get("/")
async def root():
    return {"message": "Welcome to Website Cloner API"}


@app.post("/crawl", response_model=CrawlResponse)
async def crawl_website(request: CrawlRequest, background_tasks: BackgroundTasks):
    # Generate a job ID
    import uuid

    job_id = str(uuid.uuid4())

    base_dir = BASE_DIR

    # Create folder structure
    folder_manager = FolderManager(base_dir)
    folder_path = folder_manager.create_main_folder(request.folder_name)

    if not folder_path:
        raise HTTPException(status_code=400, detail="Folder deleted or not found")

    set_session(base_dir, folder_path)

    # Create folder structure based on template
    template_structure = json.loads(FOLDER_STRUCTURE)
    folder_manager.create_childs_folder(folder_path, template_structure)

    # Set up rule based on request
    if request.rule_type.lower() == "haravan":
        rule = HaravanRule()
        page_rules = rule.get_rules()
    elif request.rule_type.lower() == "sapo":
        rule = SapoRule()
        page_rules = rule.sapo_types
    else:
        raise HTTPException(status_code=400, detail="Invalid rule type. Must be 'haravan' or 'sapo'")

    # Initialize job status
    active_jobs[job_id] = {
        "status": "started",
        "base_dir": base_dir,
        "folder_path": folder_path,
        "folder_name": request.folder_name,
        "url": request.url,
        "rule_type": request.rule_type
    }
    # Start crawling in background
    await crawl_website_task(
        job_id=job_id,
        url=request.url,
        folder_name=request.folder_name,
        page_rules=page_rules
    )

    return CrawlResponse(
        job_id=job_id,
        status=active_jobs[job_id]["status"],
        folder_path=folder_path,
        message=active_jobs[job_id].get("message", "Crawling finished.")
    )


async def crawl_website_task(job_id: str, url: str, folder_name: str, page_rules: Dict):

    try:
        active_jobs[job_id]["status"] = "running"

        # Start crawling
        await fetch_all_pages(url, folder_name, page_rules)

        # Update RFSjob status
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["message"] = f"Successfully crawled website: {url}"
    except Exception as e:
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["message"] = f"Error crawling website: {str(e)}"

@app.post("/update-embeddings")
async def update_embeddings():
    auto_embedding = Embedding(BASE_DIR)
    auto_embedding.save_embeddings()

    return {"status": "started", "message": "Started updating embeddings"}



if __name__ == "__main__":
    import uvicorn

    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, host="127.0.0.1", port=8000)