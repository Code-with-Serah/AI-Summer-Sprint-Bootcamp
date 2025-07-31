import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Read your cleaned data
df = pd.read_csv('cleaned_nasa_data1.csv')

# Check Hazardous Distribution
print(df['Hazardous'].value_counts())

# Convert 'Hazardous' to binary numeric for correlation (if not already 0/1)
df['Hazardous_numeric'] = df['Hazardous'].apply(lambda x: 1 if x == 1 else 0)

# Select numeric columns including the newly mapped ones
numeric_cols = [
    'Absolute Magnitude',
    'Avg_Diameter_KM',
    'Relative Velocity km per sec',
    'Miss Dist.(kilometers)',
    'Orbit Uncertainity',
    'Minimum Orbit Intersection',
    'Jupiter Tisserand Invariant',
    'Eccentricity',
    'Inclination',
    'Asc Node Longitude',
    'Perihelion Distance',
    'Perihelion Arg',
    'Perihelion Time',
    'Mean Anomaly',
    'Hazardous_numeric'
]

# Drop NA values for numeric analysis
df_clean = df[numeric_cols].dropna()

# Correlation Matrix
corr = df_clean.corr()

plt.figure(figsize=(14, 12))
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Matrix Including Hazardous')
plt.show()
