####### Standard Library Imports #######

import logging
import sys
from re import M, sub, search

####### Third Party Imports #######

from lxml import etree
from requests_html import HTMLSession

####### Local Imports #######

import modules.utils
import modules.constants

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


################################ !Functions #########################################


# TODO: Add documentation for the functions with docstrings.
# TODO: Can I break get_toc up into smaller functions?
def get_toc(url, novelupdates_data, novelupdates_toc, novelupdates_cover = True):
    log.info(f"get_toc( url = {url}, novelupdates_data = {novelupdates_data}, novelupdates_toc = {novelupdates_toc}, novelupdates_cover = {novelupdates_cover}")
    try:
        log.debug('Initiating get_toc')
        ##test if pg can be pulled with requests, if not then try selenium?
        ##			write a test to see if you can use requests or selenium is needed

        if 'wattpad' in url or 'knoxt' in url:
            javascript = True
        else:
            javascript = False

        if 'novelupdates' in url:
            driver = modules.utils.init_selenium(url)[0]
            session = HTMLSession()
            r = session.get(url)
            log.debug('Pulling all information from Novelupdates...')
            novel_website = 'NovelUpdates'
            novel_title = r.html.xpath('//div[@class="seriestitlenu"]/text()')[0]
            novel_filename = sub(r'[\W\&\(\)]', '_', novel_title).lower()
            novel_author = r.html.xpath('//a[@id="authtag"]/text()')[0]
            author_alias = ''
            novel_genres = r.html.xpath('//div[@id="seriesgenre"]/a/text()')
            novel_tags = r.html.xpath('//div[@id="showtags"]/a/text()')
            novel_summary = ' '.join(r.html.xpath('//div[@id="editdescription"]/p/text()'))
            novel_cover_url = r.html.xpath('//*[@class="wpb_text_column"]//img/@src')[0]
            
            ## ! Pagination for TOC
            log.debug('Getting novelupdates toc...')
            last_pagination_link = r.html.xpath('//div[contains(@class, "digg_pagination")]/a[3]/@href', first=True)

            if 'novelupdates.com' in last_pagination_link:
                pagination_query = last_pagination_link.replace(url, '')
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
                r = session.get(f'{url}?pg={page_num}#myTable')
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
            init_selenium = modules.utils.init_selenium(url, javascript)
            driver = init_selenium[0]
            toc_page_source = etree.HTML(driver.page_source)

            toc_synonyms = [
                'Table of Contents'
                ,'TOC'
                ,'Table-of-contents'
                ,'Table-of-Contents'
                ]

            try:
                if 'wattpad' in url:
                    novel_website = 'Wattpad'
                else:
                    novel_website = toc_page_source.xpath('//meta[contains(@property, "site_name")]/@content')[0]
            except:
                novel_website = input("I can't figure out where this book is from? What website did you scrape it from?")

            log.info(f"Novel Website: {novel_website}")


            ## ! Novel Title
            
            try:
                uncleaned_novel_title = toc_page_source.xpath('//title')[0].text
                
                if novel_website == 'Wattpad':
                    novel_title = toc_page_source.xpath('//div[@class = "story-info"]/span[@class = "sr-only"]')[0].text
                    if '[' in novel_title:
                        novel_title = novel_title.split(' [')[0]

                elif any([word in uncleaned_novel_title for word in toc_synonyms]):
                    for word in toc_synonyms:
                        uncleaned_novel_title = uncleaned_novel_title.replace(word, '')

                    novel_title = uncleaned_novel_title.replace('[\-]', '').strip()

                if novel_website in uncleaned_novel_title and novel_website != 'Wattpad':
                    novel_title = uncleaned_novel_title.replace(novel_website, '').replace('-', '').strip()

                elif novel_website != 'Wattpad':
                    novel_title = uncleaned_novel_title

                novel_filename = sub(r'[\W\&\(\)]', '_', novel_title).lower()

            except:
                novel_title = input("I'm sorry. I can't find the title of this novel. What is the title?")
                
                log.info(f"Novel title: {novel_title}.\nNovel Filename: {novel_filename}")


            ## ! Author's name
            
            try:
                author_string = toc_page_source.xpath('//p[contains(text(), "Author")] | //p[contains(., "Author")]')[0].text
                
                if author_string == None and toc_page_source.xpath('//p[contains(., "Author")]//*')[0].text != None and toc_page_source.xpath('//p[contains(., "Author")]//*')[0].text != "Author’s Notes:":
                    author_string = toc_page_source.xpath('//p[contains(., "Author")]//*')[0].text
                    author_string = author_string.replace('Author:', '').strip()
                elif author_string == None and toc_page_source.xpath('//p[contains(., "Author")]//*'):
                    for i in toc_page_source.xpath('//p[contains(., "Author")]//*'):
                        if i.text == None:
                            pass
                        elif 'Author:' in i.text or (i.tail != None and 'Author:' in i.tail):
                            if 'Author:' in i.text:
                                author_string = author_string.replace('Author:', '').strip()
                            else:
                                author_string_raw = i.tail.replace('Author:').strip()       
                                
                                if search(r'\p{Han}', author_string_raw):
                                    sub(r'\p{Han}', '', author_string_raw).strip()
                                    
                                    if '(' in author_string_raw:
                                        sub('\(\)', '', author_string_raw).strip()
                                        
                                author_string = author_string_raw
                                
                if author_string != None and ("(" in author_string and ")" in author_string):
                    author_string = author_string.split("(")[0].strip()
                    
                novel_author = author_string
            except:
                logging.error("Could not find novel author. Requesting manual entry.")
                novel_author = input("I'm sorry. I can't find the author's name. Who wrote this book?\n")

            novel_cover_url = ''
            author_alias = ''
            novelupdates_returned = []
            novel_genres = []
            novel_tags = []
            novel_summary = ''
            driver = ''


            ## ! Novelupdates Data
            
            if novelupdates_data == True:
                log.info("Getting data from novelupdates...")
                novelupdates_returned = modules.utils.get_novelupdates_data(novel_title, get_cover = True, novelupdates_toc = novelupdates_toc)
                chapter_links = novelupdates_returned[0]
                chapter_links_length = len(chapter_links)
                log.info(f"Returned a list of {chapter_links_length} chapter links.")
                author_alias = novelupdates_returned[1]
                log.info(f"Returned Author Alias: {author_alias}")
                novel_genres = novelupdates_returned[2]
                log.info(f"Returned Novel Genres: {novel_genres}")
                novel_tags = novelupdates_returned[3]
                log.info(f"Returned Novel Tags: {novel_tags}")
                novel_summary = novelupdates_returned[4]
                log.info(f"Returned novel Summary: {novel_summary}")
            else:
                ## ! Novel Summary
                try:
                    novel_summary = ''

                    synopsis_title_element = toc_page_source.xpath('//*[contains(text(), "Synopsis")] | //*[contains(text(), "Summary")]')[0]

                    if synopsis_title_element.xpath('..')[0].tag == "p":
                        synopsis_title_element = synopsis_title_element.xpath('..')[0]
                        synopsis_list = synopsis_title_element.xpath('./following::*')
                        summary_text_list = []
                        
                        for i in synopsis_list:
                            if i.tag == 'p' and i.text not in modules.constants.no_no_list:
                                try:
                                    summary_text_list.append(i.text)
                                    
                                except:
                                    log.warning(f'Warning: unexpected error in novel_summary_text_list. Cannot append {i.text} to summary.\n')
                                    
                            elif i.tag == 'hr':
                                break

                        novel_summary = " ".join(summary_text_list)

                except:
                    answer = input("I don't see a summary for this book. Would you like to add a summary? Y/N\n")

                    if answer == 'Y':
                        novel_summary = input("Please paste the summary here.\n")

                    else:
                        novel_summary = ''

            ## ? Get Novel TOC?
            if novelupdates_toc == "Y" or novelupdates_toc == "y":
                chapter_links = novelupdates_returned[0]

            else:
                ## ! Get chapter links
                # ## Get a list of chapter links by finding TOC elements and pulling all elements after that.
                if 'chrysanthemum' in novel_website.lower():
                    chapter_links = toc_page_source.xpath('//div[@class="chapter-item"]/a/@href')
                elif 'wattpad' in novel_website.lower():
                    chapter_links = ["http://wattpad.com" + x for x in toc_page_source.xpath("//div[@class=\'story-parts\']//li/a/@href")]
                elif 'knoxt' in novel_website.lower():
                    chapter_links = toc_page_source.xpath("//div[contains(@class, 'eplister')]//ul//li//a/@href")
                    chapter_links = list(reversed(chapter_links))
                else:
                    try:
                        toc_title = toc_page_source.xpath('//*[@class="post-content"]//*[contains(., "Table of Contents") or contains(., "TOC") or contains(., "toc") or contains(., "Table-of-Contents") or contains(., "Table-of-contents")]')[0]

                        chapter_links = toc_title.xpath('./following::a/@href[not(.//text() = "Twitter")]')

                    except:
                        answer = input("I don't see a TOC for this novel. Would you like to supply the first link?\n")

                        if answer == '':
                            return log.debug('Could not locate any chapter links. Ending function.')
                        else:
                            chapter_links.append(answer)

                ## ! Novel Genres
                try:
                    novel_genres_raw = toc_page_source.xpath('//a[@class="series-tag"]/text()')

                    for i in novel_genres_raw:
                        novel_genres.append(i.split(' (')[0])

                except:
                    novel_genres = []

                ## ! Novel Cover
                if novelupdates_cover is True:
                    novel_cover_url = novelupdates_returned[5]

        return [
            novel_filename
            ,novel_title
            ,novel_author
            ,author_alias
            ,novel_genres
            ,novel_tags
            ,novel_summary
            ,chapter_links
            ,novel_cover_url
            ,driver
        ]
        
    except:
        log.warning('ERROR: Something went wrong with accessing the TOC.\n')