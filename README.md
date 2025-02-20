# Web Novel Scraper

A Python-based web scraper designed to download and compile web novels into ebooks. This tool supports various web novel platforms and can handle different webpage structures.

## Features

- Scrapes novel content from multiple web novel platforms
- Handles different chapter navigation methods (TOC-based, next-button based)
- Creates organized ebook files from scraped content
- Supports image downloading and embedding
- Includes logging for debugging and tracking
- Error handling for various web scenarios (404s, timeouts)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

- `src/scraper/`
  - `main.py` - Entry point of the application
  - `modules/`
    - `chapter.py` - Chapter scraping logic
    - `compile.py` - Ebook compilation functionality
    - `constants.py` - Project constants and configurations
    - `metadata.py` - Novel metadata handling
    - `tableofcontents.py` - TOC parsing and navigation
    - `utils.py` - Utility functions and helpers

## Usage

Run the script using:
```bash
python src/scraper/main.py
```

When prompted, enter the URL of the novel you want to scrape.

## Areas for Improvement

1. Code Organization:
   - Consider implementing a proper class structure for better encapsulation
   - Move configuration to a separate config file
   - Implement proper dependency injection

2. Error Handling:
   - Add more robust error handling for network issues
   - Implement retry mechanisms for failed requests
   - Add validation for input URLs

3. Performance:
   - Consider implementing async/await for better performance
   - Add caching mechanisms for frequently accessed data
   - Implement proper rate limiting

4. Testing:
   - Add unit tests for core functionality
   - Implement integration tests for end-to-end flows
   - Add mock responses for testing without actual web requests

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)