import os
import json
from config import CONTENT_TEMPLATE_JSON
import requests
from urllib.parse import urlparse, urljoin


class SapoRule:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.content_template = json.loads(CONTENT_TEMPLATE_JSON)
