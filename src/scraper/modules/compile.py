## for accessing the web

from re import sub

## for working with or creating files

from os import mkdir, listdir
from ebooklib import epub
import logging
import sys

## Importing original modules created for this project

import modules.tableofcontents, modules.utils, modules.constants, modules.chapter


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


################################ !Functions #################################

def get_novel(toc_url, password = ''):
    log.info("Starting to get_novel...")
    ## Get novel info from toc with access_toc function (returns the info needed)
    try:
        novel_info = modules.tableofcontents.get_toc(toc_url, novelupdates_data = True, novelupdates_toc = input('Get novel TOC from novelupdates.com? Y/N\n'))
        log.info("TOC from novelupdates.com retrieved.")

    except:
        logging.error(f'Could not retrieve novel info from {toc_url}.')

    ## Assign all values to their proper variables
    novel_filename  = novel_info[0]
    novel_title     = novel_info[1]
    chapter_links   = novel_info[7]
    novel_cover_url = novel_info[8]
    driver          = novel_info[9]


    ## Create backup folder for accessed chapters to reduce load on server
    backup_dir = f"D:/python_projs/proj_save_the_danmei/Books/{novel_filename}/"
    img_dir = f"D:/python_projs/proj_save_the_danmei/Books/{novel_filename}/images/"

    ## Does the directory for the novel exist? If not, create it.
    try:
        mkdir(backup_dir)

    except FileExistsError:
        log.warning(f" Directory for {novel_title} already exists.")

    ## Is the sub-directory for images created? If not, create it.
    try:
        mkdir(img_dir)

    except FileExistsError:
        log.warning(f" Images folder for {novel_title} already exists.")

    chapter_filename_list = []
    chapter_filename = None

    ## Get chapters for each ch link
    if 'chrysanthemum' in chapter_links[0] or 'knoxt' in chapter_links[0]:
        modules.utils.init_selenium(toc_url, javascript= False)
    elif 'wattpad' in chapter_links[0]:
        modules.utils.init_selenium(toc_url, javascript= True)
    else:
        pass


    ## ! For each chapter link, get chapter, unless it contains twitter/facebook in url
    
    for link in chapter_links:
        if 'twitter' in link or 'facebook' in link:
            break
        elif link == '':
            link_index = chapter_links.index(link)
            logging.error(f' Encountered invalid chapter link at {link_index}. Skipping link.')
        else:
            chapter_filename = modules.chapter.get_chapter(link, driver, backup_dir, password, log = log)

            if chapter_filename not in chapter_filename_list and chapter_filename != None:
                chapter_filename_list.append(chapter_filename)
                log.info(f"Chapter {chapter_filename} has been added.")
                
                
    ## ! Get cover image and save it
    if novel_cover_url == '':
        pass
    else:
        modules.utils.get_img(novel_cover_url, img_dir, img_description='cover_img')

        print(f' Cover image saved to {img_dir}')

    ## Save chapter filename list to saved file.
    with open(f'{backup_dir}chapter_filename_list.txt', 'w') as f:
        log.info(f'Saving chapter filename list to {backup_dir}')
        f.write('\n'.join(chapter_filename_list))

    return [
        novel_info
        ,backup_dir
        ,chapter_filename_list
        ]

