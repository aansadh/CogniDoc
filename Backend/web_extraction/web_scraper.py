"""
Web scraping module for extracting content from web pages in the Smart PDF QA API application.
"""

from web_extraction.utils import remove_noise, get_html_using_requests, get_html_using_selenium
from readability import Document

class WebScraper:
    """
    Handles web scraping operations using various methods.

    Attributes:
        url (str): The URL to scrape.
        html_content (str): The raw HTML content fetched from the URL.
        cleaned_content (str): The cleaned content extracted from the HTML.
    """

    def __init__(self, url):
        """
        Initializes the WebScraper instance.

        Args:
            url (str): The URL to scrape.
        """
        self.url = url
        self.html_content = None
        self.cleaned_content = None
        # self.fetch_html(False)

    def fetch_html(self, use_requests=True):
        """
        Fetches HTML content from the URL.

        Args:
            use_requests (bool): Whether to use the requests library for fetching content.

        Returns:
            str: The fetched HTML content.
        """
        self.html_content = self.html_content or (use_requests and get_html_using_requests(self.url)) or get_html_using_selenium(self.url)
        return self.html_content

    def scrape_docs(self):
        """
        Scrapes content using the readability library.

        Returns:
            str: The scraped content.

        Raises:
            Exception: If an error occurs during scraping.
        """
        try:
            doc = Document(self.fetch_html())
            content = doc.short_title() + "\n" + remove_noise(doc.summary())
            return content
        except Exception as e:
            print(f"[READABILITY ERROR] {e}")
            return ''

    def scrape_staticContent(self):
        """
        Scrapes static content from the HTML.

        Returns:
            str: The scraped static content.
        """
        return remove_noise(self.fetch_html())

    def scrape_browserContent(self):
        """
        Scrapes content using browser rendering.

        Returns:
            str: The scraped browser-rendered content.
        """
        return remove_noise(self.fetch_html(use_requests=False))

    def scrape(self, use_requests=True):
        """
        Scrapes content using the specified method.

        Args:
            use_requests (bool): Whether to use the requests library for scraping.

        Returns:
            str: The scraped content.
        """
        if not use_requests:
            print("[INFO] Using browser rendering (Selenium)...")
            return self.scrape_browserContent()

        print("[WARN] Trying static content using requests...")
        content = self.scrape_staticContent()
        if content and len(content.split()) > 100:
            print("[INFO] Static content scrape succeeded.")
            return content

        print("[INFO] Trying readability-based scraping...")
        content = self.scrape_docs()
        if content and len(content.split()) > 100:
            print("[INFO] Readability scrape succeeded.")
            return content

        print("[WARN] Static content insufficient. Falling back to browser rendering...")
        return self.scrape_browserContent()

if __name__ == "__main__":
    url = ''
    scraper = WebScraper(url)
    content = scraper.scrape()
    print(f"{content[:1000]}...")
    print("Content length: ", len(content))