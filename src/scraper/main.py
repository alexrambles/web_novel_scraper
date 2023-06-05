##global fn for novel info

##fn to pull toc (return list of urls)

##3 methods of iterating thru urls: pull from novelupdates, pull from website toc, or click "next" button

##when it comes to scraping the actual chapter body text, there are a few websites that will require extra help. CG, Flying Lines, Google Docs, and Wattpad are some of them. 

##start by building the simplest utility functions. Scroll to bottom of page. Get rid of cookies box. 

##wattpad--hold down pgdown key until class last-page appears

##make a list of possible "next page" synonyms

##after the first page is scraped, if the next url results in a 404 error, switch scraping methods. Maybe reload previous url and switch to press next button method.

##for next button method you can do if the url is the same as the toc url, then select the first chapter to start with, else work with the url you've currently got.

##global variables:
	## ch file list
	## img filenames
	## driver


##          Packages to install         ##

import modules.toc
import modules.compile
import modules.utils
import modules.constants
		
 
##toc_url = input('Please input the URL to the Table of Contents of your novel.')

set_up_book('https://rainbow-reads.com/am-toc/')