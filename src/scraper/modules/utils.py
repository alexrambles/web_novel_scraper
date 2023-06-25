from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, InvalidSelectorException, ElementClickInterceptedException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from requests_html import HTMLSession
from re import sub
import time

import logging
import sys

import modules.constants


################################ Creating logging module #################################

def setup_logging():
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s : %(funcName)s:%(lineno)d] \n %(message)s\n',
        datefmt='%Y-%m-%d:%H:%M:%S')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    log.addHandler(console_handler)

    file_handler = logging.FileHandler('test.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    log.addHandler(file_handler)

    return log

## Initializing logging
log = setup_logging()


################################ ! Functions #################################

def get_with_requests(url):
    session = HTMLSession()
    r = session.get(url)
    return r    
    
def get_selenium(url, driver):
    quit_loop = False
    log.info(f"Getting {url} with Selenium")
    unloaded = False

    while unloaded is False:
        try:
            driver.get(url)

            element = WebDriverWait(driver, 30).until(EC.presence_of_element_located(( By.XPATH, "//div[contains(@class, 'first-page')] | //div[@class='post-content'] | //div[contains(@class, 'entry-content')] | //div[@class='epheader'] | //*[contains(., 'Sensitive Content Warning')]" )))

            unloaded = True
            log.info(f"Loaded {url} successfully")

        except TimeoutException:
            if driver.find_elements(By.CSS_SELECTOR, 'section.error-404'):
                quit_loop = True
                break
                
            else:
                log.error('Unable to load page content: attempting reload.')
                driver.refresh()
    return quit_loop

def init_selenium(url, javascript = False):
    log.info(f'Initializing selenium with url: {url}')
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
    if 'wattpad' not in url and javascript is False:
        log.info("Disabling Javascript.")
        pass
    elif javascript is True:
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
    log.info(f"Getting img from {img_url}")

    session = HTMLSession()
    src = session.get(img_url)
    img_filename = img_url.split('/')[-1].split('.')[0]

    if img_description == 'cover_img':
        img_filename = 'cover'
    else:
        pass

    img_path = ''.join([img_directory, img_filename, '.jpg'])
    save_file(src.content, img_path, write_mode = 'wb+', filetype='img')
    img_html = f'<img src="./images/{img_filename}.jpg" alt="{img_description}"></img>'
    
    log.info(f"Retrieved {img_filename}. Returning img HTML.")
    
    return img_html

def translate(text):
    pass # TODO: create translate function

def scroll_down(driver, element_awaited_xpath):
    log.info("Initializing scroll_down().")
    last_page = False
    while last_page is False:
        try:
            driver.find_element_by_xpath(element_awaited_xpath)
            last_page = True
        except NoSuchElementException:
            logging.error(f"{element_awaited_xpath} not found. Continuing scroll.")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
def wattpad_scroll_down(driver):
    log.info("Initializing wattpad_scroll_down().")
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
            logging.error("Next Chapter button not found. Continuing scroll.")
            continue
        
        elif len(next_button) != 0 or len(driver.find_elements(By.XPATH, '//div[contains(@class, "last-page")]//pre//p')) > 0:
            if item_presence:
                pass
            else:
                log.info('Last page found. Ending scroll.')
                item_presence = True
                continue
            
        elif len(driver.find_elements(By.XPATH, '//div[@id="story-part-navigation"]/div[@class="message"]/div[@class="top-message"]')) > 0 and "🎉 You've finished reading " in driver.find_elements(By.XPATH, '//div[@id="story-part-navigation"]/div[@class="message"]/div[@class="top-message"]')[0].text:
            log.info('Last page found. Ending scroll.')
            item_presence = True
            continue


def open_file(path, read_method = 'r'):
    log.debug('Opening file')
    if 'b' in read_method:
        with open(path, read_method) as f:
            return f.read()
    else:
        encoding = 'utf-8'
        with open(path, read_method, encoding) as f:
            return f.read()


def save_file(data, path, write_mode = 'wb', encoding = None, filetype = 'text'):
    log.debug('Saving file')
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


def unlock_site(driver, chapter_etree, password):
    if chapter_etree.cssselect("#site-pass"):
        log.info("Password encountered. Unlocking site with %(funcName)s...")
        password_input = driver.find_element("id", "site-pass")
        password_input.send_keys(password)

        driver.find_element("id", "password-lock").submit()

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@id='novel-content']")
            )
        )
        return driver
    else:
        return driver

        
