import json, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument("--start-maximized")
driver = webdriver.Chrome(options=opts)

driver.get("https://x.com/login")
print("👉 Please log in manually in the browser window...")
time.sleep(60)  # this time gives 1 min to log in

# here I used file handling to save cookies, so you don't have to log in every time
# and also gets the fresh cookies every login time, not expired ones
cookies = driver.get_cookies()
with open("twitter_cookies.json", "w", encoding="utf-8") as f:
    json.dump(cookies, f, indent=2)

print("✅ Cookies saved to twitter_cookies.json")
driver.quit()
