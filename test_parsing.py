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
        response.raise_for_status()
        html_content = response.text
    
    except requests.exceptions.RequestException as e:
        print(f"Connection or HTTP error: {e}")
        return []

    soup = BeautifulSoup(html_content, 'html.parser')

    medal_table = None
    all_wikitables = soup.find_all('table', class_='wikitable')
    for table in all_wikitables:
        if table.find('th', string='Gold'):
            results_table = table
            break

    if results_table is None:
        print("❌ ERROR: Medal table not found. Could not find a 'wikitable' with 'Gold' header.")
        return []
    
    extracted_data = []
    rows = results_table.find_all('tr')

    print(f"Table found with {len(rows)} rows. Extracting first 5 for testing...")

    for i, row in enumerate(rows):
        if i >= 5 and i > 0:
            break
        cells = row.find_all(['td', 'th'])

        if cells:
            cleaned_values = [cell.text.strip() for cell in cells if cell.text.strip()]
            if len(cleaned_values) > 3:
                extracted_data.append(cleaned_values)

    return extracted_data, results_table


data, results_converted = fetch_and_parse_table(PAGE_URL)

print(f"This is the table: {results_converted}")