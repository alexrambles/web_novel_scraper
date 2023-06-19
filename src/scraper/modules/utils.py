from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from requests_html import HTMLSession
from re import sub
import time
import logging


# ! Logging setup
logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s : %(funcName)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# ! Functions
def get_selenium(url, driver):
    log.info("Getting %s with Selenium", url)
    unloaded = False

    while unloaded is False:
        try:
            driver.get(url)

            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(( By.CSS, "div.post-content" )))

            unloaded = True
            log.info("Loaded %(url)s successfully")

        except TimeoutException:
            log.error('Unable to load page content: attempting reload.')
            driver.refresh()

def init_selenium(url, javascript = False):
    log.info('Initializing selenium with url: %(url)s')
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
    options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 2} )
    ##options.add_argument(f"--force-device-scale-factor={desired_dpi}")
    if 'wattpad' in url:
        log.info("Disabling Javascript.")
        pass
    else:
        log.info("Enabling Javascript")
        options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 1} )

    driver = webdriver.Chrome( service = Service(ChromeDriverManager().install()), options=options )

    wait = WebDriverWait( driver, 60 )

    driver.get( url )

    return [
        driver
        ,wait
        ]

def init_firefox(url):

    firefox_driver = webdriver.Firefox(service = Service(GeckoDriverManager().install()))

    return firefox_driver

def get_img(img_url, img_directory, img_description=None):
    log.info("Getting img from %(img_url)s")

    session = HTMLSession()

    src = session.get(img_url)

    img_filename = img_url.split('/')[-1].split('.')[0]

    if img_description == 'cover_img':
        img_filename = 'cover'

    else:
        pass

    img_path = ''.join([img_directory, img_filename, '.jpg'])

    save_file(src.content, img_path, write_mode = 'wb+', filetype='img')

    ## TODO: add img filename to list of images.
    ## TODO: insert html code for img into the chapter text.

    img_html = f'<img src="./images/{img_filename}.jpg" alt="{img_description}"></img>'

    log.info("Retrieved %(img_filename)s. Returning img HTML.")
    return img_html

def translate(text):
    pass # TODO: create translate function

def scroll_down(driver, element_awaited_xpath):
    last_page = False

    while last_page is False:
        try:
            driver.find_element_by_xpath(element_awaited_xpath)
            last_page = True
            
        except NoSuchElementException:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
def wattpad_scroll_down(driver):
    item_presence = False
    while item_presence is False:
        ## last_window_height = driver.execute_script( "return document.body.scrollHeight" )
        print("Scrolling down")
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        next_button = driver.find_elements(By.XPATH, "//a[text()='Continue to next part']" )

        load_more = driver.find_elements(By.XPATH, "//a[.='Load More Pages']")

        time.sleep(1)
        
        if len(load_more) != 0 and "hidden" not in load_more[0].get("class"):
            continue
        
        elif len(next_button) != 0 or len(driver.find_elements(By.XPATH, '//div[contains(@class, "last-page")]//pre//p')) > 0:
            if item_presence:
                pass
            else:
                item_presence = True
                continue
            
        elif len(driver.find_elements(By.XPATH, '//div[@id="story-part-navigation"]/div[@class="message"]/div[@class="top-message"]')) > 0 and "🎉 You've finished reading " in driver.find_elements(By.XPATH, '//div[@id="story-part-navigation"]/div[@class="message"]/div[@class="top-message"]')[0].text:
            item_presence = True
            continue

def open_file(path, read_method = 'r'):
    if 'b' in read_method:
        with open(path, read_method) as f:
            return f.read()
    else:
        encoding = 'utf-8'
        with open(path, read_method, encoding) as f:
            return f.read()

def save_file(data, path, write_mode = 'wb', encoding = None, filetype = 'text'):
    if filetype == 'text':
        encoding = 'utf8'
        with open(path, write_mode, encoding= encoding) as f:
            f.write(data)
    elif filetype == 'img':
        with open(path, write_mode) as f:
            f.write(data)
            
