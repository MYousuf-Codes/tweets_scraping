from selenium import webdriver

class BaseScraper:
    def __init__(self, headless: bool = True):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(options=options)

    def close(self):
        self.driver.quit()
