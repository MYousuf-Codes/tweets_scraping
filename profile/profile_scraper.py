import os, csv, time
from selenium.webdriver.common.by import By
from scraper.base_scraper import BaseScraper
from scraper.utils import safe_text, safe_attr, extract_first

class ProfileScraper(BaseScraper):
    def __init__(self, originator: dict, save_dir="originators/"):
        super().__init__(headless=True)
        self.originator = originator
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def scrape_profile(self):
        profile_url = self.originator["profile_url"]
        username = self.originator["user_handle"].lstrip("@")

        self.driver.get(profile_url)
        time.sleep(3)

        profile_data = {
            "username_handle": username,
            "display_name": safe_text(self.driver, By.XPATH, '//div[@data-testid="UserName"]//span[1]'),
            "bio": safe_text(self.driver, By.XPATH, '//div[@data-testid="UserDescription"]'),
            "followers": safe_text(self.driver, By.XPATH, '//a[contains(@href,"/followers")]//span'),
            "following": safe_text(self.driver, By.XPATH, '//a[contains(@href,"/following")]//span'),
            "join_date": safe_text(self.driver, By.XPATH, '//span[contains(text(),"Joined")]'),
            "location": safe_text(self.driver, By.XPATH, '//span[@data-testid="UserLocation"]'),
            "profile_image_url": self._profile_image(),
            "banner_image_url": self._banner_image(),
        }

        self._save_csv(username, profile_data)
        return profile_data

    def _profile_image(self):
        try:
            img = self.driver.find_element(By.XPATH, '//div[@data-testid="UserAvatar"]//img')
            return safe_attr(img, "src")
        except:
            return None

    def _banner_image(self):
        try:
            img = self.driver.find_element(By.XPATH, '//img[@data-testid="profileHeaderPhoto"]')
            return safe_attr(img, "src")
        except:
            style = safe_attr(self.driver.find_element(By.XPATH, '//div[@data-testid="profileHeaderBanner"]'), "style")
            return extract_first(r'url\("([^"]+)"\)', style)

    def _save_csv(self, username: str, data: dict):
        file_path = os.path.join(self.save_dir, f"{username}.csv")
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writeheader()
            writer.writerow(data)
        print(f"✅ Profile data saved to {file_path}")