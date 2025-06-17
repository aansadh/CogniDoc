import requests
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
import time

def remove_noise(html_content):
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
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise error for bad responses
        print(f"Response status: {response}")
        return response.text
    except Exception as e:
        print(f'An error occurred: {e}')

def get_html_using_selenium(url):
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