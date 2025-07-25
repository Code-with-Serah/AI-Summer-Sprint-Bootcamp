import pandas as pd
import os

# Define the folder where the CSVs are stored
folder_path = "./DataSets"

# List all CSV files in the folder
csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

# Load and concatenate all CSVs
df_list = [pd.read_csv(os.path.join(folder_path, file)) for file in csv_files]
merged_df = pd.concat(df_list, ignore_index=True)

# Save to a new file
merged_df.to_csv("merged_dataset.csv", index=False)