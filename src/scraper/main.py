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
import logging
import sys
from typing import Optional
from urllib.parse import urlparse
import re
import argparse

from .modules.config import Config
from .modules.base_scraper import BaseScraper
from .modules.wordpress_scraper import WordPressScraper
from .modules import compile
from .modules.utils import setup_logging, get_with_requests
from bs4 import BeautifulSoup
from .modules import WordPressScraper, EbookCompiler

logger = logging.getLogger(__name__)

def get_scraper_for_url(url: str) -> Optional[BaseScraper]:
    """Factory function to get appropriate scraper for the URL."""
    domain = urlparse(url).netloc.lower()
    
    # Check if it's a WordPress site
    if any(wp_indicator in domain for wp_indicator in ['wordpress.com', 'wp.com']) or \
       domain in ['awanderingpotato.com']:  # Add known WordPress sites
        return WordPressScraper(url)
    
    # Default to base scraper for now
    return BaseScraper(url)

def scrape_novel(url, debug=False):
    try:
        # Initialize scraper
        scraper = WordPressScraper(url, debug=debug)
        
        # Fetch main page
        try:
            response = get_with_requests(url)
            if not response or not response.text:
                raise ValueError("Empty response from server")
            soup = BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return
        
        # Extract metadata
        metadata = scraper.extract_metadata(soup)
        logger.info(f"Scraping novel: {metadata['title']}")
        
        # Extract chapters
        chapters = scraper.extract_chapters(soup)
        logger.info(f"Found {len(chapters)} chapters")
        
        # Extract chapter content
        for chapter in chapters:
            try:
                chapter_response = get_with_requests(chapter['url'])
                if not chapter_response or not chapter_response.text:
                    raise ValueError("Empty response from server")
                chapter_soup = BeautifulSoup(chapter_response.text, 'html.parser')
                chapter['content'] = scraper.extract_content(chapter_soup)
                logger.info(f"Processed chapter: {chapter['title']}")
            except Exception as e:
                logger.error(f"Request failed: {str(e)}")
                return
        
        # Compile ebook
        compiler = EbookCompiler(metadata, chapters)
        compiler.create_ebook()
        
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")

def main():
    """Main entry point for the novel scraper."""
    parser = argparse.ArgumentParser(description='Scrape web novels')
    parser.add_argument('url', help='URL of the novel to scrape')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    # Set up logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
        
    logger.info(f"\nStarting novel scraper for URL: {args.url}\n")
    
    try:
        # Load configuration
        config = Config()
        
        # Get appropriate scraper
        scraper = get_scraper_for_url(args.url)
        if not scraper:
            logger.error(f"No suitable scraper found for URL: {args.url}")
            return
        
        # Validate URL
        if not scraper.validate():
            logger.error(f"Invalid or inaccessible URL: {args.url}")
            return
        
        # Get novel information
        try:
            response = get_with_requests(args.url)
            if not response or not response.text:
                raise ValueError("Empty response from server")
            novel_info = scraper.get_novel_info()
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return
        
        if not novel_info:
            logger.error("Failed to get novel information")
            return
        
        logger.info(f"Successfully retrieved novel info: {novel_info['title']} by {novel_info['author']}")
        
        # Get chapter list
        chapters = scraper.get_chapter_list()
        if not chapters:
            logger.error("Failed to get chapter list")
            return
        
        logger.info(f"Found {len(chapters)} chapters")
        
        # Create ebook
        output_dir = config.get("output_dir")
        compile.create_ebook(novel_info, output_dir, chapters)
        
        logger.info("Novel successfully scraped and converted to ebook")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise
    finally:
        if scraper:
            scraper.cleanup()

if __name__ == "__main__":
    main()