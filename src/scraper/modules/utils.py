from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from requests import get

def get_selenium(url, driver):
    driver.get(url)

    print('Trying to get page.')

    unloaded = False

    while unloaded is False:
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@class='post-content']//* | //h1[@class='post-title']//text()"))
            )
            unloaded = True
            print('Successfully loaded page content.')
        except TimeoutError:
            driver.refresh()
            print('Trying to load page again.')

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

def get_img(img_url, img_directory, img_description=None):

    src = get(img_url)

    img_filename = img_url.split('/')[-1]

    img_path = ''.join([img_directory, img_filename])

    save_file(src.content, img_path, write_mode = 'wb+', filetype='img')

    ## TODO: add img filename to list of images.
    ## TODO: insert html code for img into the chapter text.

    img_html = f'<img src="{img_filename}" alt="{img_description}"></img>'

    print(f'Retrieved img: {img_filename}')
    return img_html

def translate(text):
    pass # TODO: create translate function

def open_file(path):
    with open(path, 'rb', encoding='utf8') as f:
        return f.read()

def save_file(data, path, write_mode = 'wb', encoding = None, filetype = 'text'):
    if filetype == 'text':
        encoding = 'utf8'
        with open(path, write_mode, encoding= encoding) as f:
            f.write(data)
    elif filetype == 'img':
        with open(path, write_mode) as f:
            f.write(data)



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