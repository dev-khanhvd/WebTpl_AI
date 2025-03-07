import requests
from bs4 import BeautifulSoup, Comment

# Crawl url của 1 trang web
def download_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Lỗi tải trang: {e}")
        return None

# Sau khi crawl về, xử lý bỏ các thẻ không cần thiết. Ví dụ: script, link ...
def clean_html(html):
    for tag in html.find_all(["script", "noscript", "input", "link"]):
        if tag.name == "input" and tag.get("type") == "hidden":
            tag.extract()
        elif tag.name == "link" and tag.get("as") == "script" and tag.get("rel") == "preload":
            tag.extract()
        elif tag.name in ["script", "noscript", "link"]:
            tag.extract()
    for comment in html.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    return html

# Xử lý html theo từng lựa chọn và trả về 1 chuỗi để bắt đầu lưu vào file đã có sẵn
def extract_content(html, part, body_part=None):
    content_html = clean_html(html)
    if part == "body":
        body = content_html.body
        result = None
        if not body:
            return "Không tìm thấy body!"
        if body_part == "content":
            for tag in body.find_all(["header", "footer"]):
                tag.extract()
            result = BeautifulSoup("".join(str(tag) for tag in body.contents), "html.parser")
        elif body_part in ["header", "footer"]:
            section = body.find(body_part)
            if not section:
                return f"Không tìm thấy <{body_part}>!"
            result = BeautifulSoup(section, "html.parser")
        return result.prettify()
    elif part == "layout":
        for body_tag in content_html.find_all("body"):
            body_tag.extract()
        new_body = content_html.new_tag("body")
        div = content_html.new_tag("div", id="app")
        new_body.append(div)
        head = content_html.find("head")
        if head:
            head.insert_after(new_body)
        return str(content_html)
    return "Không có nội dung phù hợp!"

