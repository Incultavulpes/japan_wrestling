import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

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


results_converted = fetch_and_parse_table(PAGE_URL, "Event", "Gold")

print(f"This is the table: {results_converted}")

def extract_and_clean_data(results_table):
    rows = results_table.find_all('tr')
    if not rows:
        return [], []

    header_cells = rows[0].find_all(['th', 'td'])
    initial_headers = [h.get_text(strip=True) for h in header_cells]
    total_cols = len(initial_headers) 
    
    all_data = []
    rowspan_tracker = {} 

    for row in rows[1:]:
        cells = row.find_all(['td', 'th'])
        raw_cells = list(cells)
        row_content = [None] * total_cols # Pre-fill a row with "Empty Slots"
        
        # We use col_idx to navigate our "Virtual Grid"
        col_idx = 0
        while col_idx < total_cols:
            
            # 1. Check Rowspan Memory (Vertical)
            if col_idx in rowspan_tracker and rowspan_tracker[col_idx]['count'] > 0:
                row_content[col_idx] = rowspan_tracker[col_idx]['value']
                rowspan_tracker[col_idx]['count'] -= 1
                col_idx += 1 # Move to next slot in the grid
                
            # 2. Place HTML Cell (Horizontal + New Rowspans)
            elif raw_cells:
                cell = raw_cells.pop(0)
                text = cell.get_text(strip=True)
                
                # Handle Colspan (Width)
                c_span = int(cell.get('colspan', 1))
                # Handle Rowspan (Height)
                r_span = int(cell.get('rowspan', 1))
                
                # Fill the current and any adjacent "colspan" slots
                for _ in range(c_span):
                    if col_idx < total_cols:
                        row_content[col_idx] = text
                        
                        # If this cell also has a rowspan, track it for future rows
                        if r_span > 1:
                            rowspan_tracker[col_idx] = {'value': text, 'count': r_span - 1}
                        
                        col_idx += 1 # Move to next slot
            else:
                # Security fallback
                if col_idx < total_cols:
                    row_content[col_idx] = ""
                col_idx += 1

        all_data.append(row_content)

    return all_data, initial_headers

full_table, header_columns = extract_and_clean_data(results_converted)

def visual_table(header_columns, full_table):
    tidy_table = PrettyTable(header_columns)
    for i in range(len(full_table)):
            tidy_table.add_row(full_table[i])
    return tidy_table

print(f"Those are the columns: {header_columns}")
print(f"The fullnes of our table now: {full_table}")
print(f"{visual_table(header_columns, full_table)}")