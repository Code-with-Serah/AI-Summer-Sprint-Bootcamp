from scipy.stats import levene
import pandas as pd
import numpy as np
df = pd.read_csv('cleaned_nasa_data1.csv')

# Keep only numeric columns and exclude 'Hazardous'
features_to_test = df.select_dtypes(include='number').columns.tolist()
features_to_test = [f for f in features_to_test if f != 'Hazardous']

variance_results = []

for feature in features_to_test:
    subset = df[['Hazardous', feature]].dropna()
    group1 = subset[subset['Hazardous'] == 1][feature].astype(float)
    group0 = subset[subset['Hazardous'] == 0][feature].astype(float)

    if len(group1) < 10 or len(group0) < 10:
        variance_results.append({
            'Feature': feature,
            'Levene_Stat': None,
            'P-Value': None,
            'Conclusion': 'Too few samples'
        })
        continue

    stat, p_val = levene(group1, group0)
    variance_results.append({
        'Feature': feature,
        'Levene_Stat': round(stat, 3),
        'P-Value': round(p_val, 4),
        'Conclusion': 'Unequal Variance' if p_val < 0.05 else 'Equal Variance'
    })

# Display results
variance_df = pd.DataFrame(variance_results)
print(variance_df)
