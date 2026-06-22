import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import pandas as pd
import re
import os

def uww_main_scraper_block():
    url = input("Pass the url you want to extract content from, if you may, appreciate it ")

    HEADERS = {
        'User-Agent': "WebScrapper 1.0 (Contact: fernandorevengaperez@gmail.com)"
    }

    print(f"Searching for data at: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Connection or HTTP error: {e}")

    soup = BeautifulSoup(html_content, 'html.parser')
    all_tables = soup.find_all('div', class_='table-wrapper')

    data_list = []

    for wrapper in all_tables:
        # 1. Get the Weight Class (e.g., FS 57)
        weight_class = wrapper.find('h3', class_='title').text.strip()
        
        # 2. Get all rows in this table
        rows = wrapper.find_all('a', class_='table-row')
        
        for row in rows:
            # Extract specific pieces of data
            rank = row.find('div', class_='rank').text.strip()
            
            # Get Name (Joining First and Last)
            fname = row.find('span', class_='fname').text.strip()
            lname = row.find('span', class_='lname').text.strip()
            full_name = f"{fname} {lname}"
            
            country = row.find('div', class_='country').find('span', class_='text').text.strip()
            points = row.find('div', class_='pts').find('p', class_='text').text.strip()
            
            # 3. Append to our list
            data_list.append({
                "Weight Class": weight_class,
                "Rank": rank,
                "Athlete": full_name,
                "Country": country,
                "Points": points
            })

    # 4. Create the DataFrame
    df_uww = pd.DataFrame(data_list)

    print(df_uww.head())
    # --- DEBUGGING SECTION ---
    print("\n--- Pipeline Audit ---")
    print(f"Total Athletes Scraped: {len(df_uww)}")
    print(f"Categories Found: {df_uww['Weight Class'].unique()}")

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
            folder_path = os.path.join("data", "uww_raw")
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

    if not df_uww.empty:
        flag_saver = input("Do you want to save the file? Press enter if you don't wish to")
        if flag_saver:
            save_data(df_uww)
