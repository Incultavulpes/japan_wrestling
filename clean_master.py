"""Japan Wrestling Pipeline Silver Transformation & Cleaning Engine.

This module acts as the centralized Silver-tier compiler for the data lakehouse. 
It ingests raw, unstructured Bronze CSV files from local disk, normalizes 
schemas to enforce rigid data contracts, resolves regional naming variations, 
and serializes clean outputs to their respective Silver-tier directories.

Operational Architecture & Legacy Profiles:
    * **Track 2 (Wikipedia - Active Core)**: Cleans HTML-extracted data. It parses 
      complex structures where multiple athletes are crammed into a single cell, 
      splits athlete names from their country tags, maps countries to ISO 3-letter 
      codes, normalizes weight categories, and formats the output into an active, 
      clean 4-column schema.
    * **Track 1 (UWW - Legacy/Manual Fallback)**: The automated live UWW pipeline 
      is fully self-enclosed within `test_request.py` (which handles ingestion 
      and normalization together). The UWW cleaning functions in this module 
      (`trim_world`) are preserved here as **legacy utilities** to support manual 
      adhoc transformations or historical data cleaning runs if needed.

Data Processing Contracts (Silver Schema):
    All finalized Silver-tier datasets produced by this module conform to:
    `["Weight Class", "Rank", "Athlete", "Country"]`

Directory Structure Mapping:
    * **Sources (Bronze)**:
        - Wikipedia Raw: `data/raw/`
        - UWW Raw: `data/uww_raw/`
    * **Destinations (Silver)**:
        - Wikipedia Cleaned: `data/silver/wikipedia/`
        - UWW Cleaned: `data/silver/uww/`
"""

import pandas as pand
import os.path
import re

def retrieve_data(file_handle, file_type):
    """Dynamically resolves paths and loads a raw Bronze dataset into memory.

    This function acts as the disk ingestion layer of the cleaning pipeline. 
    It dynamically routes the file lookup based on the source platform type, 
    verifies file existence on the local storage partition, and safely loads 
    the raw CSV into a pandas DataFrame.

    Args:
        file_handle (str): The filename (including extension, e.g., 'paris_2024.csv') 
            to be fetched from disk.
        file_type (str): The data pipeline source designation. Must be either 
            'uww' or 'wikipedia' (case-insensitive) to determine the base directory path.

    Returns:
        pandas.DataFrame or None: Returns the loaded dataset as a DataFrame 
            if the file exists and is readable; returns None if the path resolution 
            or file verification fails.
    """

    if file_type.lower() == "uww":
        usual_path = os.path.join("data", "uww_raw")
    elif file_type.lower() == "wikipedia":
        usual_path = os.path.join("data", "raw")
    else:
        print("Non existing file type")
        return None

    full_path = os.path.join(usual_path, file_handle)
    if os.path.isfile(full_path):
        df = pand.read_csv(full_path)
        return df
    else:
        print("Non existing file handle, run the script again")
        return None

def trim_world(data_frame):
    """Enforces the Silver-tier data contract on raw UWW Bronze datasets.

    NOTE (Legacy Architecture): This function serves as a manual, adhoc fallback 
    utility. While active automated pipelines consolidate this step directly within 
    the core extraction modules, this function remains supported to manually clean 
    and format legacy or historical offline UWW raw extractions.

    Transformations Applied:
        1. **Rank Filtering**: Discards matches where the athlete's final placing 
           is 5th or lower, preserving only the medal-winning tiers (Ranks 1 to 4).
        2. **Column Pruning**: Drops the non-contract 'Points' column to match the 
           unified Silver schema.
        3. **Weight Normalization**: Strips the 'FS' (Freestyle) signifier from 
           the 'Weight Class' string and appends the unified ' kg' suffix 
           (e.g., '74FS' -> '74 kg').

    Args:
        data_frame (pandas.DataFrame): The raw Bronze UWW DataFrame containing 
            the columns 'Weight Class', 'Rank', 'Athlete', 'Country', and 'Points'.

    Returns:
        pandas.DataFrame: The normalized Silver-compliant DataFrame restricted 
            strictly to the top four placements.
    """

    data_frame = data_frame[data_frame["Rank"] < 5]
    data_frame = data_frame.drop(columns = ["Points"])
    data_frame["Weight Class"] = data_frame["Weight Class"].str.strip("FS") + " kg"
    return data_frame

