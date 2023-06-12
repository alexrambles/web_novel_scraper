####### external imports

from lxml import etree
from re import M, sub, search, compile

####### internal imports

import utils
import constants


####### function

def get_toc(url, novelupdates_data = True, novelupdates_cover = True):
    try:
        print('trying to pull toc')
        ##test if pg can be pulled with requests, if not then try selenium?

        ##			write a test to see if you can use requests or selenium is needed


        ##set up chrome options if using selenium

        init_selenium = utils.init_selenium(url)

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
            novel_website = toc_page_source.xpath('//meta[contains(@property, "site_name")]/@content')[0]

        except:
            novel_website = print(input("I can't figure out where this book is from? What website did you scrape it from?"))

        try:
            uncleaned_novel_title = toc_page_source.xpath('//title')[0].text

            if any([word in uncleaned_novel_title for word in toc_synonyms]):
                for word in toc_synonyms:
                    uncleaned_novel_title = uncleaned_novel_title.replace(word, '')

                novel_title = uncleaned_novel_title.replace('[\-]', '').strip()

            if novel_website in uncleaned_novel_title:
                novel_title = uncleaned_novel_title.replace(novel_website, '').replace('-', '').strip()

            else:
                novel_title = uncleaned_novel_title

            novel_filename = sub(r'[\W\&\(\)]', '_', novel_title).lower()

        except:
            novel_title = print(input("I'm sorry. I can't find the title of this novel. What is the title?"))

        try:

            author_string = toc_page_source.xpath('//p[contains(text(), "Author")]')[0].text

            author_string = author_string.replace('Author:', '').strip()

            if "(" in author_string and ")" in author_string:
                author_string = author_string.split("(")[0].strip()

            novel_author = author_string

        except:
            novel_author = print(input("I'm sorry. I can't find the author's name. Who wrote this book?"))

        novel_cover_url = ''

        if novelupdates_data is True:
            novelupdates_data = utils.get_novelupdates_data(novel_title)

            author_alias = ''
            
            chapter_links = novelupdates_data[0]
            author_name = novelupdates_data[1]
            novel_genres = novelupdates_data[2]
            novel_tags = novelupdates_data[3]
            novel_summary = novelupdates_data[4]

            if author_name != novel_author:
                author_alias = author_name
        elif novelupdates_cover is True:
            novel_cover_url = utils.get_novelupdates_data(novel_title)[5]
        else:
    #######
    # Get novel summary by locating 'synopsis' or 'summary' and pulling all p values after that until you reach an hr element
            try:
                novel_summary = ''

                synopsis_title_element = toc_page_source.xpath('//*[contains(text(), "Synopsis")] | //*[contains(text(), "Summary")]')[0]

                if synopsis_title_element.xpath('..')[0].tag == "p":
                    synopsis_title_element = synopsis_title_element.xpath('..')[0]
                    synopsis_list = synopsis_title_element.xpath('./following::*')
                    summary_text_list = []
                    for i in synopsis_list:
                        if i.tag == 'p' and i.text not in constants.no_no_list:
                            try:
                                summary_text_list.append(i.text)
                            except:
                                print(f'Warning: unexpected error in novel_summary_text_list. Cannot append {i.text} to summary.')
                        elif i.tag == 'hr':
                            break

                    novel_summary = " ".join(summary_text_list)

            except:
                answer = print(input("I don't see a summary for this book. Would you like to add a summary? Y/N"))

                if answer == 'Y':
                    novel_summary = print(input("Please paste the summary here."))
                else:
                    novel_summary = ''

        #####
        ## Get a list of chapter links by finding TOC elements and pulling all elements after that.
            try:
                toc_title = toc_page_source.xpath('//*[@class="post-content"]//*[contains(., "Table of Contents") or contains(., "TOC") or contains(., "toc") or contains(., "Table-of-Contents") or contains(., "Table-of-contents")]')[0]

                chapter_links = toc_title.xpath('./following::a/@href[not(.//text() = "Twitter")]')

            except:
                answer = print(input("I don't see a TOC for this novel. Would you like to supply the first link?"))

                if answer == '':
                    return print('Could not locate any chapter links. Ending function.')
                else:
                    chapter_links.append(answer)

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
        return print('ERROR: Something went wrong with accessing the TOC.')