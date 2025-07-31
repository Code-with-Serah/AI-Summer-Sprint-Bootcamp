import pandas as pd
import numpy as np  

df=pd.read_csv('cleaned_nasa_data1.csv')


for col in df.select_dtypes(include=[np.number]).columns:
    if col != 'Hazardous':
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        print(f"{col}: {len(outliers)} outliers")