def wikipedia_trim(data_frame):
    """Normalizes raw Wikipedia tournament data into a clean, unrolled Silver dataset.

    This engine is the core transformation layer for Track 2. It converts unstructured 
    and non-standardized Wikipedia tables into a clean, normalized schema. It handles 
    irregular cell structures, parses combined athlete/country strings, maps country names 
    to ISO 3-letter codes, normalizes diverse weight class nomenclatures, and handles 
    wrestling's double-bronze-medal structure.

    Detailed Processing Stages:
        1. **Country & Athlete Parsing**: Uses a nested regular expression engine to 
           separate adjacent text strings (e.g., "Gable StevesonUnited States" into 
           "Gable Steveson" and "USA" using a custom 3-letter ISO mapping).
        2. **Weight Class Standardization**: Employs a deterministic extraction engine 
           using regular expressions to convert mixed strings (like "120 kg[c]" or "55kg") 
           into "120 kg". Falls back to an lookup dictionary for older named categories 
           (e.g., "Lightweight" -> "70 kg").
        3. **Double-Bronze State-Machine Unrolling**: 
           In Olympic/World wrestling tournament layouts, identical weight classes are 
           split across adjacent rows to account for two bronze medal paths. 
           This module tracks previously encountered weight categories in-memory:
            - **First Encounter**: Appends Gold (Rank 1), Silver (Rank 2), and 
              the first Bronze (Rank 3).
            - **Second Encounter**: Skips the duplicate Gold/Silver cells and extracts 
              the second Bronze (Rank 4).

    Args:
        data_frame (pandas.DataFrame): The raw, scraped Wikipedia DataFrame containing 
            columns matching the medal structure (typically columns starting with the 
            weight class event, followed by 'Gold', 'Silver', and 'Bronze').

    Returns:
        pandas.DataFrame: The restructured, sorted, and completely standardized 
            Silver dataset conforming to: `["Weight Class", "Rank", "Athlete", "Country"]`.
    """

    country_map = {
        "UnitedStates": "USA", "Japan": "JPN", "India": "IND", "Kazakhstan": "KAZ",
        "ROC": "ROC", "Azerbaijan": "AZE", "Iran": "IRI", "Belarus": "BLR",
        "Uzbekistan": "UZB", "SanMarino": "SMR", "Cuba": "CUB", "Italy": "ITA",
        "Georgia": "GEO", "Turkey": "TUR", "Russia": "RUS", "Romania": "ROU", 
        "NorthKorea": "PRK", "Hungary": "HUN", "PuertoRico": "PRI", "Ukraine": "UKR",
        "Slovakia": "SVK", "Bulgaria": "BGR", "Kyrgyzstan": "KGZ", "Tajikistan": "TJK",
        "SouthKorea": "KOR", "Greece": "GRC", "Macedonia": "MKD", "Canada": "CAN",
        "SovietUnion": "SUN", "Belgium": "BEL", "Finland": "FIN", "Germany": "DEU",
        "Armenia": "ARM", "UnifiedTeam": "UNI", "EastGermany": "DDR", "Yugoslavia": "YUG",
        "Czechoslovakia": "CSK", "Syria": "SYR", "WestGermany": "DEU", 
        "GreatBritain": "GBR", "Poland": "POL", "Mongolia": "MNG", "Sweden": "SWE",
        "France": "FRA", "UnitedTeamofGermany": "DEU", "Pakistan": "PAK",
        "Australia": "AUS", "Switzerland": "CHE", "Estonia": "EST", "Austria": "AUT",
        "Denmark": "DNK", "Norway": "NOR"
    }

    weight_map = {
        "Flyweight": "52 kg", "Bantamweight": "57 kg", "Featherweight": "63 kg",
        "Lightweight": "70 kg", "Welterweight": "78 kg", "Middleweight": "87 kg",
        "Light Heavyweight": "97 kg", "Heavyweight": "+97 kg"
    }

    REGEX_COUNTRY = re.compile(r'.*(\w)([A-Z][a-zA-Z\s]*)$', flags=re.UNICODE)
    # New robust regex pattern to extract 2 or 3 digits followed by optional spaces and 'kg'
    # This automatically leaves behind junk like '[c]' and 'details'
    REGEX_WEIGHT = re.compile(r'(\d{2,3})\s*(kg)', flags=re.IGNORECASE)

    def split_athlete_and_country(raw_string):
        """
        Splits 'Gable StevesonUnited States' -> 'Gable Steveson', 'USA'
        Splits 'Myles AmineSan Marino' -> 'Myles Amine', 'SMR'
        """
        if not isinstance(raw_string, str) or not raw_string:
            return "", ""
    
        # Updated Regex: capturing multi-word uppercase starting countries with spaces
        match = REGEX_COUNTRY.search(raw_string)
        if match:
            split_idx = match.start(2)
            athlete = raw_string[:split_idx].strip()
            country_raw = raw_string[split_idx:].strip()
            # Remove inner spaces for dictionary lookup (e.g., "United States" -> "UnitedStates")
            country_lookup = country_raw.replace(" ", "")
        else:
            athlete = raw_string
            country_lookup = ""
            country_raw = ""
        
        country_iso = country_map.get(country_lookup, country_raw)
        return athlete, country_iso

    # 2. Initialize Accumulator and State Tracker
    data_accumulator = []
    processed_events = {}

    col_first = data_frame.columns[0]

    # 3. Process the DataFrame in-memory by converting rows to native dictionaries
    records = data_frame.to_dict(orient="records")

    for row in records:
        raw_event = str(row[col_first])
        
        # --- NEW DETERMINISTIC EXTRACTION ENGINE ---
        weight_match = REGEX_WEIGHT.search(raw_event)
        if weight_match:
            # Reconstruct clean token: Group 1 (digits) + ' ' + Group 2 ('kg')
            weight_class = f"{weight_match.group(1)} {weight_match.group(2).lower()}"
        else:
            # Fallback for historical named categories (e.g., "Flyweight details" -> "Flyweight")
            cleaned_event = raw_event.replace("details", "").strip()
            
            # Title-case it so "flyweight" and "Flyweight" match identically
            weight_class = cleaned_event.title()
            # Translate the weight to a numerical string here
            for key_flag in weight_map:
                if key_flag == weight_class:
                    weight_class = weight_map[key_flag]

        if weight_class not in processed_events:
            # First encounter: Extract Gold (Rank 1), Silver (Rank 2), and 1st Bronze (Rank 3)
            processed_events[weight_class] = True
        
            gold_name, gold_geo = split_athlete_and_country(row['Gold'])
            silver_name, silver_geo = split_athlete_and_country(row['Silver'])
            bronze1_name, bronze1_geo = split_athlete_and_country(row['Bronze'])
        
            data_accumulator.append({"Weight Class": weight_class, "Rank": 1, "Athlete": gold_name, "Country": gold_geo})
            data_accumulator.append({"Weight Class": weight_class, "Rank": 2, "Athlete": silver_name, "Country": silver_geo})
            data_accumulator.append({"Weight Class": weight_class, "Rank": 3, "Athlete": bronze1_name, "Country": bronze1_geo})
        else:
            # Second encounter: Skip Gold/Silver duplicates, extract only 2nd Bronze (Rank 4)
            bronze2_name, bronze2_geo = split_athlete_and_country(row['Bronze'])
            data_accumulator.append({"Weight Class": weight_class, "Rank": 4, "Athlete": bronze2_name, "Country": bronze2_geo})

    # 4. Generate structured DataFrame conforming to the data contract
    final_columns = ["Weight Class", "Rank", "Athlete", "Country"]
    final_df = pand.DataFrame(data_accumulator, columns=final_columns)
    final_df = final_df.sort_values(by=["Weight Class", "Rank"]).reset_index(drop=True)
    
    return final_df

