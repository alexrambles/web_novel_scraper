from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from requests_html import HTMLSession
from re import sub

def get_selenium(url, driver):

    unloaded = False

    while unloaded is False:
        try:
            driver.get(url)

            print('Trying to get page.')

            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(( By.CSS, "div.post-content" )))

            unloaded = True

            print('Successfully loaded page content.')

        except TimeoutException:
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
    options.add_argument("--headless")
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

    wait = WebDriverWait(driver, 60)

    driver.get(url)

    return [driver, wait]

def init_firefox(url):

    firefox_driver = webdriver.Firefox(service = Service(GeckoDriverManager().install()))

    return firefox_driver

def get_img(img_url, img_directory, img_description=None):

    session = HTMLSession()

    src = session.get(img_url)

    img_filename = img_url.split('/')[-1]

    if img_description == 'cover_img':
        img_filename = 'cover.jpg'

    else:
        pass

    img_path = ''.join([img_directory, img_filename])

    save_file(src.content, img_path, write_mode = 'wb+', filetype='img')

    ## TODO: add img filename to list of images.
    ## TODO: insert html code for img into the chapter text.

    img_html = f'<img src="./images/{img_filename}" alt="{img_description}"></img>'

    print(f'Retrieved img: {img_filename}')
    return img_html

def translate(text):
    pass # TODO: create translate function

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

def get_novelupdates_data(novel_title, get_cover = True, novelupdates_toc = True):
    session = HTMLSession()

    search_query = sub(r'[^\w ]', '', novel_title).strip().replace(' ', '-').lower()

    r = session.get(f'https://www.novelupdates.com/series/{search_query}')

    if get_cover:
        novel_cover_url = r.html.xpath('//*[@class="wpb_text_column"]//img/@src')[0]

    else:
        novel_cover_url = ''


    ## Novel info variables
    author_name = r.html.find('a#authtag.genre', first=True).text
    novel_genres = r.html.find('div#seriesgenre a.genre.text')
    novel_tags = r.html.find('div#showtags a.text')
    novel_summary_list = r.html.xpath('//div[@id="editdescription"]//p/text()')
    novel_summary = ' '.join(novel_summary_list)
    novel_toc = []

    if novelupdates_toc:

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