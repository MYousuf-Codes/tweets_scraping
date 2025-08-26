
# Run this script in mulitple ways:

## scrape 50 tweets for #ai
`python main.py ai --limit 50`

## scrape all available tweets for #openai
`python main.py openai`

## scrape and save into custom CSV
`python main.py football --limit 200 --output football_tweets.csv`


### used @staticmethod in this script as, then we don't need to create object instances like other varibales to access the object with `self` or `cls`