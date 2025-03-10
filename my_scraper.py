import scrapy
from scrapy.spiders import Spider
from urllib.parse import urlparse
import os
import json
import logging
import argparse
import re


class F1GenzBagSelectiveSpider(Spider):
    name = 'f1genz_bag_selective'
    allowed_domains = ['f1genz-bag.myharavan.com']
    start_urls = ['https://f1genz-bag.myharavan.com/']

    # Page types to find
    page_types = {
        'homepage': {'pattern': r'^/$', 'found': False},
        'category': {'pattern': r'^/collections/[^/]+$', 'found': False},
        'product': {'pattern': r'^/products/[^/]+$', 'found': False},
        'cart': {'pattern': r'^/cart$', 'found': False},
        'checkout': {'pattern': r'^/checkout$', 'found': False},
        'blog_list': {'pattern': r'^/blogs/[^/]+$', 'found': False},
        'blog_article': {'pattern': r'^/blogs/[^/]+/[^/]+$', 'found': False},
        'info_page': {'pattern': r'^/pages/[^/]+$', 'found': False}
    }

    # URLs to crawl (will be populated during crawling)
    urls_to_crawl = []

    # Keep track of visited URLs to avoid duplicates
    visited_urls = set()

    def __init__(self, mode='content', *args, **kwargs):
        super(F1GenzBagSelectiveSpider, self).__init__(*args, **kwargs)

        # Set extraction mode
        self.mode = mode.lower()  # 'content', 'layout', or 'css'

        # Create output folders
        self.base_dir = f'f1genz_bag_{self.mode}'
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

        # Create extraction-specific folders
        if self.mode == 'css':
            self.css_dir = os.path.join(self.base_dir, 'css')
            if not os.path.exists(self.css_dir):
                os.makedirs(self.css_dir)
        else:
            # Create folders for each page type
            self.folders = {}
            for page_type in self.page_types:
                self.folders[page_type] = os.path.join(self.base_dir, page_type)
                if not os.path.exists(self.folders[page_type]):
                    os.makedirs(self.folders[page_type])

        # Initialize results tracking
        self.results = {
            'mode': self.mode,
            'pages': {} if self.mode != 'css' else None,
            'css_files': [] if self.mode == 'css' else None
        }

    def parse(self, response):
        print(response)
        """Parse the homepage and find links to other page types"""
        # Process homepage
        if self.mode != 'css':
            self.process_page(response, 'homepage')
            self.page_types['homepage']['found'] = True

        # If CSS mode, extract all CSS links
        if self.mode == 'css':
            for css_link in response.css('link[rel="stylesheet"]::attr(href)').getall():
                if css_link and not css_link.startswith(('data:', 'javascript:')):
                    # Make absolute URL if it's relative
                    if css_link.startswith('/'):
                        css_link = f"https://f1genz-bag.myharavan.com{css_link}"

                    # Request the CSS file
                    if css_link not in self.visited_urls:
                        self.visited_urls.add(css_link)
                        yield scrapy.Request(css_link, callback=self.parse_css)

        # Find links to other page types
        for link in response.css('a::attr(href)').getall():
            # Skip invalid links
            if not link or link.startswith(('#', 'javascript:', 'data:', 'mailto:')):
                continue

            # Make absolute URL if it's relative
            if link.startswith('/'):
                link = f"https://f1genz-bag.myharavan.com{link}"

            # Skip external domains
            if 'f1genz-bag.myharavan.com' not in link:
                continue

            # Skip if already visited or queued
            if link in self.visited_urls or link in [url for url, _ in self.urls_to_crawl]:
                continue

            # Get the path for pattern matching
            path = urlparse(link).path

            # Check against each page type pattern
            for page_type, info in self.page_types.items():
                if not info['found'] and re.match(info['pattern'], path):
                    self.urls_to_crawl.append((link, page_type))
                    self.page_types[page_type]['found'] = True
                    logging.info(f"Found {page_type} page: {link}")
                    break

        # Now crawl the discovered links
        for url, page_type in self.urls_to_crawl:
            if url not in self.visited_urls:
                self.visited_urls.add(url)
                if self.mode == 'css':
                    yield scrapy.Request(url, callback=self.parse_css_from_page)
                else:
                    yield scrapy.Request(url, callback=self.parse_specific_page, meta={'page_type': page_type})

    def parse_specific_page(self, response):
        """Process a specific page type"""
        page_type = response.meta['page_type']
        self.process_page(response, page_type)

    def parse_css_from_page(self, response):
        """Extract CSS links from the page"""
        for css_link in response.css('link[rel="stylesheet"]::attr(href)').getall():
            if css_link and not css_link.startswith(('data:', 'javascript:')):
                # Make absolute URL if it's relative
                if css_link.startswith('/'):
                    css_link = f"https://f1genz-bag.myharavan.com{css_link}"

                # Request the CSS file
                if css_link not in self.visited_urls:
                    self.visited_urls.add(css_link)
                    yield scrapy.Request(css_link, callback=self.parse_css)

    def parse_css(self, response):
        """Save CSS file"""
        # Get filename from URL
        filename = os.path.basename(urlparse(response.url).path)
        if not filename.endswith('.css'):
            filename += '.css'

        # Save the CSS file
        file_path = os.path.join(self.css_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(response.body)

        # Add to results
        self.results['css_files'].append({
            'url': response.url,
            'file': filename
        })

        # Save results
        self.save_results()

        logging.info(f"Saved CSS: {response.url}")

    def process_page(self, response, page_type):
        """Process and save page based on extraction mode"""
        filename = self.get_filename_from_url(response.url)
        file_path = os.path.join(self.folders[page_type], filename)

        if self.mode == 'layout':
            # Layout mode: Extract everything except body content
            html_start = response.text.find('<html')
            body_start = response.text.find('<body', html_start)
            body_end = response.text.find('</body>', body_start)

            if html_start >= 0 and body_start >= 0 and body_end >= 0:
                # Extract everything except body content
                html_before_body = response.text[html_start:body_start]
                html_after_body = response.text[body_end:]
                output = html_before_body + "<body></body>" + html_after_body
            else:
                output = response.text

        elif self.mode == 'content':
            # Content mode: Extract only the content within body tag, excluding header and footer

            # Extract the entire body content first
            body_html = response.css('body').get()

            if body_html:
                # Remove the body tags
                body_content = re.sub(r'^<body[^>]*>', '', body_html)
                body_content = re.sub(r'</body>$', '', body_content)

                # Find and remove header elements
                header_elements = response.css('header, .header, [class*="header"]').getall()
                for header in header_elements:
                    body_content = body_content.replace(header, '')

                # Find and remove footer elements
                footer_elements = response.css('footer, .footer, [class*="footer"]').getall()
                for footer in footer_elements:
                    body_content = body_content.replace(footer, '')

                output = body_content
            else:
                # Fallback if no body found
                output = response.text

        # Save the processed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(output)

        # Update results
        if self.mode != 'css':
            self.results['pages'][page_type] = {
                'url': response.url,
                'title': response.css('title::text').get() or "No Title",
                'file': filename
            }

        # Save results
        self.save_results()

        logging.info(f"Saved {page_type} page: {response.url}")

    def get_filename_from_url(self, url):
        """Generate a filename from URL"""
        path = urlparse(url).path.strip('/')

        if not path:
            return 'index.html'

        parts = path.split('/')
        if parts:
            safe_filename = re.sub(r'[^\w\-\.]', '_', parts[-1])
            if not safe_filename.endswith('.html'):
                safe_filename += '.html'
            return safe_filename

        return 'page.html'

    def save_results(self):
        """Save results to JSON file"""
        with open(os.path.join(self.base_dir, 'results.json'), 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)


# Script to run the spider directly
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Selective f1genz-bag.myharavan.com website scraper')
    parser.add_argument('--mode', type=str, choices=['content', 'layout', 'css'], default='content',
                        help='Extraction mode: content, layout, or css')

    args = parser.parse_args()

    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': False,  # Set to True in production for ethical crawling
        'DOWNLOAD_DELAY': 1,  # Be polite to the server
        'LOG_LEVEL': 'INFO'
    })

    process.crawl(F1GenzBagSelectiveSpider, mode=args.mode)
    process.start()

# How to run:
# 1. Install dependencies: pip install scrapy
# 2. Save this script as my_scraper.py
# 3. For CSS extraction: python my_scraper.py  --mode css
# 4. For Layout extraction: python my_scraper.py  --mode layout
# 5. For Content extraction: python my_scraper.py  --mode content