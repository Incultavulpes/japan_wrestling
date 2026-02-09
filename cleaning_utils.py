import pandas as pd
import re
import os

path_folder = os.path.join("data", "raw")
file_name = input("Enter the name of the file you want to read: ")

if not file_name.lower().endswith(".csv"):
    file_name += ".csv"

full_path = os.path.join(path_folder, file_name)

if os.path.exists(full_path):
    df = pd.read_csv(full_path)
    print("File loaded successfully!")
    print(df.head())
else:
    print(f"Error: The file {full_path} was not found.")

def split_name(text):
    """
    Identifies the boundary between a lowercase name and an uppercase country
    and inserts a space. Example: 'Take IwamotoJapan' -> 'Take Iwamoto Japan'
    """
    if pd.isna(text):
        return text

    return re.sub(r'([a-z])([A-Z])', r'\1 \2', str(text))

