import pandas as pd
from scipy.stats import pointbiserialr

# Load dataset
def load_data(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)

#  Compute Point Biserial Correlation between binary target and continuous features
def compute_point_biserial(df: pd.DataFrame, target_col: str, features: list) -> pd.DataFrame:
    results = []
    for feature in features:
        coef, p_value = pointbiserialr(df[target_col], df[feature])
        results.append({
            'Feature': feature,
            'Correlation Coefficient': round(coef, 4),
            'P-Value': round(p_value, 4),
            'Conclusion': 'Significant' if p_value < 0.05 else 'Not Significant'
        })

    correlation_df = pd.DataFrame(results)
    correlation_df = correlation_df.sort_values(by='Correlation Coefficient', ascending=False).reset_index(drop=True)
    return correlation_df

def main():
    filepath = "cleaned_nasa_data1.csv"
    df = load_data(filepath)
    features_to_test = [
        'Absolute Magnitude',
        'Relative Velocity km per sec',
        'Miss Dist.(kilometers)',
        'Avg_Diameter_KM',
        'Minimum Orbit Intersection',
        'Eccentricity',
        'Inclination'
    ]
    correlation_df = compute_point_biserial(df, target_col='Hazardous', features=features_to_test)
    print(correlation_df)

if __name__ == "__main__":
    main()
