import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import probplot

# Load the cleaned NASA dataset
def load_data(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)

# Generate Histogram + KDE and Q-Q Plot for each feature
def plot_normality(df: pd.DataFrame, features: list) -> None:
    sns.set(style="whitegrid")
    for feature in features:
        data = df[feature].dropna()
        plt.figure(figsize=(10, 4))
        plt.subplot(1, 2, 1)
        sns.histplot(data, kde=True, color='steelblue')
        plt.title(f"{feature} - Histogram & KDE")
        plt.xlabel(feature)
        plt.ylabel("Frequency")
        plt.subplot(1, 2, 2)
        probplot(data, dist="norm", plot=plt)
        plt.title(f"{feature} - Q-Q Plot")
        plt.tight_layout()
        plt.show()

def main():
    filepath = "cleaned_nasa_data1.csv"
    df = load_data(filepath)
    features_to_plot = [
        "Absolute Magnitude",
        "Relative Velocity km per sec",
        "Miss Dist.(kilometers)",
        "Avg_Diameter_KM",
        "Inclination",
        "Eccentricity"
    ]
    plot_normality(df, features_to_plot)

if __name__ == "__main__":
    main()
