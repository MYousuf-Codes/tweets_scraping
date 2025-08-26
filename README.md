
# You can run the scraper in multiple ways:

## Scrape all available tweets for a hashtag `genai`
`python main.py genai`

## Scrape a limited number of tweets
`python main.py genai --limit 50`

## scrape and save into custom CSV
`python main.py genai --limit 200 --output genai_tweets.csv`

## scrape with headless browser, by default it opens browser
`python main.py genai --headless`

## originator's profile will be saved by default as
`profile.csv`

### used @staticmethod in this script as, then we don't need to create object instances like other varibales to access the object with `self` or `cls`