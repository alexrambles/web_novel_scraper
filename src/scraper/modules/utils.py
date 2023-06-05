from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

def init_selenium(url):
    browser_header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        "Accept-Language": "en-US, en;q=0.5",
        }

    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--ignore-certificate-errors"),
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    ##options.add_argument("--headless")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    desired_dpi = 3.0
    ##options.add_argument(f"--force-device-scale-factor={desired_dpi}")
    ##options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 2})

    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options=options)

    wait = WebDriverWait(driver, 120)
    
    driver.get(url)

    return [driver, wait]

def init_firefox(url):

    firefox_driver = webdriver.Firefox(service = Service(GeckoDriverManager().install()))

    return firefox_driver

def translate(text):
    pass
def open_file(path):
    with open(path, 'rb') as f:
        return f.read()

def save_file(html, path):
    with open(path, 'wb') as f:
        f.write(html)



##TODO - create functions:

####def scroll_to_bottom():

####def click_next_button():

####def hold_pgdwn():

####def close_footer_ad(xpath):

####def decode_text(text, cipher):

####def get_spine(url):

####def scrape_ch():

####def parse_ch(path):

####def login(url,):