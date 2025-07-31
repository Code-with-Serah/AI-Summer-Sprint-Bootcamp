import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(filepath):
    return pd.read_csv(filepath)

def drop_irrelevant_features(df):
    columns_to_drop = [
        'Neo Reference ID', 'Name', 'Orbit ID', 'Orbit Determination Date',
        'Epoch Osculation', 'Equinox', 'Epoch Date Close Approach', 'Close Approach Date',
        'Est Dia in M(min)', 'Est Dia in M(max)',
        'Est Dia in Miles(min)', 'Est Dia in Miles(max)',
        'Est Dia in Feet(min)', 'Est Dia in Feet(max)',
        'Relative Velocity km per hr', 'Miles per hour',
        'Miss Dist.(Astronomical)', 'Miss Dist.(lunar)', 'Miss Dist.(miles)'
    ]
    df.drop(columns=columns_to_drop, inplace=True, errors='ignore')
    return df

def print_missing_values(df):
    print("\nMissing values per column:")
    missing = df.isnull().sum()
    print(missing[missing > 0] if not missing[missing > 0].empty else "No missing values found.")

def handle_missing_values(df):
    print_missing_values(df)

    # Fill numerical missing values with median
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())

    # Drop categorical columns with more than 50% missing values
    threshold = 0.5 * len(df)
    df.dropna(thresh=threshold, axis=1, inplace=True)

    # Fill remaining categorical missing values with mode
    cat_cols = df.select_dtypes(include='object').columns
    for col in cat_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    return df

def remove_duplicates(df):
    return df.drop_duplicates()

def convert_data_types(df):
    df['Hazardous'] = df['Hazardous'].astype(int)
    return df

def create_features(df):
    # Average diameter in KM
    df['Avg_Diameter_KM'] = (df['Est Dia in KM(min)'] + df['Est Dia in KM(max)']) / 2
    df.drop(['Est Dia in KM(min)', 'Est Dia in KM(max)'], axis=1, inplace=True)

    # Drop 'Orbiting Body' if it has only one unique value
    if 'Orbiting Body' in df.columns and df['Orbiting Body'].nunique() == 1:
        df.drop(columns=['Orbiting Body'], inplace=True)

    return df

def drop_highly_correlated_features(df, threshold=0.9):
    corr_matrix = df.drop(columns=['Hazardous']).corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = [col for col in upper.columns if any(upper[col] > threshold)]
    df.drop(columns=to_drop, inplace=True)
    return df

def standardize_features(df):
    features = df.select_dtypes(include=['float64', 'int64']).drop(columns=['Hazardous']).columns
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[features])
    df_scaled = pd.DataFrame(scaled_data, columns=features)
    df_scaled['Hazardous'] = df['Hazardous'].values
    return df_scaled

def check_class_balance(df):
    print("\nClass distribution:")
    print(df['Hazardous'].value_counts(normalize=True))
    sns.countplot(x='Hazardous', data=df)
    plt.title("Class Distribution (Hazardous vs Non-Hazardous)")
    plt.show()

def main():
    # Load and preprocess data step by step
    df = load_data("nasa.csv")
    df = drop_irrelevant_features(df)
    df = handle_missing_values(df)  # Now prints missing values before fixing
    df = remove_duplicates(df)
    df = convert_data_types(df)
    df = create_features(df)
    df = drop_highly_correlated_features(df)
    df_scaled = standardize_features(df)
    check_class_balance(df_scaled)

    # Save cleaned data
    df_scaled.to_csv("cleaned_nasa_data1.csv", index=False)

    print("\nFinal features used:")
    print(list(df_scaled.columns))

if __name__ == "__main__":
    main()
