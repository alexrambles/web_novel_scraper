from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging
import requests
from urllib.parse import urljoin
from .utils import validate_url, setup_logging

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Base class for novel scrapers implementing common functionality."""
    
    def __init__(self, url: str, session: Optional[requests.Session] = None):
        self.url = url
        self.session = session or requests.Session()
        self.logger = setup_logging(__name__)
        
    def get_page(self, url: str) -> Optional[str]:
        """Safely retrieve a page with proper error handling and logging."""
        try:
            self.logger.debug(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            self.logger.debug(f"Successfully fetched URL: {url}")
            self.logger.debug(f"Response status code: {response.status_code}")
            self.logger.debug(f"Response headers: {response.headers}")
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {str(e)}")
            if isinstance(e, requests.HTTPError):
                self.logger.error(f"HTTP Status Code: {e.response.status_code}")
            return None

    def get_novel_info(self):
        """Get novel metadata from URL - must be implemented by subclasses"""
        raise NotImplementedError

    @abstractmethod
    def get_chapter_list(self) -> List[Dict]:
        """Get list of chapters with their URLs."""
        pass

    @abstractmethod
    def get_chapter_content(self, chapter_url: str) -> Optional[str]:
        """Extract chapter content from given URL."""
        pass

    def validate(self) -> bool:
        """Validate if the URL is accessible and contains expected content."""
        return validate_url(self.url)

    def cleanup(self):
        """Cleanup resources."""
        self.session.close()
