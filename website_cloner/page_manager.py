from fastapi import BackgroundTasks
from urllib.parse import urlparse, urljoin
import os
import json
import re
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from github import Github
from config import PAGE_TYPE_MAPPING, GITHUB_ACCESS_TOKEN, GITHUB_REPO_FULLNAME
from website_cloner.folder_manager import FolderManager
from session import normalize_github_path

class PageManager:
    def __init__(self, base_url, folder_name, page_rules, github_token=GITHUB_ACCESS_TOKEN,
                 github_repo_name=GITHUB_REPO_FULLNAME):
        # Ensure base URL has protocol
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'https://' + base_url

        self.base_url = base_url
        self.folder_name = folder_name  # Keep for path formatting, but won't write to disk
        self.visited_urls = set()
        self.page_types = page_rules
        self.urls_to_crawl = []
        self.type_mapping = json.loads(PAGE_TYPE_MAPPING)
        self.results = {
            'website': base_url,
            'pages': {}
        }

        # Always require GitHub configuration
        if not github_token or not github_repo_name:
            raise ValueError("GitHub token and repository name are required")

        self.github_token = github_token
        self.github_repo_name = github_repo_name
        self.github = Github(github_token)
        self.repo = self.github.get_repo(github_repo_name)

        self.folder_manager = FolderManager()
        # Flag to track if CSS has been scanned
        self.css_scanned = False

    async def fetch_page(self, session, url):
        try:
            async with session.get(url, ssl=False, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Failed to fetch {url}: Status {response.status}")
                    return None
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    async def scan_css_first(self, session, url):
        """Scan and save CSS files before processing any HTML content"""
        # Fetch the homepage content
        content = await self.fetch_page(session, url)
        if not content:
            print("Failed to fetch homepage for CSS scanning")
            return False

        # Parse the homepage content
        soup = BeautifulSoup(content, 'html.parser')

        # Extract and save CSS files directly to GitHub
        print("Scanning and saving CSS files first...")
        css_files = self.folder_manager.create_css_files(self.folder_name, soup)
        if not css_files:
            print("No CSS files found or returned.")
            return False
        # Save CSS files to GitHub
        for css_path, css_content in css_files.items():
            github_path = os.path.join(self.folder_name, css_path).replace('\\', '/')
            self.save_to_github(github_path, css_content)

        # Mark CSS as scanned
        self.css_scanned = True
        print("CSS scanning completed")
        return True

    async def process_page(self, session, url):
        # Skip if already visited
        if url in self.visited_urls:
            return

        self.visited_urls.add(url)

        # Fetch page content
        content = await self.fetch_page(session, url)
        if not content:
            return

        # Process the page
        path = urlparse(url).path
        page_type_found = False

        soup = BeautifulSoup(content, 'html.parser')
        # Extract layout components (header, footer) from every page
        self.extract_layout_components(soup)

        # Identify page type based on URL pattern
        for page_type, info in self.page_types.items():
            if 'pattern' in info and re.match(info['pattern'], path):
                self.extract_and_save_page_content(content, page_type, url)
                page_type_found = True
                info['found'] = True

        # Check if homepage
        if not page_type_found and not self.page_types['homepage']['found'] and (path == '/' or path == ''):
            self.extract_and_save_page_content(content, 'homepage', url)
            self.page_types['homepage']['found'] = True
            page_type_found = True

        # Find links to other pages
        links = self.find_links(soup, url)
        tasks = []

        for link in links:
            # Skip invalid links
            if not link or link.startswith(('#', 'javascript:', 'data:', 'mailto:', 'tel:')):
                continue

            # Make absolute URL if it's relative
            if link.startswith('/'):
                link = urljoin(self.base_url, link)

            # Skip external domains
            parsed_link = urlparse(link)
            parsed_base = urlparse(self.base_url)
            if parsed_link.netloc and parsed_link.netloc != parsed_base.netloc:
                continue

            # Skip if already visited
            if link in self.visited_urls:
                continue

            # Get the path for pattern matching
            path = parsed_link.path
            for page_type, info in self.page_types.items():
                if 'pattern' in info and not info['found'] and re.match(info['pattern'], path):
                    tasks.append(self.process_page(session, link))
                    break

            # Add to general crawl queue if not too many pages visited
            if link not in self.visited_urls and len(self.visited_urls) < 30:
                tasks.append(self.process_page(session, link))

        # Process found links
        if tasks:
            await asyncio.gather(*tasks)

    def find_links(self, soup, base_url):
        """Extract links from HTML content"""
        links = []
        for a_tag in soup.find_all('a', href=True):
            links.append(a_tag['href'])
        return links

    def extract_and_save_page_content(self, content, page_type, url):
        """Extract content from the webpage and save it to GitHub if the target file is missing or empty."""
        if page_type not in self.type_mapping:
            print(f"No mapping found for page type: {page_type}")
            return

        mapping = self.type_mapping.get(page_type)

        if isinstance(mapping, dict):
            if page_type == 'category':
                relative_path = mapping.get("product_category")
            elif page_type == 'blog':
                relative_path = mapping.get("blog_category")
            else:
                relative_path = next(iter(mapping.values()), None)
        else:
            relative_path = mapping

        if not relative_path:
            print(f"Empty mapping for page type: {page_type}")
            return
        relative_path = self.folder_name + "/" + relative_path
        # Determine index path if applicable
        index_path = None
        info = self.page_types.get(page_type, {})
        if info.get('index_file', False) and isinstance(mapping, dict):
            if page_type == 'category':
                index_path = self.folder_name + "/" + mapping.get("product_index")
            elif page_type == 'blog':
                index_path = self.folder_name + "/" + mapping.get("blog_index")

        # Parse and clean content
        soup = BeautifulSoup(content, 'html.parser')
        for script in soup.find_all('script'):
            script.extract()

        main_content = soup.body
        if not main_content:
            print("Body not found!")
            return

        for tag in main_content.find_all(["header", "footer"]):
            tag.extract()

        result = BeautifulSoup("".join(str(tag) for tag in main_content.contents), "html.parser")
        formatted_content = self.page_render_components(page_type, result)

        # Save main file to GitHub
        self.save_to_github_if_empty(relative_path, formatted_content, f"Save {page_type} content to GitHub")

        # Save index file if applicable
        if index_path:
            index_type = 'product_index' if page_type == 'category' else 'blog_index'
            formatted_index = self.page_render_components(index_type, result)
            self.save_to_github_if_empty(index_path, formatted_index, f"Save {index_type} for {page_type}")

    def save_to_github_if_empty(self, file_path, content, message):
        """Only update/create file in GitHub if file is missing or empty."""
        try:
            github_path = normalize_github_path(file_path)
            existing_file = self.repo.get_contents(github_path, ref="main")
            existing_content = existing_file.decoded_content.decode("utf-8").strip()
            if existing_content:
                print(f"File already has content, skipping: {github_path}")
                return
            # Nếu file có nhưng rỗng, gọi save_to_github để update
            self.save_to_github(github_path, content, message)
        except Exception as e:
            if '404' in str(e):
                # Nếu file chưa có, gọi save_to_github để tạo
                self.save_to_github(file_path, content, message)
            else:
                print(f"Error checking file existence on GitHub: {e}")

    def save_to_github(self, file_path, content, message=None):
        """Create or update file in GitHub repository"""
        try:
            github_path =  normalize_github_path(file_path)

            try:
                # Kiểm tra file đã tồn tại chưa
                existing_file = self.repo.get_contents(github_path, ref="main")
                self.repo.update_file(
                    path=github_path,
                    message=message,
                    content=content,
                    sha=existing_file.sha,
                    branch="main"
                )
                print(f"Updated file in GitHub: {github_path}")
            except Exception as e:
                if '404' in str(e):
                    self.repo.create_file(
                        path=github_path,
                        message=message,
                        content=content,
                        branch="main"
                    )
                    print(f"Created file in GitHub: {github_path}")
                else:
                    raise e
        except Exception as e:
            print(f"Error saving to GitHub: {e}")

    def ensure_github_directory_exists(self, directory_path):
        """Ensure all parent directories exist in the GitHub repository"""
        if not directory_path or directory_path == '.' or directory_path == '/':
            return

        # Convert to GitHub-style path and remove leading/trailing slashes
        dir_path = directory_path.replace('\\', '/')
        if dir_path.startswith('/'):
            dir_path = dir_path[1:]
        if dir_path.endswith('/'):
            dir_path = dir_path[:-1]

        # Check if this directory already exists
        try:
            self.repo.get_contents(dir_path, ref="main")
            return  # Directory exists
        except Exception:
            # Directory doesn't exist, ensure parent directory exists first
            parent_dir = os.path.dirname(dir_path)
            if parent_dir and parent_dir != '.' and parent_dir != dir_path:
                self.ensure_github_directory_exists(parent_dir)

            # Create an empty .gitkeep file to create the directory
            try:
                self.repo.create_file(
                    f"{dir_path}/.gitkeep",
                    f"Create directory: {dir_path}",
                    "",
                    branch="main"
                )
                print(f"Created directory in GitHub: {dir_path}")
            except Exception as e:
                # If error is because file already exists, that's fine
                if "already exists" not in str(e):
                    print(f"Error creating directory in GitHub: {e}")

    def page_render_components(self, page_type, content):
        page_titles = {
            "homepage": "translate('Trang chủ')",
            "search": "translate('Tìm kiếm')",
            "product_index": "translate('Danh sách sản phẩm')",
            "category": "category.name",
            "product": "product.name",
            "order_cart": "translate('Giỏ hàng')",
            "order_checkout": "translate('Thanh toán')",
            "order_search": "translate('Tra cứu đơn hàng')",
            "blog_index": "translate('Danh sách bài viết')",
            "blog": "newsCategory.name",
            "blog_article": "news.title | striptags",
            "album_index": "translate('Danh sách album')",
            "album": "albumCategory.name",
            "album_article": "album.name | striptags",
            "contact": "translate('Liên hệ')",
            "user_signin": "translate('Đăng nhập')",
            "user_signup": "translate('Đăng ký')",
            "map": "translate('Hệ thống cửa hàng')",
            "wish_list": "translate('Yêu thích')",
            "promotion_index": "translate('Chương trình khuyến mãi')",
            "promotion_list": "promotion.name",
            "landing_page": "Landing page",
        }
        page_title = page_titles.get(page_type, "Page type not recognized.")
        meta_keywords = "getKeyContentValue('META_KEYWORDS')"
        meta_description = "getKeyContentValue('META_DESCRIPTION')"
        meta_title = "getKeyContentValue('META_TITLE')"
        url = canonical_link = "getCurrentUrl()"
        image = 'getBusinessLogo()'
        variable = ''

        # Fix the tuple to string conversion issues
        if page_type == "category":
            page_title = "category.name"
            meta_keywords = "category.metaKeywords?:category.name"
            meta_description = "category.metaDescription?:category.name"
            meta_title = "category.metaTitle?:category.name"
            url = canonical_link = "category.canonicalLink"
            image = 'category.imageUri'  # Remove the comma that created a tuple
        elif page_type == "product":
            page_title = "product.name"
            meta_keywords = "product.metaKeywords?:product.name"  # Remove the comma
            meta_description = "product.metaDescription?:product.name"  # Remove the comma
            meta_title = "product.metaTitle?:product.name"  # Remove the comma
            url = canonical_link = "product.canonicalLink"
            image = 'product.imageUri'
            variable = '''  {% set wishlist = jsonDecode(getCookies('WISHLIST_STORE_PRODUCT')) %}
                            {% set ivt = 0 %}
                            {% if product.inventory().calcAvailable() > 0 %}
                                {% set ivt = product.inventory().calcAvailable() %}
                            {% elseif product.available > 0 %}
                                {% set ivt = product.available %}
                            {% endif %}
                            {% set variableAttributes = product.variableAttributes %}
                            {% set flag = 0 %}'''
        elif page_type == "blog":
            page_title = "newsCategory.name"
            meta_keywords = "newsCategory.metaKeywords?:newsCategory.name"
            meta_description = "newsCategory.metaDescription?:newsCategory.name"
            meta_title = "newsCategory.metaTitle?:newsCategory.name"
            url = canonical_link = "newsCategory.canonicalLink"
            image = 'newsCategory.imgUri'  # Remove the comma
        elif page_type == "blog_article":
            page_title = "news.title | striptags"
            meta_keywords = "news.metaKeywords?:news.name"
            meta_description = "news.metaDescription?:news.name"
            meta_title = "news.metaTitle?:news.name"
            url = canonical_link = "news.canonicalLink"
            image = 'news.pictureUri'
        elif page_type == "album":
            page_title = "albumCategory.name | striptags"
            meta_keywords = "albumCategory.metaKeywords?:albumCategory.name"
            meta_description = "albumCategory.metaDescription?:albumCategory.name"
            meta_title = "albumCategory.metaTitle?:news.name"
            url = canonical_link = "albumCategory.canonicalLink"
            image = 'albumCategory.imgUri'
        elif page_type == "album_article":  # Fixed duplicate case from blog_article to album_article
            page_title = "album.name | striptags"
            meta_keywords = "album.metaKeywords?:album.name"
            meta_description = "album.metaDescription?:album.name"
            meta_title = "album.metaTitle?:album.name"
            url = canonical_link = "album.canonicalLink"
            image = 'album.pictureUri'
        elif page_type == "promotion_list":
            page_title = "promotion.name"
            meta_keywords = "promotion.metaKeywords?:promotion.name"
            meta_description = "promotion.metaDescription?:promotion.name"
            meta_title = "promotion.metaTitle?:promotion.name"
            url = canonical_link = "promotion.canonicalLink"
            image = 'promotion.imageUri'
        elif page_type == "order_cart":
            meta_keywords = "translate('Giỏ hàng')"
            meta_description = "translate('Giỏ hàng')"
            meta_title = "translate('Giỏ hàng')"
            variable = ''' {% set products = serviceCart().productList %}
                           {% set totalCartMoney = serviceCart().totalMoney %}
                           {% set latestProduct = products|last %}'''
        elif page_type == "order_checkout":
            meta_keywords = "translate('Thanh toán')"
            meta_description = "translate('Thanh toán')"
            meta_title = "translate('Thanh toán')"
            variable = '''  {% set user = null %}
                            {% set customer = null %}
                            {% set point = 0 %}
                            {% if(hasIdentity() is not empty) %}
                                {% set user = getUser() %}
                                {% set customer = getCustomerStore({
                                    'mobile': user.mobile
                                }) %}
                                {% if customer.points > 0 %}
                                    {% set point = customer.points %}
                                {% endif %}
                            {% elseif jsonDecode(getCookies('cod')) is not empty %}
                                {% set user = jsonDecode(getCookies('cod')) %}
                            {% endif %}
                            {% set products = serviceCart().productList %}
                            {% set totalCartMoney = serviceCart().totalMoney %}
                            {% set quantity = serviceCart().totalQuantities %}'''
        else:
            pass  # Use defaults

        return (
                "{%extends \"layout/layout\" %}\n"
                "{%block meta %}\n"
                "{{ headTitle(" + page_title + ").setSeparator(' - ').setAutoEscape(false)|raw }}\n"
                "<meta name=\"keywords\" content=\"{{ " + meta_keywords + " }}\">\n"
                "<meta name=\"description\" content=\"{{ " + meta_description + " }}\">\n"
                "<meta property=\"og:title\" content=\"{{ " + meta_title + " }}\">\n"                                                                               
                "<meta property=\"og:url\" content=\"{{ " + url + " }}\">\n"
                "<meta property=\"og:image\" content=\"{{ " + image + " }}\">\n"                                                                                                                                                                                                                                                                                    
                "<link rel=\"canonical\" href=\"{{ " + canonical_link + " }}\">\n"
                "{%endblock %}\n"
                "\n"
                "{%block body %}\n"
                + str(variable) + "\n" + str(content.prettify()) + "\n"
                "{%endblock %}\n").strip()

    def layout_render_component(self):
        return ("""
             <!DOCTYPE html>
                <html lang="vi-VN" data-nhanh.vn-template="{{ templateDir() }}">
                <head>
                    <meta charset="utf-8">
                    {{ showMetaTag() | raw }}
                    <link href="{{ getFavicon() }}" rel="shortcut icon" type="image/vnd.microsoft.icon">
                    {{ headMeta().appendName('viewport', 'width=device-width, initial-scale=1.0').appendHttpEquiv('X-UA-Compatible', 'IE=edge').setAutoEscape(false)|raw }}

                    {% block meta %}{% endblock %}
                    {{ loadBootstrapCss() | raw }}
                    {{ loadCommonCss() | raw }}
                    {{ loadTemplateCss() | raw }}
                    {{ loadScripts({'position':'head'}) | raw }}
                </head>
                <body>
                {{ loadBootstrapJs() | raw  }}
                {{ loadCommonJs() | raw }}
                {{ loadTemplateJs() | raw }}
                <div id="app">
                    {% include 'layout/header' %}
                    {% block body %}{% endblock %}
                    {% include 'layout/footer' %}
                </div>
                {{ loadScripts({'position':'body'}) | raw }}
                {{ loadViewMarketingEvent() | raw }}
                </body>
                </html>
             """).strip()

    def extract_layout_components(self, soup):
        """Extract header and footer from page and save directly to GitHub"""
        # Extract header
        header = soup.find('header') or soup.find(class_=re.compile(r'header|top-bar'))
        if header and not self.results['pages'].get('header'):
            # Generate GitHub path
            header_path = f"{self.folder_name}/view/layout/header.twig"

            # Ensure parent directory exists before saving
            self.ensure_github_directory_exists(os.path.dirname(header_path))

            # Save directly to GitHub with proper message
            self.save_to_github_if_empty(header_path, str(header.prettify()), "Save header component")

            self.results['pages']['header'] = {
                'file': header_path
            }
            print(f"Header component saved to {header_path}")

        # Extract footer
        footer = soup.find('footer') or soup.find(class_=re.compile(r'footer|bottom-bar'))
        if footer and not self.results['pages'].get('footer'):
            # Generate GitHub path
            footer_path = f"{self.folder_name}/view/layout/footer.twig"

            # Ensure parent directory exists before saving
            self.ensure_github_directory_exists(os.path.dirname(footer_path))

            # Save directly to GitHub with proper message
            self.save_to_github_if_empty(footer_path, str(footer.prettify()), "Save footer component")

            self.results['pages']['footer'] = {
                'file': footer_path
            }
            print(f"Footer component saved to {footer_path}")

        # Create layout file that includes header and footer
        if header and footer and not self.results['pages'].get('layout'):
            # Generate GitHub path
            layout_path = f"{self.folder_name}/view/layout/layout.twig"

            # Ensure parent directory exists before saving
            self.ensure_github_directory_exists(os.path.dirname(layout_path))

            # Generate layout content
            layout_content = self.layout_render_component()

            # Save directly to GitHub with proper message
            self.save_to_github_if_empty(layout_path, layout_content, "Save layout component")

            self.results['pages']['layout'] = {
                'file': layout_path
            }
            print(f"Layout component saved to {layout_path}")


async def fetch_all_pages(url, folder_name, page_rules, github_token=GITHUB_ACCESS_TOKEN,
                          github_repo_name=GITHUB_REPO_FULLNAME):
    """Run async crawler to fetch all pages"""
    try:
        # Validate GitHub parameters
        if not github_token or not github_repo_name:
            return {
                "status": "error",
                "message": "GitHub token and repository name are required",
                "output_folder": folder_name
            }

        page_manager = PageManager(
            base_url=url,
            folder_name=folder_name,
            page_rules=page_rules,
            github_token=github_token,
            github_repo_name=github_repo_name
        )

        # Create client session with SSL verification disabled and timeout
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=120)  # 2 minute timeout

        async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        ) as session:
            # Start with the base URL
            css_scan_success = await page_manager.scan_css_first(session, url)
            if not css_scan_success:
                print("Warning: CSS scanning was not successful, but continuing with page crawling")

            await page_manager.process_page(session, url)

        return {
            "status": "success",
            "message": f"Website crawled and saved to GitHub: {url}",
            "output_folder": folder_name
        }
    except Exception as e:
        print(f"ERROR: Exception during crawl: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Error crawling website: {str(e)}",
            "output_folder": folder_name
        }


def start_crawl_task(background_tasks: BackgroundTasks, job_id: str, url: str, folder_path: str, page_rules: dict,
                     active_jobs: dict):
    """Start the crawling process in a background task"""
    background_tasks.add_task(
        crawl_website_task,
        job_id=job_id,
        url=url,
        folder_path=folder_path,
        page_rules=page_rules,
        active_jobs=active_jobs
    )


async def crawl_website_task(job_id: str, url: str, folder_path: str, page_rules: dict, active_jobs: dict):
    """Background task to handle website crawling"""
    try:
        active_jobs[job_id]["status"] = "running"

        # Start crawling
        result = await fetch_all_pages(url, folder_path, page_rules)

        if result["status"] == "success":
            # Update job status on success
            active_jobs[job_id]["status"] = "completed"
            active_jobs[job_id]["message"] = f"Successfully crawled website and saved to GitHub: {url}"
        else:
            # Update job status on failure
            active_jobs[job_id]["status"] = "failed"
            active_jobs[job_id]["message"] = f"Error crawling website: {result['message']}"
    except Exception as e:
        # Handle any unexpected exceptions
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["message"] = f"Error crawling website: {str(e)}"