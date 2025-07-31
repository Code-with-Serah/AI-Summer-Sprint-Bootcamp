import pandas as pd

#make sure the file is .csv
def validate_file_type(filepath):
    if not str(filepath).endswith(".csv"):
        raise ValueError("Invalid file type. Please upload a CSV file.")

#make sure that it will load without errors
def load_csv(filepath):
    try:
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()  # normalize columns
        return df
    except Exception as e:
        raise ValueError(f"Failed to load CSV file: {e}")

def validate_required_columns(df, required_columns, default_means):
    missing_cols = [col for col in required_columns if col not in df.columns]

    if len(missing_cols) >= 3:
        raise ValueError(f"Too many required columns are missing: {missing_cols}")

    if 0 < len(missing_cols) <= 2:
        print(f"Missing columns detected: {missing_cols}")
        print("Filling missing columns with default mean values…")
        for col in missing_cols:
            df[col] = default_means.get(col, 0.0)  # fallback to 0.0 if no mean specified
    return df

def validate_numeric_columns(df, numeric_columns):
    for col in numeric_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column '{col}' must be numeric.")

def validate_missing_values(df, default_means):

    # Check per row
    rows_with_many_missing = df.isnull().sum(axis=1) > 2
    if rows_with_many_missing.any():
        raise ValueError("One or more rows have more than 2 missing values. File rejected.")

    # Fill per column
    missing_cols = df.columns[df.isnull().any()].tolist()
    if missing_cols:
        print(f"Columns with missing values: {missing_cols}")
        print("Filling missing values with default means.")
        for col in missing_cols:
            default = default_means.get(col)
            if default is not None:
                df[col] = df[col].fillna(default)
            else:
                raise ValueError(f"No default mean provided for column: {col}")

    return df

def validate_row_count(df):
    if len(df) == 0:
        raise ValueError("CSV file contains no rows.")

def remove_duplicates(df):
    return df.drop_duplicates()


def validate_input_data(filepath):

    validate_file_type(filepath)

    df = load_csv(filepath)

    # Define schema of required columns
    required_columns = [
        'Minimum Orbit Intersection',
        'Absolute Magnitude',
        'Avg_Diameter_KM',
        'Perihelion Distance',
        'Orbit Uncertainity',
        'Inclination'
    ]
    numeric_columns = required_columns

    allowed_orbits = ['Earth']  # update if needed

    default_means = {
    'Minimum Orbit Intersection': 0.4768977851980138,
    'Absolute Magnitude': 0.1591059336579516,
    'Avg_Diameter_KM': 0.13758845293463146,
    'Perihelion Distance': 0.0479985661169944,
    'Orbit Uncertainity': 0.04306290759519788,
    'Inclination': 0.04022213144882968
    }


    #  Run validations
    df = validate_required_columns(df, required_columns, default_means)
    validate_numeric_columns(df, numeric_columns)
    validate_missing_values(df, default_means)
    validate_row_count(df)

    #  Clean up
    df = remove_duplicates(df)

    final_columns = required_columns + (['Hazardous'] if 'Hazardous' in df.columns else [])
    df_ready = df[final_columns]

    print("Input data validated successfully.")
    return df_ready



if __name__ == "__main__":

    filepath = "nasa.csv"
    df_cleaned = validate_input_data(filepath)

    print("\n Cleaned data preview:")
    print(df_cleaned.head())