def save_data(df, file_type):
    """Saves the normalized DataFrame to a CSV file in the Silver storage tier.

    Prompts the user interactively for a target filename, guarantees a compliant 
    '.csv' file extension, and dynamically routes the output directory based on the 
    data source pipeline type. If the target folders do not exist on the filesystem, 
    they are created on the fly before executing a safe, UTF-8 encoded serialization.

    Args:
        df (pandas.DataFrame): The standardized Silver-compliant DataFrame 
            ready for storage.
        file_type (str): The data pipeline source designation. Must be either 
            'uww' or 'wikipedia' (case-insensitive) to resolve the destination 
            directory branch.

    Returns:
        bool: True if the file was successfully committed to disk, False if 
            the 'file_type' is invalid or if an exception occurred during 
            directory creation/file writing.
    """

    try:
        filename = input("Choose the saving name: ")
        
        # Ensure the filename has the correct extension
        if not filename.lower().endswith(".csv"):
            filename += ".csv"
            
        # Define and create the directory structure
        if file_type.lower() == "wikipedia":
            folder_path = os.path.join("data", "silver", "wikipedia")
            os.makedirs(folder_path, exist_ok=True)
            # Combine folder and filename for the final destination
            saving_path = os.path.join(folder_path, filename)
            # Write to disk
            df.to_csv(saving_path, index=False, encoding="utf-8")
        elif file_type.lower() == "uww":
            folder_path = os.path.join("data", "silver", "uww")
            os.makedirs(folder_path, exist_ok=True)
            # Combine folder and filename for the final destination
            saving_path = os.path.join(folder_path, filename)
            # Write to disk
            df.to_csv(saving_path, index=False, encoding="utf-8")
        else:
            return False
    
        print(f"SUCCESS: Data saved to {saving_path}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to save data. Details: {e}")
        return False

