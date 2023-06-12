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
import modules.compile
import cProfile, pstats

def main(url):
	novel_data = compile.get_novel(url)
	novel_info = novel_data[0]
	backup_dir = novel_data[1]
	chapter_filename_list = novel_data[2]

	compile.create_ebook(novel_info, 'D:\python_projs\proj_save_the_danmei\Books', chapter_filename_list)

if __name__ == '__main__':
    url = input("Please link to the source you'd like to scrape.")

    profiler = cProfile.Profile()
    profiler.enable()
    main(url)
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('ncalls')
    stats.print_stats()