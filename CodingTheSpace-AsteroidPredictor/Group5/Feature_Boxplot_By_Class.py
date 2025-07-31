import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the dataset
def load_data(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)

# Plot boxplots for specified features 
def plot_boxplots(df: pd.DataFrame, features: list, target_col: str = 'Hazardous') -> None:
    sns.set(style="whitegrid")
    for feature in features:
        plt.figure(figsize=(8, 5))
        sns.boxplot(x=target_col, y=feature, data=df, palette='Set2')
        plt.title(f'Box Plot of {feature} by {target_col} Status')
        plt.xlabel(f'{target_col} (0 = No, 1 = Yes)')
        plt.ylabel(feature)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

def main():
    filepath = "cleaned_nasa_data1.csv"
    df = load_data(filepath)
    features_to_plot = [
        'Absolute Magnitude',
        'Relative Velocity km per sec',
        'Miss Dist.(kilometers)',
        'Avg_Diameter_KM',
        'Minimum Orbit Intersection',
        'Eccentricity',
        'Inclination'
    ]
    plot_boxplots(df, features_to_plot)

if __name__ == "__main__":
    main()
