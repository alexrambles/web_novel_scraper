## for accessing the web

from re import sub

## for working with or creating files

from os import mkdir, listdir
from ebooklib import epub
import logging
import sys
from pathlib import Path

## Importing original modules created for this project

from . import tableofcontents, utils, constants, chapter


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
        novel_info = tableofcontents.get_toc(toc_url, novelupdates_data = True, novelupdates_toc = input('Get novel TOC from novelupdates.com? Y/N\n'))
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
        utils.init_selenium(toc_url, javascript= False)
    elif 'wattpad' in chapter_links[0]:
        utils.init_selenium(toc_url, javascript= True)
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
            chapter_filename = chapter.get_chapter(link, driver, backup_dir, password, log = log)

            if chapter_filename not in chapter_filename_list and chapter_filename != None:
                chapter_filename_list.append(chapter_filename)
                log.info(f"Chapter {chapter_filename} has been added.")
                
                
    ## ! Get cover image and save it
    if novel_cover_url == '':
        pass
    else:
        utils.get_img(novel_cover_url, img_dir, img_description='cover_img')

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

class EbookCompiler:
    def __init__(self, metadata, chapters, output_dir='output'):
        self.metadata = metadata
        self.chapters = chapters
        self.output_dir = Path(output_dir)
        self.book = epub.EpubBook()
        self._setup_logging()

    def _setup_logging(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def create_ebook(self):
        try:
            self._add_metadata()
            self._create_chapters()
            self._add_table_of_contents()
            self._save_ebook()
            self.logger.info("Ebook compilation completed successfully")
        except Exception as e:
            self.logger.error(f"Ebook compilation failed: {str(e)}")

    def _add_metadata(self):
        self.book.set_title(self.metadata['title'])
        self.book.add_author(self.metadata['author'])
        self.book.add_metadata('DC', 'description', self.metadata['description'])

    def _create_chapters(self):
        self.chapters_epub = []
        for idx, chapter in enumerate(self.chapters):
            epub_chapter = epub.EpubHtml(
                title=chapter['title'],
                file_name=f"chap_{idx+1}.xhtml",
                content=chapter['content']
            )
            self.book.add_item(epub_chapter)
            self.chapters_epub.append(epub_chapter)

    def _add_table_of_contents(self):
        self.book.toc = (tuple(self.chapters_epub))
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

    def _save_ebook(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        epub_path = self.output_dir / f"{self.metadata['title']}.epub"
        epub.write_epub(epub_path, self.book)
        self.logger.info(f"Ebook saved to: {epub_path}")

def create_ebook(novel_info, backup_dir, chapter_filename_list = None):
    """Create an EPUB file from the novel information and chapters."""
    logger = logging.getLogger(__name__)
    logger.info("Creating Ebook...")

    # Extract information from the novel_info dictionary
    novel_filename = sub(r'[^\w\-_\. ]', '_', novel_info['title'])
    novel_title = novel_info['title']
    novel_author = novel_info['author']
    novel_summary = novel_info['description']
    novel_tags = novel_info.get('tags', [])

    # Create output directory if it doesn't exist
    output_dir = Path('output')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize EPUB book
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier(novel_filename)
    book.set_title(novel_title)
    book.set_language('en')
    book.add_author(novel_author)
    book.add_metadata('DC', 'description', novel_summary)
    
    # Add tags/genres
    if novel_tags:
        for tag in novel_tags:
            book.add_metadata('DC', 'subject', tag.strip())

    # Add cover image if available
    if novel_info.get('cover_image'):
        cover_data = novel_info['cover_image']
        book.set_cover("cover.jpg", cover_data['content'], create_page=True)

    # Create chapters
    chapters = []
    for idx, chapter in enumerate(chapter_filename_list or []):
        # Create chapter with preserved formatting
        chapter_content = f"<h1>{chapter['title']}</h1>\n{chapter['content']}"
        
        # Add CSS for proper spacing
        chapter_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Times New Roman', serif; line-height: 1.5; }}
                p {{ margin: 1em 0; text-indent: 2em; }}
            </style>
        </head>
        <body>
            {chapter_content}
        </body>
        </html>
        """
        
        epub_chapter = epub.EpubHtml(
            title=chapter['title'],
            file_name=f'chap_{idx+1:03d}.xhtml',
            content=chapter_content,
            lang='en'
        )
        book.add_item(epub_chapter)
        chapters.append(epub_chapter)

    # Add navigation
    book.toc = tuple(chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Add default CSS
    style = '''
        body { 
            font-family: Times, Times New Roman, serif;
            line-height: 1.5;
            margin: 5%; 
        }
        p { 
            margin: 1em 0;
            text-indent: 2em;
        }
        h1 {
            text-align: center;
            margin: 1em 0 2em 0;
        }
    '''
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style
    )
    book.add_item(nav_css)

    # Create spine
    book.spine = ['nav'] + chapters

    # Write EPUB file
    epub_path = output_dir / f"{novel_filename}.epub"
    epub.write_epub(str(epub_path), book, {})
    
    logger.info(f"EPUB created successfully: {epub_path}")
    return str(epub_path)
