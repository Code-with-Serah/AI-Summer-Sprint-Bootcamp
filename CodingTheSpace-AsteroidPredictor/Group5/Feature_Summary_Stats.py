import pandas as pd

# Load dataset from a CSV file
def load_data(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)

# Generate summary statistics (mean, median, min, max, std) for selected features
def summarize_features(df: pd.DataFrame, features: list) -> pd.DataFrame:
    summary = (
        df[features]
        .describe()
        .loc[['mean', '50%', 'min', 'max', 'std']]
        .rename(index={'50%': 'median'})
        .round(2)
    )
    return summary

def main():
    filepath = "Cleaned_Without_Standardization_Dataset.csv"
    key_features = ['Miss Dist.(kilometers)', 'Avg_Diameter_KM', 'Relative Velocity km per sec']
    df = load_data(filepath)
    summary_stats = summarize_features(df, key_features)
    print("\nSummary Statistics of Key Features:\n")
    print(summary_stats)

if __name__ == "__main__":
    main()
