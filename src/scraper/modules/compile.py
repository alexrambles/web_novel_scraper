##for parsing text
import translators as translator

## for accessing the web

from urllib import request
import requests

## for working with or creating files

from os import mkdir
from types import NoneType

## Importing original modules created for this project

import utils
import toc
import constants


def setup(toc_url, no_no_list = constants.no_no_list):

    global downloads_folder

    downloads_folder = "D:\\alexi\\Documents\\books\\"

## Get novel info from toc with access_toc function (returns the info needed)
    try:
        novel_info = toc.access_toc(toc_url)
        print('Retrieved novel info from TOC.')
    except:
        return print('ERROR: Could not get novel info from TOC.')

## Assign all values to their proper variables
    novel_filename = novel_info[0]
    novel_title = novel_info[1]
    novel_author = novel_info[2]
    novel_summary = novel_info[3]
    chapter_links = novel_info[4]

## Create backup folder for accessed chapters to reduce load on server
    backup_files = f"D:/python_projs/proj_save_the_danmei/Books/{novel_filename}/"

    try:
        mkdir(backup_files)
    except:
        print(f"Warning: Could not create a directory for {novel_title}.")


##toc_url = input('Please input the URL to the Table of Contents of your novel.')

setup('https://rainbow-reads.com/am-toc/')