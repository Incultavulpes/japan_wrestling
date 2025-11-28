import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://en.wikipedia.org/wiki/Wrestling_at_the_2024_Summer_Olympics"

HEADERS = {
    'User-Agent': "WebScrapper 1.0 (Contact: fernandorevengaperez@gmail.com)"
}

def fetch_and_parse_table(url):
    """Performs the HTTP request and finds the main results table."""
    print(f"Getting data in: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)

    return True

fetch_and_parse_table(PAGE_URL)
