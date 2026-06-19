import pandas as pand
import os.path
import re

# Data retriever
def retrieve_data(file_handle, file_type):
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

# UWW contract
def trim_world(data_frame):
    data_frame = data_frame[data_frame["Rank"] < 5]
    data_frame = data_frame.drop(columns = ["Points"])
    data_frame["Weight Class"] = data_frame["Weight Class"].str.strip("FS") + " kg"
    return data_frame

# Wikipedia contract
def wikipedia_trim(data_frame):
    # 1. ISO 3-Letter Country Map
    country_map = {
        "UnitedStates": "USA", "Japan": "JPN", "India": "IND", "Kazakhstan": "KAZ",
        "ROC": "ROC", "Azerbaijan": "AZE", "Iran": "IRI", "Belarus": "BLR",
        "Uzbekistan": "UZB", "SanMarino": "SMR", "Cuba": "CUB", "Italy": "ITA",
        "Georgia": "GEO", "Turkey": "TUR"
    }

    REGEX_COUNTRY = re.compile(r'([a-z])([A-Z][a-zA-Z\s]*)$')

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

    # 3. Process the DataFrame in-memory by converting rows to native dictionaries
    # This preserves your custom unrolling logic without secondary I/O reads.
    records = data_frame.to_dict(orient="records")

    for row in records:
        # Clean the weight class string: '57 kgdetails' -> '57 kg'
        weight_class = str(row['Event']).replace("details", "").strip()
    
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


# --- Standard Core Execution Flow ---
file_handle = input("Enter the file handle: ")
file_type = input("Enter the file type (uww/wikipedia): ")

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

def save_data(df, file_type):
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

if not df.empty:
    flag_saver = input("Do you want to save the file? Press enter if you don't wish to")
    if flag_saver:
        save_data(df, file_type)

