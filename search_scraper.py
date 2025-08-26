import time, re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from utils import now_iso, parse_int_maybe, extract_first, gen_tweet_id

# This is the URL pattern for Twitter/X live search
# {tag} will be replaced with the hashtag we want to search
LIVE_URL = "https://x.com/search?q=%23{tag}&src=typed_query&f=live"

class SearchScraper:
    def __init__(self, driver):
        # Save the web browser driver (like Chrome)
        self.driver = driver

    def _tweet_to_dict(self, t):
        # This function takes one tweet card (t) and turns it into a dictionary (a data object)
        # It collects tweet link, user handle, text, likes, replies, etc.
        data = {
            "tweet_url": None, "tweet_id": None,
            "user_handle": None, "profile_url": None,
            "content": None, "hashtags": None,
            "post_time": None, "scrape_time": now_iso(),
            "likes": None, "comments": None, "reposts": None
        }

        # Get tweet URL, ID, and time
        try:
            # Find the link that has the tweet and time
            a = t.find_element(By.XPATH, './/a[contains(@href,"/status/")][.//time]')
            data["tweet_url"] = a.get_attribute("href")

            # Get the "time" element inside the tweet
            time_el = a.find_element(By.TAG_NAME, "time")
            data["post_time"] = time_el.get_attribute("datetime")

            # Extract the tweet ID from the URL (numbers after "status/")
            data["tweet_id"] = extract_first(r"status/(\d+)", data["tweet_url"]) or gen_tweet_id()
        except Exception:
            # If we can’t find the real ID, just make a fake one (UUID)
            data["tweet_id"] = gen_tweet_id()

        # Get user handle and profile link
        try:
            user_a = t.find_element(By.XPATH, './/div[@data-testid="User-Name"]//a')
            profile = user_a.get_attribute("href")
            data["profile_url"] = profile

            # Get the handle (the last part of the URL)
            handle = profile.rstrip("/").split("/")[-1]
            # If it’s not some "user/xxxx" type, keep it
            data["user_handle"] = handle if "user/" not in profile else None
        except Exception:
            pass

        # Get tweet text and hashtags
        try:
            text_el = t.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
            content = text_el.text
            data["content"] = content
            # Collect all words starting with "#" means hashtag
            data["hashtags"] = ";".join([w for w in content.split() if w.startswith("#")])
        except Exception:
            pass

        # Small helper inside: get stats like likes, replies, reposts
        def stat_try(testid):
            try:
                node = t.find_element(By.XPATH, f'.//button[@data-testid="{testid}"]')
                txt = node.text or node.get_attribute("aria-label") or ""
                return parse_int_maybe(extract_first(r"([\d,\.KMB]+)", txt))
            except Exception:
                return None

        # Get stats for comments, reposts, likes
        data["comments"] = stat_try("reply")
        data["reposts"]  = stat_try("retweet")
        data["likes"]    = stat_try("like")


        return data

    def search_hashtag(self, hashtag: str, limit: int | None = None):
        # Open the live search page for the given hashtag
        self.driver.get(LIVE_URL.format(tag=hashtag.lstrip("#")))
        time.sleep(3)  # wait a little for the page to load

        seen_ids = set()   # to remember tweets we already saw
        out = []           # list of all tweet data
        body = self.driver.find_element(By.TAG_NAME, "body")

        stagnant_scrolls = 0  # how many times we scrolled without new tweets

        # while loop to keep scrolling and searching for new tweets
        while True:
            # Find all tweet cards on the page
            cards = self.driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            new_found = 0

            for c in cards:
                try:
                    d = self._tweet_to_dict(c)  # turn tweet into dictionary
                    if d["tweet_id"] in seen_ids:
                        continue  # skip if already seen
                    seen_ids.add(d["tweet_id"])
                    out.append(d)
                    new_found += 1

                    # If we hit the limit, stop and return what we have
                    if limit and len(out) >= limit:
                        return out
                except StaleElementReferenceException:
                    # Tweet disappeared (page updated), skip it
                    continue
                except Exception:
                    # Ignore any other error
                    continue

            # Scroll down the page
            body.send_keys(Keys.END)
            time.sleep(1.5)

            if new_found == 0:
                stagnant_scrolls += 1  # No new tweets found
            else:
                stagnant_scrolls = 0   # Reset if new tweets were found

            # If no limit, stop when no new tweets after several scrolls
            if not limit and stagnant_scrolls >= 4:
                return out
