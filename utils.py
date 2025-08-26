import re, time, uuid, math
from datetime import datetime, timezone
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# This is how we want to show date and time (in a standard format).
ISO = "%Y-%m-%dT%H:%M:%S%z"

def now_iso():
    # Give me the current time in ISO format (like "2025-08-25T13:45:00+0000")
    return datetime.now(timezone.utc).strftime(ISO)

def parse_int_maybe(text: str):
    """Turn text like '12,345' or '1.2K' or '3.4M' into a number. If not possible, give None."""
    if not text: return None
    t = text.replace(",", "").strip().upper()
    try:
        if t.endswith("K"):  # Example: 1.2K, 1200
            return int(float(t[:-1]) * 1_000)
        if t.endswith("M"):  # Example: 3.4M, 3,400,000
            return int(float(t[:-1]) * 1_000_000)
        if t.endswith("B"):  # Example: 2B, 2,000,000,000
            return int(float(t[:-1]) * 1_000_000_000)
        # Remove anything that is not a digit and make it an int (number)
        return int(re.sub(r"[^\d]", "", t) or 0)
    except:
        # If something goes wrong, return None
        return None

def short_wait(driver, seconds=10):
    # Wait for something on the page for a few seconds
    return WebDriverWait(driver, seconds)

def safe_text(el):
    # Try to get the text from an element. If it fails, return None.
    try: return el.text.strip()
    except: return None

def safe_attr(el, name):
    # Try to get a specific attribute (like "href" or "src"). If it fails, return None.
    try: return el.get_attribute(name)
    except: return None

def extract_first(pattern, text):
    # Look inside text with a pattern (regex). Return the first match if found.
    m = re.search(pattern, text or "")
    return m.group(1) if m else None

def gen_tweet_id():
    # Make a random unique ID for a tweet (not real Twitter ID, just ours).
    return str(uuid.uuid4())

def scroll_to_bottom(driver, step_pause=1.5, max_idle=6):
    """Keep scrolling down until the page stops growing taller after some tries."""
    last = 0   # Last page height we saw
    idle = 0   # How many times the page didn't grow
    while True:
        # Scroll down by full page height
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(step_pause)  # Wait a bit so page can load new stuff
        h = driver.execute_script("return document.body.scrollHeight")  # New page height
        if h == last:
            # Page didn't grow taller → count it as idle
            idle += 1
            if idle >= max_idle:
                # If page is idle too many times, stop scrolling
                break
        else:
            # Page grow taller, reset idle counter
            idle = 0
            last = h
