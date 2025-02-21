import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper.modules.utils import get_with_requests, init_selenium
from bs4 import BeautifulSoup
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def main():
    logger = setup_logging()
    url = input("Enter the URL for testing: ")
    
    logger.info(f"Testing scraper with URL: {url}")
    
    # Try with requests-html first
    try:
        logger.info("Attempting to fetch with requests-html...")
        response = get_with_requests(url)
        soup = BeautifulSoup(response.html.html, 'html.parser')
        
        # Get novel title
        title = soup.find('h1', class_='entry-title')
        if title:
            logger.info(f"Found title: {title.text.strip()}")
        
        # Get chapter links
        content = soup.find('div', class_='entry-content')
        if content:
            chapter_links = content.find_all('a')
            logger.info(f"Found {len(chapter_links)} potential chapter links")
            
            # Print first few chapters
            for link in chapter_links[:5]:
                if 'chapter' in link.text.lower():
                    logger.info(f"Chapter link: {link.text.strip()} -> {link.get('href', '')}")
        
    except Exception as e:
        logger.error(f"Error with requests-html: {str(e)}")
        logger.info("Trying with Selenium as fallback...")
        
        try:
            driver, wait = init_selenium(url)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Get novel title
            title = soup.find('h1', class_='entry-title')
            if title:
                logger.info(f"Found title (Selenium): {title.text.strip()}")
            
            # Get chapter links
            content = soup.find('div', class_='entry-content')
            if content:
                chapter_links = content.find_all('a')
                logger.info(f"Found {len(chapter_links)} potential chapter links (Selenium)")
                
                # Print first few chapters
                for link in chapter_links[:5]:
                    if 'chapter' in link.text.lower():
                        logger.info(f"Chapter link: {link.text.strip()} -> {link.get('href', '')}")
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error with Selenium: {str(e)}")

if __name__ == "__main__":
    main()
