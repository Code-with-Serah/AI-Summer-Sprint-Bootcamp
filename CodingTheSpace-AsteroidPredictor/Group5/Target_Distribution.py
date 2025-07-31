import pandas as pd

# Load the dataset from CSV file
def load_data(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)

# Compute count and percentage distribution of classes in the target column
def compute_class_distribution(df: pd.DataFrame, target_col: str = 'Hazardous') -> pd.DataFrame:
    class_counts = df[target_col].value_counts()
    class_percentages = df[target_col].value_counts(normalize=True) * 100
    class_labels = {0: 'Non-Hazardous (0)', 1: 'Hazardous (1)'}
    distribution_df = pd.DataFrame({
        'Class': [class_labels[i] for i in class_counts.index],
        'Count': class_counts.values,
        'Percentage': class_percentages.round(1).values
    })
    return distribution_df

def main():
    filepath = "cleaned_nasa_data1.csv"
    df = load_data(filepath)
    class_distribution = compute_class_distribution(df)
    print(class_distribution)

if __name__ == "__main__":
    main()
