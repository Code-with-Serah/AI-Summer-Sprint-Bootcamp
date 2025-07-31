import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Read your cleaned data
df = pd.read_csv('cleaned_nasa_data1.csv')

# Check Hazardous Distribution
print(df['Hazardous'].value_counts())

vars_set1 = ['Absolute Magnitude', 'Avg_Diameter_KM', 'Relative Velocity km per sec', 'Miss Dist.(kilometers)']
vars_set2 = ['Orbit Uncertainity',
    'Minimum Orbit Intersection',
    'Jupiter Tisserand Invariant',
    'Eccentricity',]
vars_set3=['Inclination',
    'Asc Node Longitude',
    'Perihelion Distance',
    'Perihelion Arg',]
vars_set4=['Perihelion Time',
    'Mean Anomaly',
    'Hazardous_numeric']

sns.pairplot(df, hue='Hazardous', vars=vars_set1, height=3, aspect=1)
plt.show()

sns.pairplot(df, hue='Hazardous', vars=vars_set2, height=3, aspect=1)
plt.show()

sns.pairplot(df, hue='Hazardous', vars=vars_set3, height=3, aspect=1)
plt.show()

sns.pairplot(df, hue='Hazardous', vars=vars_set4, height=3, aspect=1)
plt.show()
