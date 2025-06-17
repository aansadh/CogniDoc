from web_extraction.utils import remove_noise, get_html_using_requests, get_html_using_selenium
from readability import Document

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.html_content = None
        self.cleaned_content = None
        # self.fetch_html(False)

    def fetch_html(self, use_requests=True):
        self.html_content = self.html_content or (use_requests and get_html_using_requests(self.url)) or get_html_using_selenium(self.url)
        return self.html_content

    def scrape_docs(self):
        try:
            doc = Document(self.fetch_html())
            content = doc.short_title() + "\n" + remove_noise(doc.summary())
            return content
        except Exception as e:
            print(f"[READABILITY ERROR] {e}")
            return ''

    def scrape_staticContent(self):
        return remove_noise(self.fetch_html())

    def scrape_browserContent(self):
        return remove_noise(self.fetch_html(use_requests=False))

    def scrape(self, use_requests=True):
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
    url = 'https://battle-through-the-heavens.fandom.com/wiki/Cai_Lin'
    # url = 'https://www.nytimes.com/'
    # url = 'https://www.nytimes.com/2025/05/29/business/economy/trump-tariffs-ruling-businesses.html'
    # url = 'https://timesofindia.indiatimes.com/'
    # url = 'https://timesofindia.indiatimes.com/india/our-right-of-self-defence-shashi-tharoor-disappointed-over-colombias-reaction-to-operation-sindoor/articleshow/121501848.cms'
    scraper = WebScraper(url)
    content = scraper.scrape()
    print(f"{content[:1000]}...")
    print("Content length: ", len(content))