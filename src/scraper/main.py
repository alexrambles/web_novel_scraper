##global fn for novel info

##fn to pull toc (return list of urls)

##3 methods of iterating thru urls: [pull from novelupdates, pull from website toc, or click "next" button

##when it comes to scraping the actual chapter body text, there are a few websites that will require extra help. CG, Flying Lines, Google Docs, and Wattpad are some of them.

##make a list of possible "next page" synonyms ( or utilize the next pagination support in requests-html)

##after the first page is scraped, if the next url results in a 404 error, switch scraping methods. Maybe reload previous url and switch to press next button method.

##for next button method you can do if the url is the same as the toc url, then select the first chapter to start with, else work with the url you've currently got.

##global variables:
	## ch file list
	## img filenames
	## driver


##          Packages to install         ##
import modules.compile

import logging
import sys


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


################################ !Initializing main module #################################

def main(url):
    log.debug("Starting get_novel.")
    novel_data = modules.compile.get_novel(url, password = 'sdgfjhsdt')
    novel_info = novel_data[0]
    backup_dir = novel_data[1]
    chapter_filename_list = novel_data[2]
    
    log.debug("Starting create_ebook")
    modules.compile.create_ebook(novel_info, "D:/python_projs/proj_save_the_danmei/Books/", chapter_filename_list)

if __name__ == '__main__':
    url = input("Please link to the source you'd like to scrape.  --\n")

    main(url)