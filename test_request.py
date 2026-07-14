"""UWW REST API Data Ingestion & Normalization Engine.

This module acts as the network boundary layer interface for the United World 
Wrestling (UWW) platform. It bypasses client-side DOM rendering by directly 
targeting backend REST API endpoints, executing high-performance memory 
accumulation patterns to land atomic datasets into the Medallion lakehouse.

Operational Design:
    - High-efficiency in-memory list tracking for vectorized Pandas creation.
    - Status-gated connection guards for fail-fast network operations.
"""

import requests as re
import pandas
import os.path

weight_classes = ["57", "61", "65", "70", "74", "79", "86", "92", "97", "125"]

def get_responses():
    """Executes a diagnostic network smoke test against UWW endpoints.

    This utility iterates through target weight categories and historical seasons, 
    pinging the REST API to print raw HTTP response codes. It is used exclusively 
    for manual network verification and sits outside the core automation workflow.

    Args:
        weight_classes: A list of string identifiers representing target 
            weight divisions (e.g., ['57kg', '61kg']).

    Returns:
        None

    Notes:
        - Bypasses local data persistence layers completely.
        - Uses a hardcoded historical season range window from 2019 to 2026.
    """

    for class_weight in weight_classes:
        for current_year in range(2026, 2018, -1):
            URL_REQUEST = "https://uww.org/apiv4/getrankinglist/api/rankings/current/seniors/fs/" + class_weight + "?page=1&season=" + str(current_year)
            status_response = re.get(URL_REQUEST)
            print(status_response)

def get_information():
    """Executes network schema discovery across UWW target endpoints.

    Iterates through specified divisions and historical seasons, validating 
    connection integrity via strict HTTP status checks, and extracts the raw 
    JSON payloads to inspect the underlying API schema structure.

    Args:
        weight_classes: A list of string identifiers representing target 
            weight divisions (e.g., ['57kg', '61kg']).

    Returns:
        None

    Raises:
        requests.exceptions.HTTPError: If any endpoint returns a non-200 
            status code, immediately halting the validation loop.

    Notes:
        - This is an out-of-band utility used strictly for schema exploration.
        - Employs a fail-fast strategy via `raise_for_status()`.
    """

    for class_weight in weight_classes:
        for current_year in range(2026, 2018, -1):
            URL_REQUEST = "https://uww.org/apiv4/getrankinglist/api/rankings/current/seniors/fs/" + class_weight + "?page=1&season=" + str(current_year)
            status_response = re.get(URL_REQUEST)
            status_response.raise_for_status()
            json_data = status_response.json()
            print(status_response)

def get_provisional():
    """Executes a hardcoded single-endpoint sandbox normalization test.

    This was an early-stage validation script used to map the JSON schema of the 
    UWW API, verify nested path keys under `hydramember`, and test column data 
    remapping sequences for the 92kg weight bracket in the 2025 season.

    Deprecated:
        Fully superseded by `get_provisional_weight_class`, which generalizes 
        this exact processing schema to dynamically loop through all target 
        seasons and weight divisions.

    Returns:
        None

    Raises:
        requests.exceptions.HTTPError: If the sandbox API network request fails.
    """
    
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

    clean_df = clean_df.rename(columns={
        'rank': 'Rank',
        'person.displayname.fullname': 'Athlete',
        'person.noc': 'Country'
    })

    standard_df = clean_df[['Weight Class', 'Rank', 'Athlete', 'Country']].copy()
    standard_df = standard_df.sort_values(by='Rank')
    top_4 = standard_df.head(4)

    print(top_4)

# SAVING DATA
def save_data(permanence_style, current_year, df, class_weight=None):
    """Routes and persists DataFrames to targeted Medallion lakehouse storage tiers.

    This function serves as the central physical storage abstraction layer. It 
    evaluates processing stages to dynamically construct folder paths, create missing 
    directories, format file names, and commit structural records to disk.

    Args:
        permanence_style: Target storage tier matching lakehouse classification 
            standards (e.g., 'Bronze' or 'Silver').
        current_year: The calendar season year context for the file naming layout.
        df: The Pandas DataFrame object to write to the filesystem.
        class_weight: Optional string weight division metric (e.g., '57', '61'). 
            Defaults to None.

    Returns:
        None
    """

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
    """Orchestrates the dynamic multi-year ingestion and normalization loop for UWW endpoints.

    This function serves as the core production runtime pipeline for the UWW module. 
    It loops through historical seasons and weight brackets, triggers network boundary 
    requests, flattens raw multi-layered JSON metadata payload responses into localized 
    DataFrames, slices the top-tier rankings, and optionally routes datasets to both 
    Bronze (isolated snapshots) and Silver (consolidated seasons) storage zones.

    Returns:
        pandas.DataFrame: A consolidated master DataFrame containing the processed 
            rankings of the *last* calendar season evaluated in the loop window.
    """

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

            clean_df = clean_df.rename(columns={
                'rank': 'Rank',
                'person.displayname.fullname': 'Athlete',
                'person.noc': 'Country'
            })

            standard_df = clean_df[['Weight Class', 'Rank', 'Athlete', 'Country']].copy()
            standard_df = standard_df.sort_values(by='Rank')
            top_four = standard_df.head(4)
            all_records.append(top_four)
        master_df = pandas.concat(all_records, ignore_index=True)
        if user_response.lower() == "yes":
            save_data("silver", current_year, master_df)
    return master_df
