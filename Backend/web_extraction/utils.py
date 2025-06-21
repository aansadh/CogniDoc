"""
Utility functions for web content extraction in the Smart PDF QA API application.
"""

import requests
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
import time

def remove_noise(html_content):
    """
    Removes noise elements from HTML content.

    Args:
        html_content (str): The raw HTML content.

    Returns:
        str: The cleaned HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    body = str(soup.find('body'))
    if not body or body == 'None':
        return ''
    
    soup = BeautifulSoup(body, 'html.parser')
    for noise in soup(['script', 'style', 'nav', 'a']):
        noise.decompose()

    cleaned_content = soup.get_text(separator='\n', strip=True)
    cleaned_content = "\n".join(line.strip() for line in cleaned_content.splitlines() if line.strip())

    return cleaned_content

def get_html_using_requests(url):
    """
    Fetches HTML content from a URL using the requests library.

    Args:
        url (str): The URL to fetch content from.

    Returns:
        str: The HTML content.

    Raises:
        Exception: If an error occurs during the request.
    """
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise error for bad responses
        print(f"Response status: {response}")
        return response.text
    except Exception as e:
        print(f'An error occurred: {e}')

def get_html_using_selenium(url):
    """
    Fetches HTML content from a URL using Selenium.

    Args:
        url (str): The URL to fetch content from.

    Returns:
        str: The HTML content.

    Raises:
        Exception: If an error occurs during the Selenium operation.
    """
    chrome_driver_options = webdriver.ChromeOptions()
    chrome_driver_options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=chrome_driver_options)

    try:
        driver.get(url)
        html_content = driver.page_source
        time.sleep(4)
        return html_content
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        driver.quit()
    return ''