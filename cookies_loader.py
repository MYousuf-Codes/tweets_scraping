import json, os

class CookiesLoader:
    @staticmethod
    def load_cookies(driver, path):
        # Check if the cookies file exists, if not, stop and raise error
        if not os.path.exists(path):
            raise FileNotFoundError("No cookies file found. Run save_cookies.py first.")

        # Open the cookies file and read  data
        with open(path, "r", encoding="utf-8") as f:
            cookies = json.load(f)

        # First open x.com
        driver.get("https://x.com/")

        # Add each cookie one by one with for loop
        for cookie in cookies:
            cookie["domain"] = ".x.com"  # make sure cookie from this domain x.com (not from another opened website/tab)

            # Selenium needs expiry as an integer, not float
            if "expiry" in cookie and isinstance(cookie["expiry"], float):
                cookie["expiry"] = int(cookie["expiry"])

            try:
                driver.add_cookie(cookie)  # add cookie into browser
            except Exception as e:
                print("⚠️ Skipped cookie:", cookie.get("name"), e)  # if fails, then just skip

        # Reload the page with cookies now applied
        driver.refresh()
        print("✅ Cookies loaded.")
