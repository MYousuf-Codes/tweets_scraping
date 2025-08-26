import pandas as pd

COLUMNS = [
    "tweet_url","tweet_id","user_handle","profile_url",
    "content","hashtags","post_time","scrape_time",
    "likes","comments","reposts","views"
]

class CSVHandler:
    @staticmethod
    def save_to_csv(data, filename="tweets.csv"):
        df = pd.DataFrame(data)
        # consistent columns
        for col in COLUMNS:
            if col not in df.columns: df[col] = None

        # even if data is not scraped in proper format by columns, 
        # but will be saved in the proper format of columns
        df = df[COLUMNS]
        
        df.to_csv(filename, index=False, encoding="utf-8")

    @staticmethod
    def load_from_csv(filename="tweets.csv"):
        return pd.read_csv(filename)
