####### external imports

from lxml import etree
from re import sub
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from types import NoneType
from requests_html import HTMLSession

####### internal imports

import modules.utils, modules.constants

# ! Functions

def get_chapter(url, driver=None, backup_dir=None):

    ## Open new browser if one isn't already available
    if driver is None:
        init_selenium = modules.utils.init_selenium(url)
        driver = init_selenium[0]
        wait = init_selenium[1]

    ## Else continue with the current instance of driver
    else:
        unloaded = False

        wait = WebDriverWait(driver, 10)

        while unloaded is False:
            try:
                element = wait.until( EC.presence_of_all_elements_located(( By.XPATH, "//div[@class='post-content']//p" )) )

                ## If the url is a redirect, use requests-html to retrieve the end URL after redirect.
                if 'novelupdates' in url:
                    r = HTMLSession.get(url)
                    url = r.url
                    driver.get(url)

                else:
                    driver.get(url)

                unloaded = True

            except TimeoutException:
                driver.refresh()
                print('Trying to reload page.')


    chapter_etree = etree.HTML(driver.page_source)

    chapter_title = chapter_etree.xpath("//h1[@class='page-title']//text()")[0]

    chapter_subtitle = ''

    if ":" in chapter_title:
        chapter_name_list = chapter_title.split(':')

        for i in chapter_name_list:
            if "chapter" in i.lower():
                chapter_title = i.strip()

            elif len(i) >5:
                chapter_subtitle = i.strip()

    chapter_filename = sub(r'[^\w\&]', '_', chapter_title).replace('&', 'and').lower()

    chapter_elements = chapter_etree.xpath("//div[@class='post-content']//*")

    chapter_html_list = []

    chapter_html = ''

    footer = ''

    if backup_dir is not None:
        img_dir = f'{backup_dir}images/'

    for element in chapter_elements:
        element_content = ''
        if element.tag == 'p':
            if element.xpath('.//em | .//strong | .//sup | .//i | .//b'):
                if element.text is not None:
                    element_content = element.text

                for i in element.xpath('.//em | .//strong | .//sup | .//i | .//b'):

                    if i.tag == 'sup':
                        print('Warning: you have not yet programmed in handling of superscript.')
                        break

                    if i.tail not in modules.constants.no_no_list:
                        if element_content[-len(i.tag)+1:] == i.tag + '>':
                            element_content = element_content[:-len(i.tag)-1]
                            element_content += f'{i.text}</{i.tag}>{i.tail}'

                        else:
                            element_content += f' <{i.tag}>{i.text}</{i.tag}>{i.tail}'

                    else:
                        if element_content[-len(i.tag)+1:] == i.tag + '>':
                            element_content = element_content[:-len(i.tag)-1]
                            element_content += f'{i.text}</{i.tag}>'

                        else:
                            element_content += f' <{i.tag}>{i.text}</{i.tag}>'

                if element.tail is not None and element.tail not in modules.constants.no_no_list:
                    element_content = f'{element_content} {element.tail}'

            elif element.text not in modules.constants.no_no_list:
                element_content = element.text

            if type(element_content) is NoneType:
                pass
            else:
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

    chapter_text = ''.join(chapter_html_list)

    chapter_html = f'<article id="{chapter_filename}_body">{chapter_text}{footer}</article>'

    chapter_html = f'<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang = "en" xml:lang="en"><head><title style="display:none;">{chapter_title}</title></head><body epub:type="chapter"><div epub:type="bodymatter"><div><h1 epub:type="title" id="{chapter_filename}">{chapter_title}</h1><h2 epub:type="subtitle">{chapter_subtitle}</h2>{chapter_html}</div>{footer}</div></body></html>'

    modules.utils.save_file(chapter_html, f'{backup_dir}{chapter_filename}.html', write_mode='w+')

    return chapter_filename