def get_chapter_info(driver, chapter_etree, url):
    if chapter_etree.cssselect('h1:contains("502 Bad Gateway")'):
        log.error( f'ERROR: {url} encountered a bad gateway. Retrying the request.')
        driver.refresh()
    elif 'knoxt' in url:
        log.info(f'Knoxt in url: {url}. Getting chapter name and title.')
        chapter_title = chapter_etree.cssselect("div.epheader h1, h1.page-title, header h1.h2, .chapter-title")[0].text
        chapter_subtitle = chapter_etree.cssselect("div.epheader div.cat-series")[0].text
    else:
        log.debug("No specific website detected. Obtaining chapter title and subtitle.")
        chapter_title_element = chapter_etree.cssselect("h1.page-title, header h1.h2, header h3, *.chapter-title, meta[property='og:title']")[0]
        chapter_title = chapter_title_element.text.strip() if chapter_title_element is not None and chapter_title_element.text is not None else chapter_title_element.attrib['content']
        chapter_subtitle = ''

    # Cleanup chapter title in case it includes a reference to novel title.
    if ":" in chapter_title:
        log.info(f"Cleaning chapter title.")
        chapter_name_list = chapter_title.split(':')

        for chapter_name in chapter_name_list:
            if "chapter" in chapter_name.lower():
                chapter_title = chapter_name.replace('\n', '').strip()

            elif len(chapter_name) >5:
                chapter_subtitle = chapter_name.replace('\n', '').strip()

    chapter_filename = sub(r'[^\w\&]', '_', chapter_title).replace('&', 'and').strip('_').lower()
    chapter_info = [chapter_title, chapter_subtitle, chapter_filename]

    return chapter_info


def append_p_or_span(driver, wait, chapter_etree, current_element, chapter_html_list, element_content, footer_content):
    if current_element.cssselect(':has(em), :has(strong), :has(sup), :has(i), :has(b), :has(span)'):
        if current_element.text is not None and current_element.text not in modules.constants.no_no_list:
            element_content += current_element.text

        for current_sub_element in current_element.cssselect('*'):
            if current_sub_element in current_element.cssselect('span.tooltip-toggle'):
                footnote_number += 1
                tooltip_id = current_element.attrib['tooltip-target']
                element_content += f'{element_content}<a epub:type="noteref" href="#{tooltip_id}" id="fn{footnote_number}">{current_element.text}</a>'

                if current_element.tail is not None:
                    element_content += f'{element_content}{current_element.tail}'

                if not driver.find_elements_by_id(tooltip_id):
                    try:
                        driver.find_element_by_css_selector(f'span:contains("{current_element.text}")').click()

                    except ElementClickInterceptedException:
                        driver.find_element_by_css_selector('.cookie-consent button').click()
                        driver.find_element_by_css_selector(f'span:contains("{current_element.text}")').click()
                        driver.implicitly_wait(1)

                    except InvalidSelectorException:
                        driver.find_element_by_css_selector(f'span:contains("{current_element.text}")').click()

                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'div[id="{tooltip_id}"]')))
                    chapter_etree = etree.HTML(driver.page_source)

                # TODO: Can we take out the 'Translator's Note' bit and put the actual text being explained instead?
                tooltip_p = chapter_etree.cssselect(f'div[id="{tooltip_id}"] > *')[0]
                tooltip = f'<p><a href="#fn{footnote_number}" id="{tooltip_id}"><strong>{current_sub_element.text}</strong></a> -- {tooltip_p.tail}</p>'
                footer_content.append(f'<div epub:type="footnote" class="tooltip">{tooltip}</div>')

            elif current_sub_element in current_element.cssselect('span[style="text-decoration: underline"]'):
                element_content += f'<u>{current_sub_element.text}</u>'

            elif current_sub_element.get('role') == 'tooltip':
                tooltip = f'<a href = "#fn{footnote_number}" id="footnote{footnote_number}">{footnote_number}</a> -- {current_sub_element.text}'
                footer_content.append(f'<div epub:type="footnote" class="tooltip">{tooltip}</div>')

            elif current_sub_element.tag == 'sup' and len(current_sub_element.attrib) != 0:
                footnote_number += 1
                current_sub_element_content = current_sub_element.cssselect('a')[0].text
                element_content += f'<sup><a epub:type = "noteref" href="#footnote{footnote_number}" id="fn{footnote_number}">{current_sub_element_content}</a></sup>'

                if current_sub_element.tail is not None:
                    element_content += current_sub_element.tail

            elif current_sub_element.text not in modules.constants.no_no_list:
                if current_sub_element.get('style') is not None and ('font-weight: 400' in current_sub_element.get('style') or 'mso-fareast-font-family:' in current_sub_element.get('style')):
                    element_content += f'<p>{current_sub_element.text}</p>'

                elif 'face' in current_sub_element.attrib:
                    element_content += f'<p>{current_sub_element.text}</p>'

            if current_sub_element.tail not in modules.constants.no_no_list and current_sub_element.tag != 'span':
                if element_content[-len(current_sub_element.tag) + 1:] == f'{current_sub_element.tag}>':
                    element_content = element_content[:-len(current_sub_element.tag) - 1]
                    element_content += f'{current_sub_element.text}</{current_sub_element.tag}>{current_sub_element.tail}'

                elif current_sub_element.text not in modules.constants.no_no_list and current_sub_element.text not in '\t'.join(footer_content):
                    element_content += f' <{current_sub_element.tag}>{current_sub_element.text}</{current_sub_element.tag}>{current_sub_element.tail}'

                else:
                    element_content = f'{element_content}{current_sub_element.tail}'
            else:
                if element_content[-len(current_sub_element.tag) + 1:] == f'{current_sub_element.tag}>':
                    element_content = element_content[:-len(current_sub_element.tag) - 1]
                    element_content += f'{current_sub_element.text}</{current_sub_element.tag}>'

                elif 'face' in current_sub_element.attrib and current_sub_element.tag == 'span' and current_sub_element.text not in modules.constants.no_no_list and current_sub_element.text not in element_content:
                    if i.getparent().tag == 'i' and element_content[-4:] == '</i>':
                        chapter_html_list[:-4].append(f' {current_sub_element.text}</i>')

                    else:
                        chapter_html_list.append(f'<p>{current_sub_element.text}</p>')

                elif current_sub_element.text not in modules.constants.no_no_list and current_sub_element.text not in element_content and (current_sub_element.text is not None or current_sub_element.tail is not None):
                    element_content += f' <{current_sub_element.tag}>{current_sub_element.text}</{current_sub_element.tag}>'

        if element_content not in footer_content and current_element.tail is not None and current_element.tail not in modules.constants.no_no_list:
            element_content = f'{element_content}{current_element.tail}</p>'

    elif current_element.text is not None and current_element.text not in modules.constants.no_no_list:
        element_content = current_element.text

    if element_content is None:
        pass

    elif element_content not in chapter_html_list and element_content not in modules.constants.no_no_list:
        chapter_html_list.append(f'<p>{element_content}</p>')

    return chapter_html_list


