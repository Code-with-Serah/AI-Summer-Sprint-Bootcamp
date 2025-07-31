from flask import Flask, request, jsonify
import joblib
import pandas as pd
from flask_cors import CORS
from validation import (
    validate_required_columns,
    validate_numeric_columns,
    validate_missing_values,
    validate_row_count,
    remove_duplicates,
)
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the model once when the backend starts
try:
    model = joblib.load("final_rf_model.joblib")
    print("✅ Model loaded successfully from final_rf_model.joblib")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    raise

def validate_input_data(csv_string):
    """
    Uses the imported validation functions to validate and clean the CSV data string.
    Returns a cleaned DataFrame ready for prediction.
    """
    # Define required columns and their default mean values
    required_columns = [
        'Minimum Orbit Intersection',
        'Absolute Magnitude',
        'Avg_Diameter_KM',
        'Perihelion Distance',
        'Orbit Uncertainity',
        'Inclination'
    ]

    default_means = {
        'Minimum Orbit Intersection': 0.4768977851980138,
        'Absolute Magnitude': 0.1591059336579516,
        'Avg_Diameter_KM': 0.13758845293463146,
        'Perihelion Distance': 0.0479985661169944,
        'Orbit Uncertainity': 0.04306290759519788,
        'Inclination': 0.04022213144882968
    }

    numeric_columns = required_columns

    # Load CSV from string
    df = pd.read_csv(io.StringIO(csv_string))
    df.columns = df.columns.str.strip()  # Normalize columns

    # Use imported validators
    df = validate_required_columns(df, required_columns, default_means)
    df = validate_missing_values(df, default_means)
    validate_numeric_columns(df, numeric_columns)
    validate_row_count(df)
    df = remove_duplicates(df)

    # Return only the required columns in the correct order
    final_columns = [col for col in required_columns if col in df.columns]
    return df[final_columns]

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Handle incoming request data
        if request.is_json:
            # If JSON, get 'processedData' list and convert to DataFrame
            data = request.json.get('processedData', [])
            df = pd.DataFrame(data)
        else:
            # If form-data with file or raw CSV text
            if 'file' in request.files:
                file = request.files['file']
                csv_string = file.read().decode('utf-8')
            else:
                csv_string = request.data.decode('utf-8')

            # Validate and clean CSV data
            df = validate_input_data(csv_string)

        required_features = [
            'Minimum Orbit Intersection',
            'Absolute Magnitude',
            'Avg_Diameter_KM',
            'Perihelion Distance',
            'Orbit Uncertainity',
            'Inclination'
        ]

        # Confirm all required features exist
        for feature in required_features:
            if feature not in df.columns:
                raise ValueError(f"Required feature '{feature}' missing after validation")

        # Predict with the loaded model
        predictions = model.predict(df[required_features]).tolist()

        # Respond with predictions and cleaned data
        return jsonify({
            'predictions': predictions,
            'data': df[required_features].to_dict('records')
        })

    except Exception as e:
        # Return error message and HTTP 400 for any issues
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
