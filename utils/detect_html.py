import re
from bs4 import BeautifulSoup
from utils.embedding import Embedding

class DetectHtml:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def detect_position_html(self, wrapper_pattern, soup, question=None, type=None, options=None, index_name=None):
        """
        Find an HTML wrapper based on pattern, extract an item from it, and clear the wrapper.

        Args:
            wrapper_pattern: String or list of strings with patterns to match wrappers
            soup: BeautifulSoup object or HTML string
            question, type, options, index_name: Additional parameters (not used in current implementation)

        Returns:
            The extracted item from the wrapper or None if no wrapper was found
        """
        # Convert to BeautifulSoup object if string is provided
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'html.parser')

        # Ensure wrapper_pattern is a list
        if isinstance(wrapper_pattern, str):
            wrapper_pattern = [wrapper_pattern]

        # Step 1: Find potential parent wrappers based on patterns
        potential_parents = []
        for pattern in wrapper_pattern:
            # Try to find by ID first, then fall back to class
            elements = soup.find_all(id=re.compile(pattern))
            if not elements:
                elements = soup.find_all(class_=re.compile(pattern))

            if elements:
                potential_parents.extend(elements)

        # Step 2: Extract an item from the first found wrapper
        if potential_parents:
            parent_wrapper = potential_parents[0]
            item = None

            # Try to find the first meaningful child element
            if parent_wrapper.contents:
                for child in parent_wrapper.contents:
                    # Check if it's a non-empty element or non-whitespace string
                    if (not isinstance(child, str) and child) or (isinstance(child, str) and child.strip()):
                        item = child
                        break
            if not item:
                item = parent_wrapper.find()

            parent_wrapper.clear()
            embedings = Embedding(self.base_dir)
            result = embedings.process_question(question, type, item, options, index_name)
            if result:
                twig_soup = BeautifulSoup(f"\n{result}\n", "html.parser")
                parent_wrapper.append(twig_soup)

                return soup

        return None
    def detect_position_home_promotion_section(self, main_wrapper:str, product_wrapper:str, soup, question=None, type=None):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'html.parser')

        prd_wrapper = None
        main_product_wrp = None
        found_items = []
        potential_parents = []
        section_wrp = None
        # Tìm các phần tử tiềm năng theo main_wrapper pattern
        for pattern in main_wrapper:
            elements = soup.find_all(id=re.compile(pattern))
            if not elements:
                elements = soup.find_all(class_=re.compile(pattern))
            potential_parents.extend(elements)
        # Tìm các sản phẩm theo product_wrapper pattern
        for parent in potential_parents:
            items = []
            for keyword in product_wrapper:
                found = soup.find_all(id=re.compile(keyword))
                if not found:
                    found = soup.find_all(class_=re.compile(keyword))
                if found:
                    items.extend(found)

                if items:
                    found_items = items[0].find_all("div", recursive=False)
                    main_product_wrp = items[0].parent
                    prd_wrapper = items[0]
                    break
            if found_items:
                break

        if found_items and prd_wrapper and main_product_wrp and potential_parents:
            list_prd_promt = found_items[0]
            first_products = list_prd_promt.find_all("div", recursive=False)
            prd_wrapper.clear()
            list_prd_promt.clear()
            prd_wrapper.append(first_products[0])

            parent_wrapper = potential_parents[0]
            if parent_wrapper.contents:
                for child in parent_wrapper.contents:
                    if child and not isinstance(child, str) or (isinstance(child, str) and child.strip()):
                        section_wrp = child
                        break

            promotion_section = potential_parents[0]
            promotion_section.clear()
            embedings = Embedding(self.base_dir)
            result = embedings.process_question(question, type, section_wrp, None, 'home_tranning')

            if result:
                section_prm = BeautifulSoup(f"\n{result}\n", "html.parser")
                promotion_section.append(section_prm)
                return soup
        return None
    def detect_position_product_attributes_section(self, main_wrapper:str, attrs_item_wrapper:str, soup, question=None, type=None):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'html.parser')

        prd_wrapper = None
        main_attrs_wrp = None
        found_items = []
        potential_parents = []
        section_wrp = None

        for pattern in main_wrapper:
            elements = soup.find_all(id=re.compile(pattern))
            if not elements:
                elements = soup.find_all(class_=re.compile(pattern))
            potential_parents.extend(elements)

        for parent in potential_parents:
            items = []
            for keyword in attrs_item_wrapper:
                found = soup.find_all(id=re.compile(keyword))
                if not found:
                    found = soup.find_all(class_=re.compile(keyword))
                if found:
                    items.extend(found)

                if items:
                    found_items = items[0].find_all("div", recursive=False)
                    if not found_items:
                        found_items = items[0].find_all("li", recursive=False)

                    main_attrs_wrp = items[0].parent
                    prd_wrapper = items[0]
                    break
            if found_items:
                break

        if found_items and prd_wrapper and main_attrs_wrp and potential_parents:
            first_item = found_items[0]
            prd_wrapper.clear()

            if first_item:
                prd_wrapper.append(first_item)
            else:
                print("Không tìm thấy <li> trong list_prd_promt!")

            parent_wrapper = potential_parents[0]
            if parent_wrapper.contents:
                for child in parent_wrapper.contents:
                    if child and not isinstance(child, str) or (isinstance(child, str) and child.strip()):
                        section_wrp = child
                        break
            attrs_section = potential_parents[0]
            attrs_section.clear()
            embedings = Embedding(self.base_dir)
            result = embedings.process_question(question, type, section_wrp, None, 'product_category_tranning')

            if result:
                section_prm = BeautifulSoup(f"\n{result}\n", "html.parser")
                attrs_section.append(section_prm)
                return soup
        return None
    def detect_position_product_details_attributes_section(self, main_wrapper: str, attrs_item_wrapper: str, soup,
                                                           question=None, type=None):
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup, 'html.parser')

        # Tìm thẻ chứa main_wrapper
        main_section = soup.find(id=re.compile(main_wrapper)) or soup.find(class_=re.compile(main_wrapper))
        if not main_section:
            return None

        # Tìm các item wrapper bên trong main_wrapper
        attrs_wrapper = main_section.find(id=re.compile(attrs_item_wrapper)) or main_section.find(
            class_=re.compile(attrs_item_wrapper))
        if not attrs_wrapper:
            return None

        # Tìm item đầu tiên trong wrapper
        found_items = attrs_wrapper.find_all(["div", "li"], recursive=False)
        if not found_items:
            return None

        first_item = found_items[0]

        attrs_wrapper.clear()
        embedings = Embedding(self.base_dir)
        result = embedings.process_question(question, type, first_item, None, 'product_detail_tranning')

        if result:
            section_prm = BeautifulSoup(f"\n{result}\n", "html.parser")
            attrs_wrapper.append(section_prm)
            return soup

        return None