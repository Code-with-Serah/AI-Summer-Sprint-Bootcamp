import pandas as pd
import numpy as np
from sklearn.feature_selection import f_classif

# Load dataset
def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df['Hazardous'] = df['Hazardous'].astype(int)
    return df

# Apply ANOVA F-test to all features against the 'Hazardous' target
def perform_anova(df: pd.DataFrame) -> pd.DataFrame:
    X = df.drop(columns=['Hazardous'])
    y = df['Hazardous']
    f_values, p_values = f_classif(X, y)
    results = pd.DataFrame({
        'Feature': X.columns,
        'F-Value': f_values,
        'P-Value': p_values,
        'Conclusion': np.where(p_values < 0.05, 'Significant', 'Not Significant')
    })
    results = results.sort_values(by='F-Value', ascending=False).reset_index(drop=True)
    return results

def main():
    filepath = "cleaned_nasa_data1.csv"
    df = load_data(filepath)
    anova_results = perform_anova(df)
    print(anova_results)

if __name__ == "__main__":
    main()
