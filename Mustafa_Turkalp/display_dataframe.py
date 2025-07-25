import pandas as pd

file_path = "./merged_dataset.csv"

df = pd.read_csv(file_path)
print(df.head(20))