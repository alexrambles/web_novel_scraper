####### external imports

from lxml import etree
from re import M, sub, search, compile

####### internal imports

import modules.utils
import modules.constants


####### function

def get_toc(url, novelupdates_data, novelupdates_toc, novelupdates_cover = True):
    try:
        print('trying to pull toc')
        ##test if pg can be pulled with requests, if not then try selenium?

        ##			write a test to see if you can use requests or selenium is needed

        init_selenium = modules.utils.init_selenium(url)

        driver = init_selenium[0]

        wait = init_selenium[1]

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
            novel_website = print(input("I can't figure out where this book is from? What website did you scrape it from?"))

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
            novel_title = print(input("I'm sorry. I can't find the title of this novel. What is the title?"))

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
            novel_author = print(input("I'm sorry. I can't find the author's name. Who wrote this book?\n"))

        novel_cover_url = ''
        author_alias = ''
        novelupdates_returned = []
        novel_genres = []
        novel_tags = []
        novel_summary = ''

        ## ! Novelupdates Data
        if novelupdates_data == True:
            novelupdates_returned = modules.utils.get_novelupdates_data(novel_title, get_cover = True, novelupdates_toc = novelupdates_toc)

            chapter_links = novelupdates_returned[0]
            author_alias = novelupdates_returned[1]
            novel_genres = novelupdates_returned[2]
            novel_tags = novelupdates_returned[3]
            novel_summary = novelupdates_returned[4]


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
                                print(f'Warning: unexpected error in novel_summary_text_list. Cannot append {i.text} to summary.\n')
                                
                        elif i.tag == 'hr':
                            break

                    novel_summary = " ".join(summary_text_list)

            except:
                answer = print(input("I don't see a summary for this book. Would you like to add a summary? Y/N\n"))

                if answer == 'Y':
                    novel_summary = print(input("Please paste the summary here.\n"))

                else:
                    novel_summary = ''

        ## ? Get Novel TOC?
        if novelupdates_toc == "Y" or novelupdates_toc == "y":
            chapter_links = novelupdates_returned[0]

        else:
            #####
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
                    answer = print(input("I don't see a TOC for this novel. Would you like to supply the first link?\n"))

                    if answer == '':
                        return print('Could not locate any chapter links. Ending function.')
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
        return print('ERROR: Something went wrong with accessing the TOC.\n')