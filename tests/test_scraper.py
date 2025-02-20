import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper.modules import compile, chapter, tableofcontents, utils
from scraper.modules.constants import *

class TestNovelScraper(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_url = "https://example.com/novel/chapter-1"
        self.mock_html_content = """
        <html>
            <head><title>Test Novel - Chapter 1</title></head>
            <body>
                <div class="chapter-content">
                    <p>This is a test chapter content.</p>
                </div>
                <a href="/novel/chapter-2" class="next-chapter">Next Chapter</a>
            </body>
        </html>
        """

    @patch('requests.get')
    def test_url_validation(self, mock_get):
        """Test URL validation and response handling"""
        # Test valid URL
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = self.mock_html_content
        self.assertTrue(utils.validate_url(self.test_url))

        # Test invalid URL
        mock_get.return_value.status_code = 404
        self.assertFalse(utils.validate_url("https://example.com/nonexistent"))

    @patch('scraper.modules.tableofcontents.get_toc')
    def test_toc_extraction(self, mock_get_toc):
        """Test table of contents extraction"""
        mock_chapters = [
            {"title": "Chapter 1", "url": "https://example.com/novel/chapter-1"},
            {"title": "Chapter 2", "url": "https://example.com/novel/chapter-2"}
        ]
        mock_get_toc.return_value = mock_chapters
        
        toc = tableofcontents.get_toc(self.test_url)
        self.assertEqual(len(toc), 2)
        self.assertEqual(toc[0]["title"], "Chapter 1")

    @patch('scraper.modules.chapter.get_chapter_content')
    def test_chapter_extraction(self, mock_get_content):
        """Test chapter content extraction"""
        mock_content = "This is a test chapter content."
        mock_get_content.return_value = mock_content
        
        content = chapter.get_chapter_content(self.test_url)
        self.assertEqual(content, mock_content)

    def test_ebook_creation(self):
        """Test ebook file creation"""
        test_novel_info = {
            "title": "Test Novel",
            "author": "Test Author",
            "chapters": ["Chapter 1", "Chapter 2"]
        }
        test_output_dir = "test_output/"
        test_chapter_files = ["chapter1.html", "chapter2.html"]
        
        # Mock the actual ebook creation
        with patch('scraper.modules.compile.create_ebook') as mock_create:
            compile.create_ebook(test_novel_info, test_output_dir, test_chapter_files)
            mock_create.assert_called_once()

if __name__ == '__main__':
    unittest.main()
