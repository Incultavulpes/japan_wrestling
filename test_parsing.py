import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import pandas as pd
import re
import os

HEADERS = {
    'User-Agent': "WebScrapper 1.0 (Contact: fernandorevengaperez@gmail.com)"
}

def is_table_a_match(table, keyword_header, aux_header="", signature_data=""):
    """
    Evaluates a table's eligibility based on structural and content-based filters.

    Args:
        table (bs4.Tag): The <table> object to inspect.
        keyword_header (str): A string that must exist in a <th> tag.
        aux_header (str, optional): A second string for stricter header validation.
        signature_data (str, optional): A unique data value (like a name) that must 
                                       exist in a <td> tag to confirm identity.

    Returns:
        bool: True if all provided criteria are found within the table.
    """
    def find_flexible(table_element, target_keyword, tag_to_search):
        """
        Nested helper that uses a lambda to search for text within specific tags,
        handling nested HTML like links or spans via get_text().
        """
        target_lower = target_keyword.lower()
        return table_element.find(lambda tag: tag.name == tag_to_search and 
                                  target_lower in tag.get_text().lower())
    
    # 1. Structural Check (Validating the column headers)
    if not find_flexible(table, keyword_header, 'th'):
        return False
    if aux_header and not find_flexible(table, aux_header, 'th'):
        return False

    # 2. Signature Check (Validating specific row content/data)
    if signature_data:
        if not find_flexible(table, signature_data, 'td'):
            return False

    return True

def fetch_and_parse_table(url, keyword_identifier, aux_one="", signature_data=""):
    """
    Performs the HTTP request and filters through all wikitables on a page.

    Args:
        url (str): The destination Wikipedia URL.
        keyword_identifier (str): Primary string to look for in headers.
        aux_one (str): Secondary string to look for in headers.
        signature_data (str): Specific data to identify the correct table 
                              among identical structures.

    Returns:
        bs4.Tag: The matching <table> object, or None if no match is found.
    ```python
    """
    print(f"Searching for data at: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Connection or HTTP error: {e}")
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    all_wikitables = soup.find_all('table', class_='wikitable')
    
    for table in all_wikitables:
        if is_table_a_match(table, keyword_identifier, aux_one, signature_data):
            return table

    print("❌ ERROR: Match not found. Check your headers or signature data.")
    return None

def extract_and_clean_data(results_table):
    """
    Parses a <table> into a 2D list, resolving HTML rowspans and colspans.

    This function uses a 'Virtual Grid' approach. It tracks rowspans in a dictionary
    and pre-fills slots to ensure the resulting 2D list remains aligned even 
    when the HTML table uses complex spanning.

    Args:
        results_table (bs4.Tag): The BeautifulSoup table object.

    Returns:
        tuple: (all_data [list of lists], initial_headers [list of strings])
    """
    if results_table is None:
        return [], []

    rows = results_table.find_all('tr')
    if not rows:
        return [], []

    # Identify the structure based on the first row (headers)
    header_cells = rows[0].find_all(['th', 'td'])
    initial_headers = [h.get_text(strip=True) for h in header_cells]
    total_cols = len(initial_headers) 
    
    all_data = []
    rowspan_tracker = {} 

    for row in rows[1:]:
        cells = row.find_all(['td', 'th'])
        raw_cells = list(cells)
        row_content = [None] * total_cols 
        
        col_idx = 0
        while col_idx < total_cols:
            # 1. Apply Vertical Memory (Rowspans from previous rows)
            if col_idx in rowspan_tracker and rowspan_tracker[col_idx]['count'] > 0:
                row_content[col_idx] = rowspan_tracker[col_idx]['value']
                rowspan_tracker[col_idx]['count'] -= 1
                col_idx += 1 
                
            # 2. Process Current Row Cells
            elif raw_cells:
                cell = raw_cells.pop(0)
                text = cell.get_text(strip=True)
                
                c_span = int(cell.get('colspan', 1))
                r_span = int(cell.get('rowspan', 1))
                
                # Handle horizontal spanning (colspan)
                for _ in range(c_span):
                    if col_idx < total_cols:
                        row_content[col_idx] = text
                        # Store vertical spanning for future rows
                        if r_span > 1:
                            rowspan_tracker[col_idx] = {'value': text, 'count': r_span - 1}
                        col_idx += 1 
            else:
                # Fallback for irregular table structures
                if col_idx < total_cols:
                    row_content[col_idx] = ""
                col_idx += 1

        all_data.append(row_content)

    return all_data, initial_headers

def visual_table(header_columns, full_table):
    """
    Converts raw data into a PrettyTable object for terminal display.
    """
    tidy_table = PrettyTable(header_columns)
    for row in full_table:
        tidy_table.add_row(row)
    return tidy_table

def save_data(df):
    """
    Saves the provided DataFrame to a CSV file in the data/raw directory.
    Prompts the user for a filename and ensures proper formatting and encoding.
    """
    try:
        filename = input("Choose the saving name: ")
        
        # Ensure the filename has the correct extension
        if not filename.lower().endswith(".csv"):
            filename += ".csv"
            
        # Define and create the directory structure
        folder_path = os.path.join("data", "raw")
        os.makedirs(folder_path, exist_ok=True)
        
        # Combine folder and filename for the final destination
        saving_path = os.path.join(folder_path, filename)
        
        # Write to disk
        df.to_csv(saving_path, index=False, encoding="utf-8")
        
        print(f"SUCCESS: Data saved to {saving_path}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to save data. Details: {e}")
        return False

def wikipedia_main_scraper_block():
    # --- MAIN EXECUTION ---
    # Collect user inputs to make the script adaptable to any Wikipedia page
    PAGE_URL = input("Enter Wikipedia URL: ")
    header_one = input("Enter primary header (e.g., Event): ")
    header_two = input("Enter secondary header (e.g., Gold): ")
    signa_data = input("Enter signature data (e.g., Athlete Name): ")

    # Step 1: Find the table
    results_converted = fetch_and_parse_table(PAGE_URL, header_one, header_two, signa_data)

    # Step 2: Extract and display if a match was found
    if results_converted:
        full_table, header_columns = extract_and_clean_data(results_converted)
        
        print(f"\nSuccessfully extracted {len(full_table)} rows.")
        print(visual_table(header_columns, full_table))
    else:
        print("Execution halted: Table not found.")

    df = pd.DataFrame(full_table, columns=header_columns)

    if not df.empty:
        flag_saver = input("Do you want to save the file? Press enter if you don't wish to")
        if flag_saver:
            save_data(df)
