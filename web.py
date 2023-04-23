# Usage:
#   poetry run python web.py https://www.google.com/
#
# About:
#   This script uses Selenium to scrape the text from a website.
#
# This code is originally from https://github.com/Significant-Gravitas/Auto-GPT/blob/60b2b61b52c263dba25a6c33623561273e890229/autogpt/web.py
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging
from pathlib import Path

def browse_website(url):
    driver, text = scrape_text_with_selenium(url)
    # add_header(driver)
    links = scrape_links_with_selenium(driver)

    # Limit links to 5
    if len(links) > 5:
        links = links[:5]
    close_browser(driver)

    return text


def scrape_text_with_selenium(url):
    logging.getLogger("selenium").setLevel(logging.CRITICAL)

    options = Options()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Get the HTML content directly from the browser's DOM
    page_source = driver.execute_script("return document.body.outerHTML;")
    soup = BeautifulSoup(page_source, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)
    return driver, text


def scrape_links_with_selenium(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    hyperlinks = extract_hyperlinks(soup)

    return format_hyperlinks(hyperlinks)


def close_browser(driver):
    driver.quit()


def extract_hyperlinks(soup):
    return [(link.text, link["href"]) for link in soup.find_all("a", href=True)]


def format_hyperlinks(hyperlinks):
    return [f"{link_text} ({link_url})" for link_text, link_url in hyperlinks]


# def add_header(driver):
#     driver.execute_script(open(f"{file_dir}/js/overlay.js", "r").read())

if __name__ == "__main__":
    import sys
    url = sys.argv[1]

    if not url.startswith("http"):
        sys.exit("Please enter a valid url")

    print(browse_website(url))
