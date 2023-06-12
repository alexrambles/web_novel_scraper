## for accessing the web

from re import sub

## for working with or creating files

from os import mkdir, listdir
from ebooklib import epub
from types import NoneType

## Importing original modules created for this project

import toc
import utils
import constants
import chapter


def get_novel(toc_url, no_no_list = constants.no_no_list):

    ## Get novel info from toc with access_toc function (returns the info needed)
    try:
        novel_info = toc.get_toc(toc_url)
        print('Retrieved novel info from TOC.')
    except:
        return print('ERROR: Could not get novel info from TOC.')

    ## Assign all values to their proper variables

    novel_filename  = novel_info[0]
    novel_title     = novel_info[1]
    chapter_links   = novel_info[7]
    novel_cover_url = novel_info[8]
    driver          = novel_info[9]


    ## Create backup folder for accessed chapters to reduce load on server
    backup_dir = f"D:/python_projs/proj_save_the_danmei/Books/{novel_filename}/"

    try:
        mkdir(backup_dir)
    except FileExistsError:
        print(f"Warning: Directory for {novel_title} already exists.")

    try:
        mkdir(backup_dir + 'images/')
    except FileExistsError:
        print(f"Warning: Images folder for {novel_title} already exists.")

    img_filename_list = []
    chapter_filename_list = []
    chapter_filename = None

    ## Get chapters for each ch link
    for link in chapter_links:
        if 'twitter' in link or 'facebook' in link:
            break
        else:
            chapter_filename = chapter.get_chapter(link, driver, backup_dir)

            chapter_filename_list.append(chapter_filename)
            print(f'{chapter_filename} has been added.')

    if novel_cover_url == '':
        pass
    else:
        utils.get_img(novel_cover_url, f'{backup_dir}images/cover.jpg')

    with open(f'{backup_dir}chapter_filename_list.txt', 'w') as f:
        f.write('\n'.join(chapter_filename_list))

    return [novel_info, backup_dir, chapter_filename_list]


def create_ebook(novel_info, backup_dir, chapter_filename_list  = None):

    novel_filename  = novel_info[0]
    novel_title     = novel_info[1]
    novel_author    = novel_info[2]
    author_alias    = novel_info[3]
    novel_genres    = novel_info[4]
    novel_tags      = novel_info[5]
    novel_summary   = novel_info[6]
    chapter_links   = novel_info[7]
    driver          = novel_info[8]

    if chapter_filename_list == None:
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


    book.add_author(novel_author, uid="Author")


    print(f"Book Metadata added.")

    ## TODO: Create a google image scraper to find the book cover automatically. Safer is just searching novelupdates, but better results from google img.
    ##TODO: Build a UI that presents the image found and asks for approval before saving and applying to the novel epub.

    # create title page

    titlepage = f"<?xml version='1.0' encoding='utf-8'?>" + f'<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/#" lang="en" xml:lang="en"><head><link rel="stylesheet" href="stylesheet.css" type="text/css" /></head><div epub:type="frontmatter"><body><div class="title">{novel_title}</div><div>This ebook is compiled for educational purposes only and is not to be redistributed.</div><div>Title: {novel_title}</div><div>Author: {novel_author} </div><div class="cover"><h1 id="titlepage">{novel_title}</h1><h2>by {novel_author} </h2></div></body></div></html>'


    book.add_item(
        epub.EpubItem(uid="title page", file_name="titlepage.html", content=titlepage)
    )
    print("Title page added.")

    # create spine variable and set up

    spine = ["title page", "nav", "toc"]

    toc_list = []

    # add contents of chapter to book, spine, and TOC
    for i in chapter_filename_list:

        with open(f'{backup_dir}\{novel_filename}\{i}.html', "r", encoding="utf-8") as f:
            text = f.read()
            ch_content = text

        try:
            chap_title = i.rsplit(".", 1)[0]
            chap_num = sub("[^0-9.]", " ", chap_title).strip()
            new_chap_title = "Chapter " + chap_num
        except Exception:
            pass

        ebook_chapter = epub.EpubHtml(title=new_chap_title, file_name=f'{i}.html', media_type="text/html")

        ebook_chapter.set_content(str(ch_content))

        book.add_item(ebook_chapter)

        spine.append(ebook_chapter)

        toc_list.append(ebook_chapter)

        # add images to book
        # load Image file

    for image_filename in listdir(f'{backup_dir}images/'):
        image_filepath = f'{backup_dir}images/{image_filename}'

        with open(f'{image_filepath}', "rb") as f:
            image = f.read()

        filetype = image_filename.split('.')[1]

        # define Image file path in .epub
        image_item = epub.EpubItem(uid=image_filename, file_name=f'images/{image_filename}', media_type=f'image/{filetype}', content=image)

        # add Image file
        book.add_item(image_item)

    # create stylesheet

    style = "@page {margin-top: 0em;margin-bottom: 0em;text-indent: 1.5em;}div.cover {text-align: center;page-break-after: always;padding: 0;margin: 0;}div.cover img {max-height: 100%;max-width: 100%;padding: 10px;margin: 10px;background-color: #ccc;}.cover-img {max-height: 100%;max-width: 100%;margin: auto;}h1, h2 {-webkit-hyphens: none;hyphens: none;-moz-hyphens: none;page-break-after: avoid;page-break-inside: avoid;text-indent: 0;text-align: center;}h1 {font-size: 1.6em;margin-bottom: 20px;}.title {margin-bottom: 0;margin-top: 20px;}h2 {font-size: 10px;margin-top: 5px;margin-bottom: 5px;}img {-webkit-border-radius: 5px;border-radius: 5px;-webkit-box-shadow: rgba(0, 0, 0, 0.15) 0 1px 4px;box-shadow: rgba(0, 0, 0, 0.15) 0 1px 4px;box-sizing: border-box;border: #fff 5px solid;max-width: 80%;max-height: 80%;}.footnote_image {max-width: 80%;max-height: 80%;margin: auto;}.footnote_link {text-decoration: underline;}"

    # add stylesheet to book

    book.add_item(
        epub.EpubItem(
            uid="stylesheet",
            file_name="stylesheet.css",
            media_type="text/css",
            content=style
        )
    )
    print("CSS added.")

    # create TOC
    book.toc = toc_list

    # create spine of book

    book.spine = spine

    # add nav files

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    print("Nav elements added.")

    book_file = 'D:\python_projs\proj_save_the_danmei\Books' + novel_filename + ".epub"


    epub.write_epub(book_file, book)

##toc_url = input('Please input the URL to the Table of Contents of your novel.')

novel_data = get_novel('https://rainbow-reads.com/am-toc/')

novel_info = novel_data[0]
backup_dir = novel_data[1]
chapter_filename_list = novel_data[2]

create_ebook(novel_info, 'D:\python_projs\proj_save_the_danmei\Books', chapter_filename_list)