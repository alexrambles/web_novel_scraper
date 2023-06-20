####### external imports

from lxml import etree
from re import sub
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, InvalidSelectorException
from types import NoneType
from requests_html import HTMLSession
from time import time
from unicodedata import normalize
import logging
import sys

####### internal imports

import modules.utils, modules.constants

################################ !Initializing logging module #################################

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


################################ !Functions #####################################

def get_chapter(url, driver=None, backup_dir=None, password=''):

    try_again = True
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
            ## Else continue with the current instance of driver
            else:
                unloaded = False

                wait = WebDriverWait(driver, 30)

                while unloaded is False:
                    try:
                        log.debug("Attempting unload of chapter page...")
                        
                        ## If the url is a redirect, use requests-html to retrieve the end URL after redirect.
                        if 'novelupdates' in url:
                            r = HTMLSession.get(url)
                            url = r.url
                            driver.get(url)
                        else:
                            modules.utils.get_selenium(url, driver)
                            
                        unloaded = True

                    except TimeoutException:
                        log.error(f"Timeout Error while attempting unload of {url}. Refreshing...")
                        driver.refresh()
                chapter_etree = etree.HTML(driver.page_source)
            
            
            ## ! Check if site is locked
            if chapter_etree.xpath("//*[@id= 'site-pass']"):
                driver = modules.utils.unlock_site(driver, password)
            
            if chapter_etree.xpath('/html/body/center/h1[.="502 Bad Gateway"]'):
                log.error( f'ERROR: {url} encountered a bad gateway. Retrying the request.')
                driver.refresh()
            elif 'knoxt' in url:
                log.debug(f'Knoxt in url: {url}. Getting chapter name and title.')
                chapter_title = chapter_etree.xpath("//div[@class='epheader']/h1/text() | //h1[@class='page-title']//text() | //header/h1[@class='h2']/text() | //*[@class = 'chapter-title']/text()")[0]
                chapter_subtitle = chapter_etree.xpath("//div[@class='epheader']/div[@class='cat-series']/text()")
            else:
                log.debug("No specific website detected. Obtaining chapter title and subtitle.")
                chapter_title = chapter_etree.xpath("//h1[@class='page-title']//text() | //header/h1[@class='h2']/text() | //*[@class = 'chapter-title']/text()")[0]
                chapter_subtitle = ''

            if ":" in chapter_title:
                log.debug(f"Cleaning chapter title.")
                chapter_name_list = chapter_title.split(':')

                for i in chapter_name_list:
                    if "chapter" in i.lower():
                        chapter_title = i.replace('\n', '').strip()

                    elif len(i) >5:
                        chapter_subtitle = i.replace('\n', '').strip()

            chapter_filename = sub(r'[^\w\&]', '_', chapter_title).replace('&', 'and').strip('_').lower()
            log.debug("Obtaining chapter_elements.")
            chapter_elements = chapter_etree.xpath("//div[@class='post-content']//* | //div[@id='novel-content']//* | //div[contains(@class, 'epcontent')]/p")

            chapter_html_list = []
            chapter_html = ''
            footer = ''
            footer_content = []
            footnote_number = 00
            
            if backup_dir is not None:
                img_dir = f'{backup_dir}images/'
            
            if 'wattpad' in url:
                modules.utils.wattpad_scroll_down(driver)
                ##modules.utils.scroll_down(driver, '//div[contains(@class, "last-page")]')
                chapter_etree = etree.HTML(driver.page_source)
                chapter_elements = chapter_etree.xpath('//div[contains(@class, "page")]//p')

            log.debug("Beginning parse of chapter elements...")
            for element in chapter_elements:
                element_content = ''
                
                if element.tag == 'p':
                    if element.xpath('.//em | .//strong | .//sup | .//i | .//b | .//span[@class="tooltip-toggle"] | .//span[@class="tooltip"] | .//span[@role="tooltip"] | .//span[@style="text-decoration: underline"] | .//span[@style = "font-weight: 400"]'):
                        if element.text is not None and element.text not in modules.constants.no_no_list:
                            element_content += element.text

                        for i in element.xpath('.//em | .//strong | .//sup | .//i | .//b | .//span[@class="tooltip-toggle"] | .//span[@class="tooltip"] | .//span[@role="tooltip"] | .//span[@style="text-decoration: underline"] | .//span[@style = "font-weight: 400"]'):
                            if i in element.xpath('.//span[@class="tooltip-toggle"]'):     
                                footnote_number += 1                   
                                tooltip_id = i.attrib['tooltip-target']
                                element_content += f'{element_content}<a epub:type = "noteref" href="#{tooltip_id}" id = "fn{footnote_number}">{i.text}</a>'
                                
                                if i.tail is not None:
                                    element_content += f'{element_content}{i.tail}'
                                
                                if not driver.find_elements_by_id(tooltip_id):
                                    try:
                                        driver.find_element_by_xpath(f"//span[contains(., '{i.text}')]").click()
                                        
                                    except ElementClickInterceptedException:
                                        driver.find_element_by_xpath('//div[contains(@class, "cookie-consent")]//button').click()
                                        driver.find_element_by_xpath(f"//span[contains(., '{i.text}')]").click()
                                        driver.implicitly_wait(1)
                                        
                                    except InvalidSelectorException:
                                        driver.find_element_by_xpath(f'//span[contains(., "{i.text}")]').click()
                                        
                                    wait.until(EC.element_to_be_clickable((By.XPATH, f'//div[@id="{tooltip_id}"]')))
                                    
                                    chapter_etree = etree.HTML(driver.page_source)
                                    
                                # TODO: Can we take out the 'Translator's Note' bit and put the actual text being explained instead?
                                tooltip_p = chapter_etree.xpath(f'//div[@id="{tooltip_id}"]/*')[0]
                                tooltip = f'<p><a href = "#fn{footnote_number}" id="{tooltip_id}"><strong>{i.text}</strong></a> -- {tooltip_p.tail}</p>'
                                footer_content.append(f'<div epub:type="footnote" class="tooltip">{tooltip}</div>')
                            
                            elif i in element.xpath('.//span[@style="text-decoration: underline"]'):
                                element_content += f'<u>{i.text}</u>'
                                    
                            elif i.get('role') == 'tooltip':
                                tooltip = f'<a href = "#fn{footnote_number}" id="footnote{footnote_number}">{footnote_number}</a> -- {i.text}'
                                footer_content.append(f'<div epub:type="footnote" class="tooltip">{tooltip}</div>')
                            
                            elif i.tag == 'sup':
                                footnote_number += 1
                                i_content = i.xpath('./a')[0]
                                element_content += f'<sup><a epub:type = "noteref" href="#footnote{footnote_number}" id="fn{footnote_number}">{i_content.text}</a></sup>'
                                
                                if i.tail is not None:
                                    element_content += i.tail
                                    
                            elif i.get('style') == 'font-weight: 400' and i.text not in modules.constants.no_no_list:
                                element_content += i.text

                            if i.tail not in modules.constants.no_no_list:
                                if element_content[-len(i.tag)+1:] == i.tag + '>':
                                    element_content = element_content[:-len(i.tag)-1]
                                    element_content += f'{i.text}</{i.tag}>{i.tail}'

                                elif i.text not in modules.constants.no_no_list and i.text not in '\t'.join(footer_content):
                                    element_content += f' <{i.tag}>{i.text}</{i.tag}>{i.tail}'
                                    
                                else:
                                    element_content = f'{element_content}{i.tail}'

                            else:
                                if element_content[-len(i.tag)+1:] == i.tag + '>':
                                    element_content = element_content[:-len(i.tag)-1]
                                    element_content += f'{i.text}</{i.tag}>'

                                elif i.text not in modules.constants.no_no_list and i.text not in element_content and (i.text != None or i.tail != None):
                                    element_content += f' <{i.tag}>{i.text}</{i.tag}>'

                        if element_content not in footer_content and element.tail is not None and element.tail not in modules.constants.no_no_list:
                            element_content = f'{element_content}{element.tail}</p>'

                    elif element.text is not None and element.text not in modules.constants.no_no_list:
                        element_content = element.text
                        
                    if type(element_content) is NoneType:
                        pass
                    
                    elif element_content not in chapter_html_list and element_content not in modules.constants.no_no_list:
                        chapter_html_list.append(f'<p>{element_content}</p>')

                elif element.tag == 'a':
                    if element.get('href') is not None and element.get('href')[-4:] in modules.constants.img_suffixes:
                        if element.xpath("*[contains(@*, 'description')]"):
                            img_description = element.xpath("@*[contains(., 'description')]")[0].text
                            img_html = modules.utils.get_img(element.get('href'), img_dir, img_description)

                            chapter_html_list.append(img_html)

                        else:
                            img_html = modules.utils.get_img(element.get('href'), img_dir)
                            chapter_html_list.append(img_html)

                    else:
                        continue

                ## TODO: code in handling of img tags

                elif element.tag == 'hr':
                    chapter_html_list.append('<hr/>')

                elif element.tag == 'div':
                    continue

        except TimeoutException:
            log.warning(f'Had to refresh url {url}')
            try_again = True
            driver.refresh()

    chapter_text = ''.join(chapter_html_list)
    
    if footer_content != []:
        footer = f'<div id="footer" class = "footer">{"<br>".join(footer_content)}</div>'

    chapter_html = f'<article id="{chapter_filename}_body">{chapter_text}</article>'
    
    chapter_html = f'<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang = "en" xml:lang="en"><head><title style="display:none;">{chapter_title}</title></head><body epub:type="chapter"><div epub:type="bodymatter"><div><h1 epub:type="title" id="{chapter_filename}">{chapter_title}</h1><h2 epub:type="subtitle">{chapter_subtitle}</h2>{chapter_html}</div>{footer}</div></body></html>'

    modules.utils.save_file(chapter_html, f'{backup_dir}{chapter_filename}.html', write_mode='w+')

    return chapter_filename
