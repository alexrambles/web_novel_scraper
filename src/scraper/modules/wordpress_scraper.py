from .base_scraper import BaseScraper
from .utils import get_with_requests, save_file, validate_url
from bs4 import BeautifulSoup
import logging
import os
from urllib.parse import urljoin
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class WordPressScraper(BaseScraper):
    """Scraper implementation for WordPress-based novel sites."""
    
    def __init__(self, url: str):
        super().__init__(url)
        self.logger = logging.getLogger(__name__)
        
    def get_novel_info(self):
        """Extract novel metadata from the main page."""
        try:
            self.logger.debug("Attempting to fetch page content")
            html = self.get_page(self.url)
            if not html:
                self.logger.error("Failed to retrieve page content")
                return {}
                
            self.logger.debug("Creating BeautifulSoup object")
            soup = BeautifulSoup(html, 'html.parser')
            
            # Debug: Check what HTML we're getting
            self.logger.debug(f"Page title tag: {soup.title}")
            self.logger.debug("Looking for title in these elements:")
            for h1 in soup.find_all('h1'):
                self.logger.debug(f"Found h1: {h1}")
            
            self.logger.debug("Extracting metadata")
            metadata = self.extract_metadata(soup)
            if not metadata:
                self.logger.error("Failed to extract metadata")
                return {}
            
            # Extract cover image
            cover_image = self.extract_cover_image(soup)
            if cover_image:
                metadata['cover_image'] = cover_image
            
            return {
                "title": metadata.get('title', 'Unknown Title'),
                "author": metadata.get('author', 'Unknown Author'),
                "description": metadata.get('description', ''),
                "source_url": self.url,
                "tags": metadata.get('tags', []),
                "cover_image": metadata.get('cover_image')
            }
        except Exception as e:
            self.logger.error(f"Error getting novel info: {str(e)}")
            return {}
    
    def get_chapter_list(self) -> List[Dict]:
        """Extract chapter list and content from the table of contents."""
        try:
            html = self.get_page(self.url)
            if not html:
                return []
                
            soup = BeautifulSoup(html, 'html.parser')
            chapters = self.extract_chapters(soup)
            
            # Fetch content for each chapter
            for chapter in chapters:
                self.logger.debug(f"Fetching content for chapter: {chapter['title']}")
                try:
                    chapter_html = self.get_page(chapter['url'])
                    if chapter_html:
                        chapter_soup = BeautifulSoup(chapter_html, 'html.parser')
                        content = self.extract_content(chapter_soup)
                        chapter['content'] = content
                    else:
                        self.logger.error(f"Failed to fetch content for chapter: {chapter['title']}")
                        chapter['content'] = "Content unavailable"
                except Exception as e:
                    self.logger.error(f"Error fetching chapter content: {str(e)}")
                    chapter['content'] = "Error fetching content"
            
            return chapters
            
        except Exception as e:
            self.logger.error(f"Error getting chapter list: {str(e)}")
            return []
    
    def get_chapter_content(self, chapter_url: str) -> Optional[str]:
        """Extract chapter content from the chapter page."""
        try:
            html = self.get_page(chapter_url)
            if not html:
                return None
                
            soup = BeautifulSoup(html, 'html.parser')
            
            content = self.extract_content(soup)
            
            # Remove unwanted elements
            for unwanted in BeautifulSoup(content, 'html.parser').find_all(['script', 'style', 'iframe', 'form']):
                unwanted.decompose()
            
            # Remove navigation elements
            for nav in BeautifulSoup(content, 'html.parser').find_all(['div', 'p'], class_=re.compile(r'nav|navigation|chapter-nav')):
                nav.decompose()
            
            # Clean up the content
            text = BeautifulSoup(content, 'html.parser').get_text('\n\n')
            text = re.sub(r'\n{3,}', '\n\n', text)  # Remove excessive newlines
            text = text.strip()
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error getting chapter content: {str(e)}")
            return None

    def extract_content(self, soup):
        """Extract chapter content from WordPress entry-content div"""
        content_div = soup.find('div', class_='entry-content')
        if not content_div:
            return 'Content not found'
        
        # Clean up unnecessary elements
        for element in content_div.find_all(['script', 'style']):
            element.decompose()
        
        # Remove sharing buttons and other unnecessary divs
        for element in content_div.find_all('div', class_=['sharedaddy', 'nav', 'footer']):
            element.decompose()
        
        # Extract text content with preserved formatting
        content = []
        for element in content_div.children:
            if element.name == 'p':
                text = element.get_text().strip()
                if text:
                    content.append(f"<p>{text}</p>")
            elif element.name == 'br':
                content.append("<br/>")
        
        return '\n'.join(content)

    def extract_cover_image(self, soup):
        """Extract cover image URL from the page"""
        try:
            # Try to find cover image in various locations
            cover_img = None
            
            # Look for featured image
            cover_img = soup.find('img', class_='wp-post-image')
            
            # Look for first image in content that might be cover
            if not cover_img:
                content_div = soup.find('div', class_='entry-content')
                if content_div:
                    cover_img = content_div.find('img')
            
            if cover_img and cover_img.get('src'):
                img_url = cover_img['src']
                # Get high quality version if available
                img_url = img_url.replace('-300x450', '').replace('-150x150', '')
                
                # Download image
                try:
                    response = self.session.get(img_url, timeout=30)
                    response.raise_for_status()
                    return {
                        'content': response.content,
                        'type': response.headers.get('content-type', 'image/jpeg')
                    }
                except Exception as e:
                    self.logger.error(f"Failed to download cover image: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error extracting cover image: {str(e)}")
        
        return None

    def extract_metadata(self, soup):
        """Extract novel metadata from WordPress post"""
        try:
            # Find title using h1.card_title
            title_element = soup.find('h1', class_='card_title')
            self.logger.debug(f"Raw title element: {title_element}")
            
            if not title_element:
                self.logger.error("Title element not found")
                return None
            
            # Find synopsis between Synopsis and Chapter List
            synopsis = ""
            synopsis_start = soup.find('p', string=lambda text: text and 'Synopsis' in text)
            chapter_list = soup.find('p', string=lambda text: text and 'Chapter List' in text)
            
            if synopsis_start and chapter_list:
                current = synopsis_start.find_next('p')
                synopsis_parts = []
                while current and current != chapter_list:
                    if current.text.strip():
                        synopsis_parts.append(current.text.strip())
                    current = current.find_next('p')
                synopsis = '\n'.join(synopsis_parts)
            
            # Find tags in paragraph containing "Tags"
            tags = []
            tags_p = soup.find('p', string=lambda text: text and 'Tags' in text)
            if tags_p:
                tags = [tag.strip() for tag in tags_p.text.replace('Tags:', '').split(',')]
            
            metadata = {
                'title': title_element.text.strip(),
                'author': 'A Wandering Potato',  # Site author
                'description': synopsis,
                'tags': tags
            }
            
            self.logger.debug(f"Extracted metadata: {metadata}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {str(e)}")
            return None

    def _detect_author(self, author_element):
        # Author detection logic
        return author_element.text.strip() if author_element else 'Unknown Author'

    def _extract_description(self, soup):
        entry_content = soup.find('div', class_='entry-content')
        if entry_content:
            first_paragraphs = entry_content.find_all('p', limit=3)
            return '\n'.join(p.text.strip() for p in first_paragraphs)
        return ''

    def extract_chapters(self, soup):
        """Extract chapter links from table of contents"""
        chapters = []
        content_div = soup.find('div', class_='entry-content')
        
        if content_div:
            # Find the Chapter List header
            chapter_list = soup.find('p', string=lambda text: text and 'Chapter List' in text)
            if chapter_list:
                current = chapter_list.find_next('p')
                while current:
                    # Check if we've hit another major section
                    if current.find('strong'):  # Arc header
                        arc_title = current.text.strip()
                        self.logger.debug(f"Found arc: {arc_title}")
                    
                    # Look for chapter links
                    for link in current.find_all('a'):
                        if link.get('href'):
                            chapters.append({
                                'title': link.text.strip(),
                                'url': link['href']
                            })
                    current = current.find_next('p')
                    
                    # Stop if we hit the end of the chapter list
                    if current and current.find('strong') and 'Author' in current.text:
                        break
                        
        self.logger.debug(f"Found {len(chapters)} chapters")
        return chapters