def create_chapter_html_file(chapter_html_list, chapter_title, chapter_subtitle, footer_content, backup_dir, chapter_filename):
    try:
        if len(chapter_html_list) < 10 and len(' '.join(chapter_html_list)) < 100:
            raise Exception('Wait--this chapter is too short. Something is wrong. Please check the chapter_html_list.')

    except Exception:
        pass

    chapter_text = ''.join(chapter_html_list)

    chapter_text = chapter_text.replace('.\n', '</p><p>')

    if footer_content != []:
        footer = f'<div id="footer" class = "footer">{"<br>".join(footer_content)}</div>'
    else:
        footer = ''

    chapter_html = f'<article id="{chapter_filename}_body">{chapter_text}</article>'
    chapter_html = f'<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang = "en" xml:lang="en"><head><title style="display:none;">{chapter_title}</title></head><body epub:type="chapter"><div epub:type="bodymatter"><div><h1 epub:type="title" id="{chapter_filename}">{chapter_title}</h1><h2 epub:type="subtitle">{chapter_subtitle}</h2>{chapter_html}</div>{footer}</div></body></html>'
    modules.utils.save_file(chapter_html, f'{backup_dir}{chapter_filename}.html', write_mode='w+')


def append_a_element(current_element, chapter_html_list, img_dir):
    if current_element.get('href') is not None and current_element.get('href')[-4:] in modules.constants.img_suffixes:
        if current_element.cssselect('*[contains(@*, "description")]'):
            img_description = current_element.cssselect('@*[contains(., "description")]')[0].text
            img_html = get_img(current_element.get('href'), img_dir, img_description)
            chapter_html_list.append(img_html)
        else:
            img_html = get_img(current_element.get('href'), img_dir)
            chapter_html_list.append(img_html)
    else:
        pass

    return chapter_html_list

            
def get_novelupdates_data(novel_title, get_cover = True, novelupdates_toc = True):
    log.info("Getting info from Novelupdates.")
    session = HTMLSession()
    search_query = sub(r'[^\w ]', '', novel_title).strip().replace(' ', '-').lower()
    r = session.get(f'https://www.novelupdates.com/series/{search_query}')

    if get_cover:
        try:
            novel_cover_url = r.html.xpath('//*[@class="wpb_text_column"]//img/@src')[0]

        except IndexError:
            log.debug(exec_info=1)
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
        log.debug('Getting novelupdates information...')
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
        log.debug('Handling redirect for automating pagination.')
        for page_num in range(int(num_of_paginated_pages)+1):
            unredirected_chapter_links = []
            r = session.get(f'https://www.novelupdates.com/series/{search_query}/?pg={page_num}#myTable')
            [unredirected_chapter_links.append(link[2:]) for link in r.html.xpath('//*[@id="myTable"]//a[@class="chp-release"]/@href')]

            for link in unredirected_chapter_links:
                r = session.get('http://' + link)
                chapter_links.append(r.url)

        ## ! Check if list is in order
        log.debug('Checking to see if list is in order.')
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

##TODO - create functions:


####def click_next_button():

####def scrape_ch():

####def parse_ch(path):
