####### Standard Library Imports #######
from re import sub
from types import NoneType
import logging
import sys

####### external imports

from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, InvalidSelectorException
from requests_html import HTMLSession

####### internal imports

import modules.utils
import modules.constants

################################ !Initializing logging module #################################


################################ !Functions #####################################

## TODO: Add docstring
def get_chapter(url, driver=None, backup_dir=None, password='', log=''):
    wait = WebDriverWait(driver, 30)

    try_again = True
    quit_loop = False
    while try_again:
        try:
            try_again = False
            ## Open new browser if one isn't already available
            if driver is None:
                init_selenium = modules.utils.init_selenium(url)
                driver = init_selenium[0]
                chapter_etree = etree.HTML(driver.page_source)

            elif 'knoxt' in url:
                session = modules.utils.get_with_requests(url)
                session_html = session.html.html
                chapter_etree = etree.HTML(session_html)

            elif 'wattpad' in url:
                driver.get(url)
                chapter_etree = etree.HTML(driver.page_source)

            ## Else continue with the current instance of driver
            else:
                unloaded = False

                while unloaded is False:
                    try:
                        log.debug("Attempting unload of chapter page...")

                        ## If the url is a redirect, use requests-html to retrieve the end URL after redirect.
                        if 'novelupdates' in url:
                            r = HTMLSession.get(url)
                            url = r.url
                            driver.get(url)

                        elif driver.find_elements(By.XPATH, '//h1[text()="Sensitive Content Warning"]'):
                            driver.find_element(By.XPATH, '//a[text()="I UNDERSTAND AND I WISH TO CONTINUE"]').click()
                            wait.until(EC.presence_of_element_located(By.XPATH, '//div[@class="post"]/div/p'))

                        else:
                            quit_loop = modules.utils.get_selenium(url, driver)
                            if quit_loop:
                                break

                        unloaded = True

                    except TimeoutException:
                        log.error(f"Timeout Error while attempting unload of {url}. Refreshing...")
                        driver.refresh()
                        
                if quit_loop:
                    break
                
                site_body = driver.find_element(By.CSS_SELECTOR, "div.post-body, div.entry-content, div#novel-content, div.epcontent")
                chapter_etree = etree.HTML(driver.page_source)
                content_body = etree.HTML(site_body.get_attribute("innerHTML"))

            # Unlock site if locked
            driver = modules.utils.unlock_site(driver, chapter_etree, password)

            # Get chapter title/subtitle/filename
            chapter_info = modules.utils.get_chapter_info(driver, chapter_etree, url)

            chapter_title = chapter_info[0]
            chapter_subtitle = chapter_info[1]
            chapter_filename = chapter_info[2]

            # Get chapter_elements
            log.info("Obtaining chapter_elements.")

            if 'wattpad' in url:
                modules.utils.wattpad_scroll_down(driver)
                chapter_etree = etree.HTML(driver.page_source)
                chapter_elements = chapter_etree.cssselect("div.page p")
            else:
                chapter_elements = content_body.cssselect("p")
            
            ## Creating empty variables
            chapter_html_list = []
            footer = ''
            footer_content = []
            footnote_number = 00

            # create backup_directory
            if backup_dir is not None:
                img_dir = f'{backup_dir}images/'
            

            log.debug("Beginning parse of chapter elements...")
            for current_element in chapter_elements:
                element_content = ''

                if current_element.tag == 'a':
                    chapter_html_list = modules.utils.append_a_element(current_element, chapter_html_list, img_dir)

                elif current_element.tag in ['p', 'span']:
                    chapter_html_list = modules.utils.append_p_or_span(driver, wait, chapter_etree, current_element, chapter_html_list, element_content, footer_content)

                ## TODO: proper handling of img tags
                elif current_element.tag == 'hr':
                    chapter_html_list.append('<hr/>')

                elif current_element.tag == 'div':
                    continue

                elif current_element.cssselect('span'):
                    for bit_of_text in current_element.cssselect('span[face*="Arial"][face*="sans-serif"]'):
                        if bit_of_text.text not in modules.constants.no_no_list:
                            text_to_add = f'<p>{bit_of_text.text}'
                            if bit_of_text.tail not in modules.constants.no_no_list:
                                chapter_html_list.append(f'{text_to_add}{bit_of_text.tail}</p>')

                            else:
                                chapter_html_list.append(f'{text_to_add}</p>')

        except Exception as e:
            log.error(f"Exception: {e}")
            if driver is not None:
                driver.quit()
                driver = None
                
            try_again = True

        if quit_loop:
            break

    if quit_loop:
        pass

    else:
        # Creates and saves the html for the chapter.
        modules.utils.create_chapter_html_file(chapter_html_list, chapter_title, chapter_subtitle, footer_content, backup_dir, chapter_filename)

        return chapter_filename
