import pandas as pd

class OriginatorFinder:
    @staticmethod
    def find_originator(df: pd.DataFrame):
        # Change the "post_time" column into real date/time values
        s = pd.to_datetime(df["post_time"], errors="coerce")

        # Add a new hidden column "_pt" with the date/time values
        df = df.assign(_pt=s)

        # Remove rows where "_pt" is empty or not valid
        df = df.dropna(subset=["_pt"])

        # Sort the rows by time (oldest first), and pick the very first one
        first = df.sort_values("_pt", ascending=True).iloc[0]

        # Return the main details of that very first tweet
        return {
            "user_handle": first.get("user_handle"),  # the @username
            "profile_url": first.get("profile_url"),  # link to the profile
            "tweet_id": first.get("tweet_id"),        # tweet ID
            "tweet_url": first.get("tweet_url"),      # link to the tweet
            "post_time": first.get("post_time"),      # when it was posted
        }
