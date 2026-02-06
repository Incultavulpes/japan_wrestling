import pandas

path_file = os.path.join("data", "raw")
file_name = input("Enter the name of the file you want to read ")
path_file = os.path.join(path_file, file_name)
csv_file = pandas.read_csv(path_file)