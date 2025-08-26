# main.py
import argparse
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from cookies_loader import CookiesLoader
from search_scraper import SearchScraper
from csv_handler import CSVHandler
from originator_finder import OriginatorFinder
from profile_scraper import ProfileScraper


def run(hashtag: str, limit: Optional[int] = None, out_csv: str = "tweets.csv", headless: bool = False):
    """Scrape tweets for a hashtag, save to CSV, find originator, and scrape profile."""
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
    else:
        opts.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=opts)

    try:
        #  Authentication with cookies
        CookiesLoader.load_cookies(driver, "twitter_cookies.json")

        # Search + scrape tweets
        search = SearchScraper(driver)
        tweets = search.search_hashtag(hashtag, limit=limit)

        # Save CSV
        CSVHandler.save_to_csv(tweets, out_csv)
        print(f"[OK] Saved {len(tweets)} rows -> {out_csv}")

        # Find originator (earliest post_time)
        df = CSVHandler.load_from_csv(out_csv)
        origin = OriginatorFinder.find_originator(df)
        print("[OK] Originator candidate:", origin)

        # Scrape originator profile
        prof = ProfileScraper(driver).scrape_profile(origin["profile_url"])
        print("[OK] Originator profile data:")
        for k, v in prof.items():
            print(f"  - {k}: {v}")

    finally:
        driver.quit()

# here the configuration for running this script
def main():
    parser = argparse.ArgumentParser(
        description="Twitter/X Hashtag Scraper: Scrape tweets, find originator, and extract profile data."
    )
    parser.add_argument("hashtag", help="Hashtag to scrape (without the #)")
    parser.add_argument(
        "-l", "--limit", type=int, default=None,
        help="Limit number of tweets (default: scrape all available)"
    )
    parser.add_argument(
        "-o", "--output", default="tweets.csv",
        help="Output CSV filename (default: tweets.csv)"
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="Run Chrome in headless mode (no visible browser window)"
    )

    args = parser.parse_args()
    run(args.hashtag, args.limit, args.output, args.headless)


if __name__ == "__main__":
    main()
