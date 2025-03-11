import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse, urljoin
import os
import json
import re
from bs4 import BeautifulSoup
import logging
from config import PAGE_TYPE_MAPPING
from website_cloner.folder_manager import FolderManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PageManager(scrapy.Spider):
    name = 'page_manager'

    def __init__(self, base_url, output_folder, page_rules, *args, **kwargs):

        super(PageManager, self).__init__(*args, **kwargs)
        # Ensure base URL has protocol
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'https://' + base_url
        self.start_urls = [base_url]
        self.base_url = base_url
        self.output_folder = output_folder
        self.visited_urls = set()
        self.page_types = page_rules
        self.urls_to_crawl = []
        self.type_mapping = json.loads(PAGE_TYPE_MAPPING)
        self.results = {
            'website': base_url,
            'pages': {}
        }

    def parse(self, response):
        # Process current page
        self.identify_and_process_page(response)

        # Find links to other pages
        links = response.css("a::attr(href)").getall()
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

            # Check against each page type pattern
            for page_type, info in self.page_types.items():
                if 'pattern' in info and not info['found'] and re.match(info['pattern'], path):
                    info['found'] = True
                    self.visited_urls.add(link)
                    yield scrapy.Request(link, callback=self.parse_specific_page, cb_kwargs={'page_type': page_type})

            # Add to general crawl queue if not already identified as a specific page type
            if link not in self.visited_urls and len(self.visited_urls) < 30:  # Limit to avoid excessive crawling
                self.visited_urls.add(link)
                yield scrapy.Request(link, callback=self.parse)

    def parse_specific_page(self, response, page_type):
        """Process a specific page type"""
        self.extract_and_save_page_content(response, page_type)

        # Also extract layout components (header, footer) from every page
        self.extract_layout_components(response)

    def identify_and_process_page(self, response):
        """Identify page type based on URL pattern and process it"""
        path = urlparse(response.url).path

        for page_type, info in self.page_types.items():
            if 'pattern' in info and re.match(info['pattern'], path):
                self.extract_and_save_page_content(response, page_type)
                return True

        # If homepage and not yet found, check if this is the homepage
        if not self.page_types['homepage']['found'] and (path == '/' or path == ''):
            self.extract_and_save_page_content(response, 'homepage')
            return True

        return False

    def extract_and_save_page_content(self, response, page_type):
        """Extract content and save to appropriate file"""
        # Check if page type exists in mapping
        if page_type not in self.type_mapping:
            logger.warning(f"No mapping found for page type: {page_type}")
            return

        mapping = self.type_mapping.get(page_type)

        if isinstance(mapping, dict):
            if page_type == 'category':
                relative_path = mapping.get("product_category")
            elif page_type == 'blog':
                relative_path = mapping.get("blog_category")
            else:
                # Default case if needed
                relative_path = next(iter(mapping.values()), None)
        else:
            relative_path = mapping

        if not relative_path:
            logger.warning(f"Empty mapping for page type: {page_type}")
            return

        file_path = os.path.join(self.output_folder, relative_path)

        # Check if this is a page type that should also be saved to an index file
        info = self.page_types.get(page_type, {})
        if info.get('index_file', False) and isinstance(mapping, dict):
            # Get the correct index path based on page type
            if page_type == 'category':
                index_path = mapping.get("product_index")
            elif page_type == 'blog':
                index_path = mapping.get("blog_index")
            else:
                index_path = None

            if index_path:
                index_file_path = os.path.join(self.output_folder, index_path)
            else:
                index_file_path = None
        else:
            index_file_path = None

        # Extract content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove scripts and style for cleaner content
        for script in soup.find_all('script'):
            script.extract()

        # Get main content (excluding header and footer)
        main_content = soup.body
        if not main_content:
            return "Không tìm thấy body!"
        for tag in main_content.find_all(["header", "footer"]):
            tag.extract()
        result = BeautifulSoup("".join(str(tag) for tag in main_content.contents), "html.parser")

        formatted_content = self.page_render_components(page_type, result)

        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Check if file exists and has content before writing
        flag_content = True
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:  # If file already has content
                    flag_content = False
                    logger.info(f"File already has content, skipping: {file_path}")

        # Save the processed content if file doesn't exist or is empty
        if flag_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            logger.info(f"Saved content for {page_type}: {file_path}")


        # If it's a category or blog_category, also save to index file
        if index_file_path:
            formatted_content2 = self.page_render_components('product_index', result)
            if page_type == 'blog':
                formatted_content2 = self.page_render_components('blog_index', result)

            os.makedirs(os.path.dirname(index_file_path), exist_ok=True)

            # Check if file exists and has content before writing
            flag_content_index = True
            if os.path.exists(index_file_path):
                with open(index_file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        flag_content_index = False
                        logger.info(f"File already has content, skipping: {index_file_path}")

            # Save the processed content if file doesn't exist or is empty
            if flag_content_index:
                with open(index_file_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_content2)
                logger.info(f"Saved content for {page_type}: {index_file_path}")

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
            "blog": "category.name",
            "blog_article": "news.title | striptags",
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
        if page_title == "Page type not recognized.":
            return page_title

        return (
                "{%extends \"layout/layout\" %}\n"
                "{%block meta %}\n"
                "    {{ headTitle(" + page_title + ").setSeparator(' - ').setAutoEscape(false)|raw }}\n"
                "    <meta name=\"keywords\" content=\"{{ getKeyContentValue('META_KEYWORDS') }}\">\n"
                "    <meta name=\"description\" content=\"{{ getKeyContentValue('META_DESCRIPTION') }}\">\n"
                "    <meta property=\"og:title\" content=\"{{ getKeyContentValue('META_TITLE') }}\">\n"
                "    <meta property=\"og:url\" content=\"{{ getCurrentUrl() }}\">\n"
                "    <meta property=\"og:image\" content=\"{{ getBusinessLogo() }}\">\n"
                "{%endblock %}\n"
                "\n"
                "{%block body %}\n"
                + str(content.prettify()) + "\n"
                "{%endblock %}\n"

        ).strip()

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

    def extract_layout_components(self, response):
        """Extract header and footer from page"""
        soup = BeautifulSoup(response.text, 'html.parser')

        folder_manager = FolderManager(self.base_url)
        folder_manager.create_css_files(self.output_folder, soup)

        # Extract header
        header = soup.find('header') or soup.find(class_=re.compile(r'header|top-bar'))
        if header and not self.results['pages'].get('header'):
            header_path = os.path.join(self.output_folder, "view/layout/header.twig")
            os.makedirs(os.path.dirname(header_path), exist_ok=True)
            with open(header_path, 'w', encoding='utf-8') as f:
                f.write(str(header.prettify()))
            self.results['pages']['header'] = {
                'file': header_path
            }

        # Extract footer
        footer = soup.find('footer') or soup.find(class_=re.compile(r'footer|bottom-bar'))
        if footer and not self.results['pages'].get('footer'):
            footer_path = os.path.join(self.output_folder, "view/layout/footer.twig")
            os.makedirs(os.path.dirname(footer_path), exist_ok=True)
            with open(footer_path, 'w', encoding='utf-8') as f:
                f.write(str(footer.prettify()))
            self.results['pages']['footer'] = {
                'file': footer_path
            }

        # Create layout file that includes header and footer
        if header and footer and not self.results['pages'].get('layout'):
            layout_path = os.path.join(self.output_folder, "view/layout/layout.twig")
            os.makedirs(os.path.dirname(layout_path), exist_ok=True)
            layout_content = self.layout_render_component()
            with open(layout_path, 'w', encoding='utf-8') as f:
                f.write(layout_content)
            self.results['pages']['layout'] = {
                'file': layout_path
            }

def fetch_all_pages(url, output_folder, page_rules):
    """Run Scrapy crawler to fetch all pages"""
    process = CrawlerProcess(settings={
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 1,  # Be polite
        "LOG_LEVEL": "INFO"
    })
    try:
        process.crawl(PageManager,
                      base_url=url,
                      output_folder=output_folder,
                      page_rules=page_rules)
        process.start()
    except Exception as e:
        print(f"ERROR: Exception during crawl: {e}")
        import traceback
        traceback.print_exc()

    process.start()

    return {
        "status": "success",
        "message": f"Website crawled: {url}",
        "output_folder": output_folder
    }