def execution_flow_clean_master(file_type):
    """Orchestrates the terminal-based Silver cleaning pipeline for a selected track.

    This function acts as the execution wrapper called by the main menu (main.py) 
    to manage Silver-tier transformations. It handles both the active Wikipedia 
    cleaning pipeline and the legacy, manual UWW utility path.

    Pipeline Routing Profiles:
        * **Active Core (Wikipedia)**: Standard transformation workflow. Ingests raw 
          scraped tables, applies heuristic parsing rules, unrolls the double-bronze 
          medal structure, and serializes the structured schema to Silver storage.
        * **Legacy/Manual Fallback (UWW)**: Runs the legacy `trim_world` contract on 
          offline raw UWW data. Note that standard automated Track 1 runs bypass this 
          entire module, handling ingestion and normalization natively within the 
          dedicated `test_request.py`.

    Args:
        file_type (str): The target pipeline track. Must be 'uww' or 'wikipedia' 
            (case-insensitive), which dictates both the directory routing and 
            the specific cleaning rules applied.

    User Inputs (CLI Prompts):
        file_handle (str): The filename of the raw CSV file to clean (e.g., 'paris_2024.csv').
        flag_saver (str): Entering any non-empty input at the final saving prompt 
            initiates the file-writing process.

    Side Effects:
        - Prompts the user via terminal inputs.
        - Prints data previews and pipeline execution messages to the console.
        - Triggers file writes to the 'data/silver/' subdirectory hierarchy.

    Returns:
        None
    """

    # --- Standard Core Execution Flow ---
    file_handle = input("Enter the file handle: ")
    # file_type = input("Enter the file type (uww/wikipedia): ")

    df = retrieve_data(file_handle, file_type)

    if df is not None:
        if file_type.lower() == "uww":
            df = trim_world(df)
        elif file_type.lower() == "wikipedia":
            df = wikipedia_trim(df)

        print("\n--- Processed Silver Data Output ---")
        print(df)
    else:
        print("Pipeline execution failed due to empty or missing dataset.")

    if not df.empty:
        flag_saver = input("Do you want to save the file? Press enter if you don't wish to")
        if flag_saver:
            save_data(df, file_type)

