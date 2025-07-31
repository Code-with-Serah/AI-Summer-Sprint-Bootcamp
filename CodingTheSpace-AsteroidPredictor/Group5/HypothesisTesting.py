import pandas as pd
from scipy import stats

# Load and prepare the data
df = pd.read_csv('cleaned_nasa_data1.csv')

# Ensure correct types
df['Hazardous'] = df['Hazardous'].astype(int)

# List of numeric features to test
features_to_test = [
    'Absolute Magnitude',
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
    'Avg_Diameter_KM'
]


# Store results
results = []

# Perform t-tests
for feature in features_to_test:
    # Drop rows with NaN for current feature
    subset = df[['Hazardous', feature]].dropna()
    group1 = subset[subset['Hazardous'] == 1][feature].astype(float)
    group0 = subset[subset['Hazardous'] == 0][feature].astype(float)
    
    # Check sample sizes
    if len(group1) < 10 or len(group0) < 10:
        results.append({
            'Feature': feature,
            'T-Statistic': None,
            'P-Value': None,
            'Conclusion': 'Too few samples'
        })
        continue
    
    # Perform Welch's t-test
    t_stat, p_val = stats.ttest_ind(group1, group0, equal_var=False)
    
    results.append({
        'Feature': feature,
        'T-Statistic': round(t_stat, 3),
        'P-Value': round(p_val, 4),
        'Conclusion': 'Significant' if p_val < 0.05 else 'Not Significant'
    })

# Convert to DataFrame
results_df = pd.DataFrame(results)

# Display results
print(results_df)