def create_ebook(novel_info, backup_dir, chapter_filename_list = None):

    log.info("Creating Ebook...")

    novel_filename  = novel_info[0]
    novel_title     = novel_info[1]
    novel_author    = novel_info[2]
    author_alias    = novel_info[3]
    novel_genres    = novel_info[4]
    novel_tags      = novel_info[5]
    novel_summary   = novel_info[6]

    novel_tag_string = ', '.join(novel_tags)

    backup_dir = f"D:/python_projs/proj_save_the_danmei/Books/{novel_filename}/"
    img_dir = f"D:/python_projs/proj_save_the_danmei/Books/{novel_filename}/images/"

    if chapter_filename_list == None:
        log.info("Chapter filename list not found. Opening .txt file.")
        ebook_chapter_list = []
        with open(f'{backup_dir}chapter_filename_list.txt', 'r') as f:
            for line in f:
                # remove linebreak from a current name
                # linebreak is the last character of each line
                x = line[:-1]

                # add current item to the list
                ebook_chapter_list.append(x)
    else:
        ebook_chapter_list = chapter_filename_list

    ## Create ebook
    book = epub.EpubBook()

    # adding metadata
    book.set_identifier(f"{novel_title}")
    book.set_title(novel_title)
    book.set_language("en")

    ## English authorname (hopefully)
    book.add_author(novel_author, uid="Author")

    ## If there is a native-language version of the name, it's author alias.
    if author_alias != '' and author_alias != novel_author:
        log.info(f"Author alias found. Adding {author_alias} as author alias.")
        book.add_author(author_alias, role="Alias" ,uid="author_alias")


    print(f"Book Metadata added.")

    ## TODO: Create a google image scraper to find the book cover automatically. Safer is just searching novelupdates, but better results from google img.
    ## TODO: Build a UI that presents the image found and asks for approval before saving and applying to the novel epub.

    ## create spine and toc variable
    spine = []
    toc_list = []

    ## Set book cover
    with open( f'{img_dir}cover.jpg', "rb" ) as f:
        cover_image = f.read()

    book.set_cover( file_name=f'cover.jpg', content=cover_image )

    spine.append( "cover.xhtml" )

    ## create title page
    #titlepage = "<?xml version='1.0' encoding='utf-8'?><!DOCTYPE html>" + f'<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/#" lang="en" xml:lang="en"><head><title>{novel_title}</title><link rel="stylesheet" href="stylesheet.css" type="text/css" /></head><div epub:type="frontmatter"><body><div class="title">{novel_title}</div><div>This ebook is compiled for educational purposes only and is not to be redistributed.</div><div>Title: {novel_title}</div><div>Author: {novel_author} {author_alias}</div><div class="cover"><h1 id="titlepage">{novel_title}</h1><h2>by {novel_author} {author_alias}</h2><p>Tags: {", ".join(novel_tags)}</p><img src="images/cover.jpg" alt = "cover_image"/></div></body></div></html>'

    titlepage_html = f'<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/#" lang="en" xml:lang="en"><head><title>{novel_title}</title><link rel="stylesheet" href="stylesheet.css" type="text/css" /><meta charset = "utf-8"/></head><div epub:type="frontmatter"><body><div class="title">{novel_title}</div><div>This ebook is compiled for educational purposes only and is not to be redistributed.</div><div>Title: {novel_title}</div><div>Author: {novel_author} {author_alias}</div><div class="cover"><h1 id="titlepage">{novel_title}</h1><h2>by {novel_author} {author_alias}</h2><p>Tags: {novel_tag_string}</p><img src="images/cover.jpg"></img></div></body></div></html>'


    ## set title page
    title_page = book.add_item(epub.EpubItem(
        uid="title_page"
        ,file_name="titlepage.html"
        ,content=titlepage_html
        ,media_type="application/xhtml+xml"))

    spine.append("title_page")
    toc_list.append("title_page")

    print("Title page added.")

    spine.append("nav")


    # add contents of chapter to book, spine, and TOC
    for i in chapter_filename_list:
        with open(f'{backup_dir}{i}.html', "r", encoding="utf-8") as f:
            log.info("Reading chapter_filename_list file...")
            text = f.read()
            ch_content = text

        try:
            chap_title = i.rsplit(".", 1)[0]
            chap_num = sub("[^0-9.]", " ", chap_title).strip()
            if chap_num == '':
                chap_num = '0'
            new_chap_title = "Chapter " + chap_num
        except Exception:
            log.debug("Exception encountered while retrieving chapter title/number.")
            pass

        ebook_chapter =\
            epub.EpubHtml(
                title=new_chap_title
                ,file_name=f'{i}.html'
                ,media_type="application/xhtml+xml"
                )

        ebook_chapter.set_content( str(ch_content) )

        book.add_item(ebook_chapter)

        spine.append(ebook_chapter)

        toc_list.append(ebook_chapter)

        # add images to book
        # load Image file

    for image_filename in listdir(img_dir):
        log.info(f"Reading all files from {img_dir}.")
        image_filepath = f'{img_dir}{image_filename}'

        with open(f'{image_filepath}', "rb") as f:
            image = f.read()

        filename = image_filename.split('.')[0]
        image_filename = f'{filename}.jpg'

        # * define Image file path in .epub
        image_item = epub.EpubItem(
            uid=image_filename
            ,file_name=f'images/{image_filename}'
            ,media_type=f'image/jpeg'
            ,content=image
            )

        # add Image file
        book.add_item(image_item)

    # create stylesheet
    style = "@page {margin-top: 0em;margin-bottom: 0em;text-indent: 1.5em;}div.cover {text-align: center;page-break-after: always;padding: 0;margin: 0;}div.cover img {max-height: 100%;max-width: 100%;padding: 10px;margin: 10px;background-color: #ccc;}.cover-img {max-height: 100%;max-width: 100%;margin: auto;}h1, h2 {-webkit-hyphens: none;hyphens: none;-moz-hyphens: none;page-break-after: avoid;page-break-inside: avoid;text-indent: 0;text-align: center;}h1 {font-size: 1.6em;margin-bottom: 20px;}.title {margin-bottom: 0;margin-top: 20px;}h2 {font-size: 10px;margin-top: 5px;margin-bottom: 5px;}img {-webkit-border-radius: 5px;border-radius: 5px;-webkit-box-shadow: rgba(0, 0, 0, 0.15) 0 1px 4px;box-shadow: rgba(0, 0, 0, 0.15) 0 1px 4px;box-sizing: border-box;border: #fff 5px solid;max-width: 80%;max-height: 80%;}.footnote_image {max-width: 80%;max-height: 80%;margin: auto;}.footnote_link {text-decoration: underline;}"

    # add stylesheet to book
    book.add_item(
        epub.EpubItem(
            uid="stylesheet"
            ,file_name="stylesheet.css"
            ,media_type="text/css"
            ,content=style
            )
        )

    print("CSS added.")

    ## Novel tags
    book.add_metadata("DC", "description", novel_summary)

    for i in novel_genres:
        book.add_metadata("DC", "subject", i)

    print("Metadata added.")

    # create TOC
    book.toc = toc_list

    # create spine of book
    book.spine = spine

    # add nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    print("Nav elements added.")

    book_file = ''.join(["D:/python_projs/proj_save_the_danmei/Books/", novel_filename, ".epub"])

    epub.write_epub(book_file, book)

