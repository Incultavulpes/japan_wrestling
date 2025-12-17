import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://en.wikipedia.org/wiki/Wrestling_at_the_2024_Summer_Olympics"

HEADERS = {
    'User-Agent': "WebScrapper 1.0 (Contact: fernandorevengaperez@gmail.com)"
}

def is_table_a_match(table, keyword_identifier, aux_one=""):
    """
    Checks if an HTML table contains specific headers using a flexible search.

    Args:
        table (bs4.Tag): The <table> object to inspect.
        keyword_identifier (str): Primary header required (e.g., "Gold").
        aux_one (str, optional): Secondary header for validation (e.g., "Event").

    Returns:
        bool: True if criteria are met, False otherwise.

    Note on Architecture:
        This function uses a nested helper 'find_flexible'. While this causes the 
        helper to be redefined on every call, it was intentionally chosen to 
        achieve 'Fortress Encapsulation.' By nesting the logic, we ensure the 
        internal search mechanics do not pollute the global namespace and 
        remain inaccessible to other parts of the script.
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
        return [], []

    # --- 1. HEADER PROCESSING (with Bronze Split) ---
    header_cells = rows[0].find_all('th')
    initial_headers = [h.get_text(strip=True) for h in header_cells]
    
    final_headers = []
    for h in initial_headers:
        if h == "Bronze":
            final_headers.extend(["Bronze_1", "Bronze_2"])
        else:
            final_headers.append(h)

    # --- 2. DATA PROCESSING (with Rowspan Logic) ---
    all_data = []
    # This 'rowspan_tracker' keeps track of: [value, remaining_rows]
    # We initialize it with None for each column
    rowspan_tracker = {} 

    for row_idx, row in enumerate(rows[1:]): # Skip the header row
        cells = row.find_all(['td', 'th'])
        row_content = []
        cell_idx = 0
        
        # We need to loop through the total number of columns we expect
        # because some cells might be 'missing' due to a rowspan above.
        total_cols = len(initial_headers) 
        
        raw_cells = list(cells)
        
        for col_idx in range(total_cols):
            # Check if there is an active rowspan for this column from a previous row
            if col_idx in rowspan_tracker and rowspan_tracker[col_idx]['count'] > 0:
                row_content.append(rowspan_tracker[col_idx]['value'])
                rowspan_tracker[col_idx]['count'] -= 1
            else:
                # If no rowspan active, take the next available cell from the HTML
                if raw_cells:
                    cell = raw_cells.pop(0)
                    text = cell.get_text(strip=True)
                    row_content.append(text)
                    
                    # If this cell HAS a rowspan, start tracking it
                    if cell.has_attr('rowspan'):
                        count = int(cell.get('rowspan'))
                        # -1 because we just used the first instance of it now
                        rowspan_tracker[col_idx] = {'value': text, 'count': count - 1}
                else:
                    row_content.append("") # Fallback for malformed rows

        # Special handling: If the HTML row only had 1 Bronze cell 
        # but our header has 2, we might need to adjust. 
        # (Wikipedia often uses two <td> for Bronze, so this usually works)
        all_data.append(row_content)

    return all_data, final_headers

full_table, header_columns = extract_and_clean_data(results_converted)

print(f"Those are the columns: {header_columns}")
print(f"The fullnes of our table now: {full_table}")