import pandas as pand
import os.path

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

def wikipedia_trim(data_frame):
    return data_frame

if file_type.lower() == "uww":
    df = trim_world(df)
elif file_type.lower() == "wikipedia":
    df = wikipedia_trim(df)

print(df)