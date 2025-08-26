import time, re, csv, os
from selenium.webdriver.common.by import By
from utils import safe_attr, safe_text, extract_first

class ProfileScraper:
    def __init__(self, driver, csv_file="profiles.csv"):
        self.driver = driver
        self.csv_file = csv_file

        # if CSV file does not exist, make a new one with headings
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "username_handle", "display_name", "user_id", "bio",
                    "email", "phone", "address", "verification_status", "account_creation_date",
                    "account_type", "protected_status", "followers_count",
                    "following_count", "tweet_count", "media_count",
                    "location", "website_url", "profile_language"
                ])

    # try to get one element, if not found, return None
    def _maybe(self, xpath):
        try:
            return self.driver.find_element(By.XPATH, xpath)
        except:
            return None

    # same as _maybe, but give back text
    def _maybe_text(self, xpath):
        el = self._maybe(xpath)
        return safe_text(el) if el else None

    # clean numbers like "2.5k" or "1.2M" into real numbers
    def _extract_number(self, raw: str):
        if not raw:
            return None
        raw = raw.lower().replace(",", "").strip()
        match = re.search(r"([\d\.]+)([km]?)", raw)
        if not match:
            return None
        num, suffix = match.groups()
        num = float(num)
        if suffix == "k":
            num *= 1_000
        elif suffix == "m":
            num *= 1_000_000
        return int(num)

    # get followers and following counts from profile stats
    def _stats(self):
        stats = {}
        try:
            items = self.driver.find_elements(By.XPATH, '//div[@data-testid="UserStats"]//a')
            for a in items:
                lbl = a.get_attribute("aria-label") or a.text
                if "Follower" in lbl:
                    stats["followers_count"] = self._extract_number(lbl)
                elif "Following" in lbl:
                    stats["following_count"] = self._extract_number(lbl)
        except:
            pass
        return stats

    # get count from profile tabs like Posts, Media
    def _tab_count(self, tab_name: str):
        try:
            tab = self.driver.find_element(
                By.XPATH, f'//a[@role="tab" and .//span[text()="{tab_name}"]]'
            )
            aria = tab.get_attribute("aria-label") or tab.text
            return self._extract_number(aria)
        except:
            return None

    # get profile or avatar image link
    def _image_src(self, testid: str):
        try:
            c = self.driver.find_element(By.XPATH, f'//div[@data-testid="{testid}"]//img')
            return safe_attr(c, "src")
        except:
            try:
                return self.driver.execute_script(
                    f"return document.querySelector('div[data-testid=\"{testid}\"] img')?.src"
                )
            except:
                return None

    # get banner (cover) image link
    def _banner_src(self):
        try:
            img = self.driver.find_element(By.XPATH, '//img[@data-testid="profileHeaderPhoto"]')
            return safe_attr(img, "src")
        except:
            try:
                hdr = self.driver.find_element(By.XPATH, '//div[@data-testid="profileHeaderBanner"]')
                style = safe_attr(hdr, "style") or ""
                return extract_first(r'url\("([^"]+)"\)', style)
            except:
                return None

    # check if account is verified
    def _verification_status(self):
        try:
            self.driver.find_element(
                By.XPATH, '//div[@data-testid="UserName"]//*[contains(@aria-label,"Verified")]'
            )
            return "Verified"
        except:
            return "Unverified"

    # check if account is private or public
    def _protected_status(self):
        try:
            self.driver.find_element(By.XPATH, '//svg[@aria-label="Protected account"]')
            return "Private"
        except:
            pass
        if "This account is private" in (self.driver.page_source or ""):
            return "Private"
        return "Public"

    # guess account type (business or personal)
    def _account_type(self):
        try:
            chip = self.driver.find_element(By.XPATH, '//div[@data-testid="UserProfessionalCategory"]')
            if chip and chip.text.strip():
                return "Business/Professional"
        except:
            pass
        return "Personal/Unknown"

    # pull user id from page source
    def _user_id_from_source(self):
        html = self.driver.page_source
        rid = extract_first(r'"rest_id"\s*:\s*"(\d+)"', html)
        if rid:
            return rid
        return extract_first(r'"id_str"\s*:\s*"(\d+)"', html)

    # main method: open profile, collect all info, save to CSV
    def scrape_profile(self, profile_url: str, save=True):
        self.driver.get(profile_url)
        time.sleep(3)  # wait so page can load

        # break down info
        handle = profile_url.rstrip("/").split("/")[-1]
        display_name = self._maybe_text('//div[@data-testid="UserName"]//span[1]')
        bio = self._maybe_text('//div[@data-testid="UserDescription"]')

        # joined date, location, website
        join_date, location, website = None, None, None
        try:
            items = self.driver.find_elements(By.XPATH, '//div[@data-testid="UserProfileHeader_Items"]//span')
            for item in items:
                text = item.text.strip()
                if text.startswith("Joined "):
                    join_date = text.replace("Joined", "").strip()
                elif text.startswith("http") or "." in text:
                    website = text
                else:
                    location = text
        except:
            pass
        try:
            a = self.driver.find_element(By.XPATH, '//a[@data-testid="UserUrl"]')
            website = safe_attr(a, "href") or website
        except:
            pass


        # get followers and following numbers
        stats = self._stats()
        followers, following = stats.get("followers_count"), stats.get("following_count")

        # number of posts and media
        tweet_count = self._tab_count("Posts")
        media_count = self._tab_count("Media")

        # verification, private/public, account type
        verification = self._verification_status()
        protected = self._protected_status()
        account_type = self._account_type()
        user_id = self._user_id_from_source()

        # try to find email/phone in bio text
        email = extract_first(r'[\w\.-]+@[\w\.-]+\.\w+', bio or "")
        phone = extract_first(r'(\+?\d[\d\-\s]{7,}\d)', bio or "")
        address = location

        # profile language from html tag
        try:
            lang = self.driver.find_element(By.TAG_NAME, "html").get_attribute("lang")
        except:
            lang = None

        # all data packed in a box (dict)
        data = {
            "username_handle": handle,
            "display_name": display_name,
            "user_id": user_id,
            "bio": bio,
            "email": email,
            "phone": phone,
            "address": address,
            "verification_status": verification,
            "account_creation_date": join_date,
            "account_type": account_type,
            "protected_status": protected,
            "followers_count": followers,
            "following_count": following,
            "tweet_count": tweet_count,
            "media_count": media_count,
            "location": location,
            "website_url": website,
            "profile_language": lang,
        }
        
        #save to csv with file handling 
        with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(data.values())

        return data

