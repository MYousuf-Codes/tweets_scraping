import pandas as pd
from originator_finder import OriginatorFinder
from scraper.profile_scraper import ProfileScraper

def run_pipeline(csv_file: str):
    df = pd.read_csv(csv_file)
    originator = OriginatorFinder.find_originator(df)

    print(f"Originator found: {originator['user_handle']} ({originator['profile_url']})")

    scraper = ProfileScraper(originator)
    profile = scraper.scrape_profile()
    scraper.close()

    print(f"Profile saved for {originator['user_handle']}")

if __name__ == "__main__":
    run_pipeline("tweets.csv")
