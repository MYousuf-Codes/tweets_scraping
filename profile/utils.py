import re
from selenium.common.exceptions import NoSuchElementException

def safe_text(driver_or_elem, by, value):
    try:
        return driver_or_elem.find_element(by, value).text.strip()
    except NoSuchElementException:
        return None

def safe_attr(elem, attr: str):
    try:
        return elem.get_attribute(attr)
    except Exception:
        return None

def extract_first(pattern: str, text: str):
    if not text:
        return None
    match = re.search(pattern, text)
    return match.group(1) if match else None
