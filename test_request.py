import requests as re
import pandas
import os.path

weight_classes = ["57", "61", "65", "70", "74", "79", "86", "92", "97", "125"]

def get_responses():
    for class_weight in weight_classes:
        for current_year in range(2026, 2018, -1):
            URL_REQUEST = "https://uww.org/apiv4/getrankinglist/api/rankings/current/seniors/fs/" + class_weight + "?page=1&season=" + str(current_year)
            status_response = re.get(URL_REQUEST)
            print(status_response)

def get_information():
    for class_weight in weight_classes:
        for current_year in range(2026, 2018, -1):
            URL_REQUEST = "https://uww.org/apiv4/getrankinglist/api/rankings/current/seniors/fs/" + class_weight + "?page=1&season=" + str(current_year)
            status_response = re.get(URL_REQUEST)
            status_response.raise_for_status()
            json_data = status_response.json()
            print(status_response)

def get_provisional():
    URL_REQUEST = "https://uww.org/apiv4/getrankinglist/api/rankings/current/seniors/fs/" + "92" + "?page=1&season=" + "2025"
    status_response = re.get(URL_REQUEST)
    status_response.raise_for_status()
    json_data = status_response.json()
    wrestler_list = json_data["content"]["hydramember"]
    df = pandas.json_normalize(wrestler_list)
    clean_df = df[[
        'rank', 
        'person.displayname.fullname', 
        'person.noc', 
        'uwwPoints', 
        'season'
    ]].copy()

    clean_df['Weight Class'] = "92 kg"

    # 2 & 3. Rename the existing columns to your target standard
    clean_df = clean_df.rename(columns={
        'rank': 'Rank',
        'person.displayname.fullname': 'Athlete',
        'person.noc': 'Country'
    })

    # 4. Filter down to your exact 4 standard columns (dropping uwwPoints and season)
    standard_df = clean_df[['Weight Class', 'Rank', 'Athlete', 'Country']].copy()

    # 5. Sort by Rank and grab the top 4
    standard_df = standard_df.sort_values(by='Rank')
    top_4 = standard_df.head(4)

    print(top_4)

# SAVING DATA
def save_data(permanence_style, current_year, df, class_weight=None):
    if permanence_style.lower() == "bronze":
        folder_path = os.path.join("data", "uww_raw")
        os.makedirs(folder_path, exist_ok=True)
        # Combine folder and filename for the final destination
        weight_str = f"_{class_weight}kg" if class_weight else ""
        filename = f"uww_{current_year}{weight_str}_raw_results.csv"
        saving_path = os.path.join(folder_path, filename)
        # Write to disk
        df.to_csv(saving_path, index=False, encoding="utf-8")
    elif permanence_style.lower() == "silver":
        folder_path = os.path.join("data", "silver", "uww")
        os.makedirs(folder_path, exist_ok=True)
        # Combine folder and filename for the final destination
        filename = f"{current_year}_uww_clean_results.csv"
        saving_path = os.path.join(folder_path, filename)
        # Write to disk
        df.to_csv(saving_path, index=False, encoding="utf-8")

#UWW RETRIEVER
def get_provisional_weight_class():
    user_response = input("Do you want to save the data? Yes or no ")
    for current_year in range(2026, 2018, -1):
        all_records = []
        for class_weight in weight_classes:
            URL_REQUEST = "https://uww.org/apiv4/getrankinglist/api/rankings/current/seniors/fs/" + class_weight + "?page=1&season=" + str(current_year)
            status_response = re.get(URL_REQUEST)
            status_response.raise_for_status()
            json_data = status_response.json()
            wrestler_list = json_data["content"]["hydramember"]
            df = pandas.json_normalize(wrestler_list)
            clean_df = df[[
                'rank', 
                'person.displayname.fullname', 
                'person.noc', 
                'uwwPoints', 
                'season'
            ]].copy()

            clean_df['Weight Class'] = class_weight + " kg"
            if user_response.lower() == "yes":
                save_data("bronze", current_year, clean_df, class_weight)

            # 2 & 3. Rename the existing columns to your target standard
            clean_df = clean_df.rename(columns={
                'rank': 'Rank',
                'person.displayname.fullname': 'Athlete',
                'person.noc': 'Country'
            })

            # 4. Filter down to your exact 4 standard columns (dropping uwwPoints and season)
            standard_df = clean_df[['Weight Class', 'Rank', 'Athlete', 'Country']].copy()

            # 5. Sort by Rank and grab the top 4
            standard_df = standard_df.sort_values(by='Rank')
            top_four = standard_df.head(4)
            all_records.append(top_four)
        master_df = pandas.concat(all_records, ignore_index=True)
        if user_response.lower() == "yes":
            save_data("silver", current_year, master_df)
    return master_df
 
get_provisional_weight_class()
