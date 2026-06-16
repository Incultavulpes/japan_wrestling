import pandas as pand
import os.path
import csv
import re

df_aux = pand.read_csv("data/uww_raw/uww_rank.csv")

def tell_data(file_handle, file_type):
    if file_type.lower() == "uww":
        usual_path = os.path.join("data", "uww_raw")
    elif file_type.lower() == "wikipedia":
        usual_path = os.path.join("data", "processed")
    else:
        print("Non existing file type")
        return None

    if os.path.isfile(os.path.join(usual_path, file_handle)):
        df = pand.read_csv(os.path.join(usual_path, file_handle))
        print(df)
    else:
        print("Non existing file handle, run the script again")


file_handle = input("Enter the file handle ")
file_type = input("Enter the file type ")

def retrieve_data(file_handle, file_type):
    if file_type.lower() == "uww":
        usual_path = os.path.join("data", "uww_raw")
    elif file_type.lower() == "wikipedia":
        usual_path = os.path.join("data", "processed")
    else:
        print("Non existing file type")
        return None

    if os.path.isfile(os.path.join(usual_path, file_handle)):
        df = pand.read_csv(os.path.join(usual_path, file_handle))
        return df
    else:
        print("Non existing file handle, run the script again")

df = retrieve_data(file_handle, file_type)

def trim_world(data_frame):
    data_frame = data_frame[data_frame["Rank"] < 5]
    data_frame = data_frame.drop(columns = ["Points"])
    data_frame["Weight Class"] = data_frame["Weight Class"].str.strip("FS") + " kg"
    return data_frame

def wikipedia_trim(data_file):
    csv_data = data_file
    # 1. ISO 3-Letter Country Map
    country_map = {
        "UnitedStates": "USA", "Japan": "JPN", "India": "IND", "Kazakhstan": "KAZ",
        "ROC": "ROC", "Azerbaijan": "AZE", "Iran": "IRI", "Belarus": "BLR",
        "Uzbekistan": "UZB", "SanMarino": "SMR", "Cuba": "CUB", "Italy": "ITA",
        "Georgia": "GEO", "Turkey": "TUR"
    }

    def split_athlete_and_country(raw_string):
        """
        Splits 'Zaur UguevROC' -> 'Zaur Uguev', 'ROC'
        Uses regex to split right before the trailing block of uppercase letters (or mixed name casing).
        """
        if not raw_string:
            return "", ""
    
        # Regex logic: Find the boundary where a lowercase letter meets an uppercase letter
        # capturing the country suffix group.
        match = re.search(r'([a-z])([A-Z][a-zA-Z]*)$', raw_string)
        if match:
            # Split index is at the start of the country match
            split_idx = match.start(2)
            athlete = raw_string[:split_idx].strip()
            country_raw = raw_string[split_idx:].strip()
        else:
            # Fallback if text format varies unexpectedly
            athlete = raw_string
            country_raw = ""
        
        # Convert country string to ISO format using our dictionary fallback
        country_iso = country_map.get(country_raw, country_raw)
        return athlete, country_iso

    # 2. Initialize Boilerplate Accumulator
    data_accumulator = []

    # Tracker dictionary to remember what medals we've processed per weight class
    processed_events = {}

    # 3. Process the CSV file data on the fly
    # (Simulated reading using your exact text block string payload)
    """csv_data = Event,Gold,Silver,Bronze
    57 kgdetails,Zaur UguevROC,Ravi KumarIndia,Nurislam SanayevKazakhstan
    57 kgdetails,Zaur UguevROC,Ravi KumarIndia,Thomas GilmanUnited States
    65 kgdetails,Takuto OtoguroJapan,Haji AliyevAzerbaijan,Gadzhimurad RashidovROC
    65 kgdetails,Takuto OtoguroJapan,Haji AliyevAzerbaijan,Bajrang PuniaIndia
    74 kgdetails,Zaurbek SidakovROC,Mahamedkhabib KadzimahamedauBelarus,Kyle DakeUnited States
    74 kgdetails,Zaurbek SidakovROC,Mahamedkhabib KadzimahamedauBelarus,Bekzod AbdurakhmonovUzbekistan
    86 kgdetails,David TaylorUnited States,Hassan YazdaniIran,Artur NaifonovROC
    86 kgdetails,David TaylorUnited States,Hassan YazdaniIran,Myles AmineSan Marino
    97 kgdetails,Abdulrashid SadulaevROC,Kyle SnyderUnited States,Reineris SalasCuba
    97 kgdetails,Abdulrashid SadulaevROC,Kyle SnyderUnited States,Abraham ConyedoItaly
    125 kgdetails,Gable StevesonUnited States,Geno PetriashviliGeorgia,Amir Hossein ZareIran
    125 kgdetails,Gable StevesonUnited States,Geno PetriashviliGeorgia,Taha AkgülTurkey"""


    # Reading raw layout line-by-line progressively
    lines = csv_data.strip().split('\n')
    csv_reader = csv.DictReader(lines)

    for row in csv_reader:
        # Clean the weight class string: '57 kgdetails' -> '57 kg'
        weight_class = row['Event'].replace("details", "").strip()
    
        # Check if we have already encountered this weight group before
        if weight_class not in processed_events:
            # First encounter: Extract Gold (Rank 1), Silver (Rank 2), and 1st Bronze (Rank 3)
            processed_events[weight_class] = True
        
            # Parse names and countries
            gold_name, gold_geo = split_athlete_and_country(row['Gold'])
            silver_name, silver_geo = split_athlete_and_country(row['Silver'])
            bronze1_name, bronze1_geo = split_athlete_and_country(row['Bronze'])
        
            # Append Rank 1, 2, 3 entries immediately to our structural accumulator
            data_accumulator.append({"Weight Class": weight_class, "Rank": 1, "Athlete": gold_name, "Country": gold_geo})
            data_accumulator.append({"Weight Class": weight_class, "Rank": 2, "Athlete": silver_name, "Country": silver_geo})
            data_accumulator.append({"Weight Class": weight_class, "Rank": 3, "Athlete": bronze1_name, "Country": bronze1_geo})
        else:
            # Second encounter: Skip Gold/Silver duplicates, extract only 2nd Bronze (Rank 4)
            bronze2_name, bronze2_geo = split_athlete_and_country(row['Bronze'])
            data_accumulator.append({"Weight Class": weight_class, "Rank": 4, "Athlete": bronze2_name, "Country": bronze2_geo})

    # 4. Generate data frame from boilerplate structural rules all at once
    final_columns = ["Weight Class", "Rank", "Athlete", "Country"]
    final_df = pand.DataFrame(data_accumulator, columns=final_columns)

    # Display complete structured outcome sorted nicely
    final_df = final_df.sort_values(by=["Weight Class", "Rank"]).reset_index(drop=True)
    print(final_df)
    return data_file

if file_type.lower() == "uww":
    df = trim_world(df)
elif file_type.lower() == "wikipedia":
    df = wikipedia_trim(df)

print(df)