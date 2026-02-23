import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import pandas as pd
import re
import os

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
