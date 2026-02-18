import pandas as pd
import re
import os

def saving_data(df, file_name):
    output_folder = os.path.join("data", "processed")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")

    output_filename = file_name
    save_path = os.path.join(output_folder, output_filename)

    df.to_csv(save_path, index=False, encoding="utf-8")

    print("-" * 30)
    print(f"SUCCESS: Data saved to {save_path}")
    print("-" * 30)

    return save_path

def split_name(text):
    """
    Identifies the boundary between a lowercase name and an uppercase country
    and inserts a space. Example: 'Take IwamotoJapan' -> 'Take Iwamoto Japan'
    """
    if pd.isna(text):
        return text

    return re.sub(r'([a-z])([A-Z])', r'\1 \2', str(text))

def remove_details(text):
    if pd.isna(text):
        return text
    return text.replace("details", "").strip()

target_keywords = ["Gold", "Silver", "Bronze"]
    
path_folder = os.path.join("data", "raw")
file_name = input("Enter the name of the file you want to read: ")

if not file_name.lower().endswith(".csv"):
    file_name += ".csv"

full_path = os.path.join(path_folder, file_name)

if os.path.exists(full_path):
    df = pd.read_csv(full_path)
    print("File loaded successfully!")
    print(df.head())
    for col in df.columns:
        if any(key.lower() in col.lower() for key in target_keywords):
            df[col] = df[col].apply(split_name)
            df[col] = df[col].str.strip()
    if "Event" in df.columns:
        df["Event"] = df["Event"].apply(remove_details)
else:
    print(f"Error: The file {full_path} was not found.")

print(df)

file_name = input("If willing to save the file enter the file name, if you don't, please, press the enter key  ")
if file_name:
    if not file_name.lower().endswith(".csv"):
        file_name += ".csv"
    saving_data(df, file_name)