def chrysanthemum_descramble_text(cipher):
    cipher = str(cipher)
    plain = ""
    lower_fixer = "tonquerzlawicvfjpsyhgdmkbx"
    upper_fixer = "JKABRUDQZCTHFVLIWNEYPSXGOM"
    for ch in cipher.strip():
        if ch in [
            "Σ",
            "△",
            "|",
            "β",
            "з",
            "ç",
            "=￣ω￣='",
            ":",
            "ω",

            'à','á','ā','ǎ',
            "è","é","ē",
            "î","ï",'í','ì','ī',
            'ǒ','ō',"ô",
            "ū",'ú',
        ]:
            plain = ''.join([plain, ch])
        elif not ch.isalpha():
            plain = ''.join([plain, ch])
        elif ch.islower():
            plain = ''.join([plain, lower_fixer[ord(ch) - ord("a")]])
        elif ch.isupper():
            plain = ''.join([plain, upper_fixer[ord(ch) - ord("A")]])
        else:
            plain = ''.join([plain, ch])

    return plain

def unlock_site(driver, password):
            password_input = driver.find_element("id", "site-pass")
            password_input.send_keys(password)

            driver.find_element("id", "password-lock").submit()

            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[@id='novel-content']")
                )
            )
            
def logging_module():

    
    def func():
        log.critical('A Critical Error!')
        log.debug('A Debug Error!')
            
def get_novelupdates_data(novel_title, get_cover = True, novelupdates_toc = True):
    session = HTMLSession()

    search_query = sub(r'[^\w ]', '', novel_title).strip().replace(' ', '-').lower()

    r = session.get(f'https://www.novelupdates.com/series/{search_query}')

    if get_cover:
        try:
            novel_cover_url = r.html.xpath('//*[@class="wpb_text_column"]//img/@src')[0]

        except IndexError:
            novel_cover_url = r.html.xpath('//*[@class="seriesimg"]//img/@src')[0]

    else:
        novel_cover_url = ''


    ## Novel info variables
    author_name = r.html.find('a#authtag.genre', first=True).text
    novel_genres = r.html.xpath('//div[@id="seriesgenre"]/a[@class="genre"]/text()')
    novel_tags = r.html.xpath('//div[@id="showtags"]/a/text()')
    novel_summary_list = r.html.xpath('//div[@id="editdescription"]//p/text()')
    novel_summary = ' '.join(novel_summary_list)
    novel_toc = []

    if novelupdates_toc == True:

        ## ! Pagination for TOC
        last_pagination_link = r.html.xpath('//div[contains(@class, "digg_pagination")]/a[3]/@href', first=True)

        if 'novelupdates.com' in last_pagination_link:
            pagination_query = last_pagination_link.replace(f'https://www.novelupdates.com/series/{search_query}/', '')

        else:
            pagination_query = last_pagination_link[2:]

        num_of_paginated_pages = pagination_query.replace('?pg=', '').replace('#myTable', '')
        unredirected_chapter_links = [link[2:] for link in r.html.xpath('//*[@id="myTable"]//a[@class="chp-release"]/@href')]
        chapter_titles = r.html.xpath('//*[@id="myTable"]//a[@class="chp-release"]/text()')

        chapter_links = []

        for link in unredirected_chapter_links:
            r = session.get('http://' + link)
            chapter_links.append(r.url)

        ## ! handle redirects for automating pagination
        for page_num in range(int(num_of_paginated_pages)+1):
            unredirected_chapter_links = []
            r = session.get(f'https://www.novelupdates.com/series/{search_query}/?pg={page_num}#myTable')
            [unredirected_chapter_links.append(link[2:]) for link in r.html.xpath('//*[@id="myTable"]//a[@class="chp-release"]/@href')]

            for link in unredirected_chapter_links:
                r = session.get('http://' + link)
                chapter_links.append(r.url)

        ## ! Check if list is in order
        if sorted(chapter_titles) == chapter_titles:
            pass
        else:
            ## reverse the list to be in numerical order
            chapter_links.reverse()

    else:
        chapter_links = ''
    
    return [
    chapter_links
    ,author_name
    ,novel_genres
    ,novel_tags
    ,novel_summary
    ,novel_cover_url
    ]

##    book.add_metadata("DC", "description", novel_summary)
##    for i in novel_tags:
##        book.add_metadata("DC", "subject", i)
##    print("Metadata added.")

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