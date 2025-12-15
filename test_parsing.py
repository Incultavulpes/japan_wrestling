import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://en.wikipedia.org/wiki/Wrestling_at_the_2024_Summer_Olympics"

HEADERS = {
    'User-Agent': "WebScrapper 1.0 (Contact: fernandorevengaperez@gmail.com)"
}

def is_table_a_match(table, keyword_identifier, aux_one=""):
    """
    Checks if the HTML table contains the required headers using a robust, flexible search.

    This function is core to identifying the correct 'wikitable' among many on the page.

    Args:
        table (BeautifulSoup Tag): The <table> object to inspect.
        keyword_identifier (str): The primary header the table MUST contain (e.g., "Gold").
        aux_one (str, optional): The secondary header for double-filtering (e.g., "Event").

    Returns:
        bool: True if the table meets the filtering criteria, False otherwise.
    """

    def find_flexible(table_element, target_keyword):
        target_lower = target_keyword.lower()

        return table_element.find('th', 
                                  string = lambda t: t and target_lower in t.lower())
    
    if not find_flexible(table, keyword_identifier):
        return False
    
    if aux_one:
        if not find_flexible(table, aux_one):
            return False

    return True

def fetch_and_parse_table(url, keyword_identifier, aux_one = ""):
    """
    Performs the HTTP request and applies the robust filter to find the results table.

    Args:
        url (str): URL of the Wikipedia page.
        keyword_identifier (str): Primary header for the filter function.
        aux_one (str, optional): Secondary header for the double-filter.

    Returns:
        BeautifulSoup Tag: The results table if found, or None on error/not found.
    """

    print(f"Getting data in: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        html_content = response.text
    
    except requests.exceptions.RequestException as e:
        print(f"Connection or HTTP error: {e}")
        return []

    soup = BeautifulSoup(html_content, 'html.parser')

    results_table = None
    all_wikitables = soup.find_all('table', class_='wikitable')
    
    for table in all_wikitables:
        
        if is_table_a_match(table, keyword_identifier, aux_one):
            results_table = table
            break

    if results_table is None:
        print("❌ ERROR: Medal table not found. Could not find a 'wikitable' with 'Gold' header.")
        return [], None

    return results_table


results_converted = fetch_and_parse_table(PAGE_URL, "Gold", "Event")

print(f"This is the table: {results_converted}")

def extract_and_clean_data(results_table):
    rows = results_table.find_all('tr')
    if not rows:
        return []

    header_columns = rows[0].find_all('th')
    cleaned_text = ""
    cleaned_columns = []

    for head in header_columns:
        cleaned_text = head.get_text(strip="True")
        cleaned_columns.append(cleaned_text)

    return cleaned_columns

header_columns = extract_and_clean_data(results_converted)

print(f"Those are the columns: {header_columns}")