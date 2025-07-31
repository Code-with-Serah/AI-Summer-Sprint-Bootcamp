#Import necessary libraries
import pandas as pd
import numpy as np
import pickle
import warnings
import os
warnings.filterwarnings('ignore')

# Machine Learning Libraries
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
import xgboost as xgb

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Flask for API
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json

# SHAP for interpretability
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("SHAP not available. Install with: pip install shap")

# 1. DATA LOADING AND PREPROCESSING
class LoanApprovalModel:
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.scaler = None
        self.feature_columns = None
        self.target_names = {0: 'Rejected', 1: 'Approved'}
        
    def load_and_preprocess_data(self, filepath):
        """Load and preprocess the loan data"""
        print("🔄 Loading and preprocessing data...")
        
        # Load data
        df = pd.read_csv(r"C:\Users\MY-PC\OneDrive - Sagesse University\Desktop\Bootcamp_Project\cleaned1_loan_data.csv")
        print(f" Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Feature Engineering
        df['debt_to_income'] = df['loan_amnt'] / df['person_income']
        df['credit_to_income'] = df['credit_score'] / df['person_income'] * 100000  # Normalize
        df['experience_to_age'] = df['person_emp_exp'] / df['person_age']
        df['loan_affordability'] = df['person_income'] / df['loan_amnt']
        
        # Categorical encoding
        categorical_columns = ['person_gender', 'person_education', 'person_home_ownership', 
                            'loan_intent', 'previous_loan_defaults_on_file']
        
        for col in categorical_columns:
            le = LabelEncoder()
            df[col + '_encoded'] = le.fit_transform(df[col])
            self.label_encoders[col] = le
        
        # Select features for model
        feature_columns = [
            'person_age', 'person_income', 'person_emp_exp', 'loan_amnt',
            'loan_int_rate', 'loan_percent_income', 'cb_person_cred_hist_length',
            'credit_score', 'debt_to_income', 'credit_to_income', 
            'experience_to_age', 'loan_affordability'
        ] + [col + '_encoded' for col in categorical_columns]
        
        self.feature_columns = feature_columns
        
        X = df[feature_columns]
        y = df['loan_status']
        
        print(f"✅ Features prepared: {len(feature_columns)} features")
        print(f"✅ Target distribution: {y.value_counts().to_dict()}")
        
        return X, y, df
    
    def train_model(self, X, y):
    #Train XGBoost model with class weighting and an adjusted prediction threshold.
        print("\n🔄 Training XGBoost with a 2-step approach: Weighting + Thresholding...")

    # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

    # --- STEP 1: USE CLASS WEIGHTING (scale_pos_weight) ---
    # This is still a best practice. It tells the model to pay more attention
    # to the minority class ('Approved') during training.
        ratio = float(np.count_nonzero(y_train == 0)) / np.count_nonzero(y_train == 1)
        print(f"⚖️ Step 1: Using class weight (scale_pos_weight): {ratio:.2f}")

        self.model = xgb.XGBClassifier(
            objective='binary:logistic',
            eval_metric='auc',
            scale_pos_weight=ratio,  # Keep this parameter
            max_depth=6,
            learning_rate=0.1,
            n_estimators=200,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )

    # Train the model
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            callbacks=[xgb.callback.EarlyStopping(rounds=20, save_best=True)],
            verbose=False
        )
        print("✅ Model trained successfully.")

    # --- STEP 2: ADJUST THE PREDICTION THRESHOLD ---
    # The default threshold is 0.5. We will lower it to increase Recall for 'Approved'.
    # This is a critical step for imbalanced problems.

    # Get the predicted probabilities for the 'Approved' class (class 1)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]

    # Set a new, lower threshold. You can experiment with this value (e.g., 0.4, 0.35).
        new_threshold = 0.4
        print(f"🔧 Step 2: Adjusting prediction threshold from 0.5 to {new_threshold}")

    # Apply the new threshold to get the final predictions
        y_pred = (y_pred_proba >= new_threshold).astype(int)

    # EVALUATE WITH THE NEW, ADJUSTED PREDICTIONS 
        print("\nMODEL PERFORMANCE METRICS (with adjusted threshold):")
        print("="*50)
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        print(f"Precision: {precision_score(y_test, y_pred):.4f}")
        print(f"Recall: {recall_score(y_test, y_pred):.4f}")
        print(f"F1-Score: {f1_score(y_test, y_pred):.4f}")
        # ROC-AUC is calculated on probabilities, so it's unaffected by the threshold
        print(f"ROC-AUC: {roc_auc_score(y_test, y_pred_proba):.4f}")

        print("\nCLASSIFICATION REPORT (with adjusted threshold):")
        print(classification_report(y_test, y_pred, target_names=['Rejected', 'Approved']))

        print("\nCONFUSION MATRIX (with adjusted threshold):")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)

        # Add the new plot for your presentation
        self.plot_precision_recall_curve(y_test, y_pred_proba)
        self.plot_feature_importance()

        return X_train, X_test, y_train, y_test
    
    
    def plot_feature_importance(self):
        """Plot feature importance"""
        if self.model is None:
            return
        
        feature_importance = self.model.feature_importances_
        feature_names = self.feature_columns
        
        # Create DataFrame for plotting
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': feature_importance
        }).sort_values('importance', ascending=False)
        
        plt.figure(figsize=(10, 8))
        sns.barplot(data=importance_df.head(15), x='importance', y='feature')
        plt.title('Top 15 Feature Importance - XGBoost Model')
        plt.xlabel('Importance Score')
        plt.tight_layout()
        plt.show()
        
        print("\n🎯 TOP 10 MOST IMPORTANT FEATURES:")
        for idx, (feature, importance) in enumerate(importance_df.head(10).values):
            print(f"{idx+1:2d}. {feature:30s}: {importance:.4f}")
    
    def predict_single(self, input_data):
        """Make prediction for a single loan application with an adjusted threshold."""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Convert input to DataFrame
        df_input = pd.DataFrame([input_data])
        
        # Feature engineering (same as training)
        df_input['debt_to_income'] = df_input['loan_amnt'] / df_input['person_income']
        df_input['credit_to_income'] = df_input['credit_score'] / df_input['person_income'] * 100000
        df_input['experience_to_age'] = df_input['person_emp_exp'] / df_input['person_age']
        df_input['loan_affordability'] = df_input['person_income'] / df_input['loan_amnt']
        
        # Encode categorical variables
        categorical_mapping = {
            'person_gender': {'male': 0, 'female': 1},
            'person_education': {'High School': 0, 'Associate': 1, 'Bachelor': 2, 'Master': 3, 'Doctorate': 4},
            'person_home_ownership': {'RENT': 0, 'OWN': 1, 'MORTGAGE': 2, 'OTHER': 3},
            'loan_intent': {'PERSONAL': 0, 'EDUCATION': 1, 'MEDICAL': 2, 'VENTURE': 3, 'HOMEIMPROVEMENT': 4, 'DEBTCONSOLIDATION': 5},
            'previous_loan_defaults_on_file': {'No': 0, 'Yes': 1}
        }
        
        for col, mapping in categorical_mapping.items():
            if col in df_input.columns:
                df_input[col + '_encoded'] = df_input[col].map(mapping)
        
        # Select features
        X_input = df_input[self.feature_columns]
        
        # --- KEY CHANGE IS HERE ---
        # Instead of using model.predict(), we get the probabilities and apply our own threshold.
        
        # 1. Get the probability of the loan being 'Approved' (class 1)
        probability_approved = self.model.predict_proba(X_input)[0][1]
        
        # 2. Set a custom threshold (you can tune this value)
        new_threshold = 0.4 
        
        # 3. Make the final prediction based on the new threshold
        prediction = 1 if probability_approved >= new_threshold else 0
        # --- END OF CHANGE ---

        probability = self.model.predict_proba(X_input)[0]
        
        return {
            'prediction': int(prediction),
            'prediction_label': self.target_names[prediction],
            'probability_rejected': float(probability[0]),
            'probability_approved': float(probability[1]),
            'confidence': float(max(probability))
        }
    
    def save_model(self, filepath):
        """Save the trained model and encoders"""
        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'target_names': self.target_names
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load a trained model and encoders"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.label_encoders = model_data['label_encoders']
        self.feature_columns = model_data['feature_columns']
        self.target_names = model_data['target_names']
        print(f"✅ Model loaded from {filepath}")


# 2. FLASK API 
# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Global model instance
loan_model = LoanApprovalModel()

@app.route('/')
def home():
    """Serve the loan application form from external HTML file"""
    try:
        # Try to serve from static folder first
        return send_from_directory('static', 'loan_form.html')
    except:
        try:
            # Fallback: look for template in templates folder
            return render_template('loan_form.html')
        except:
            # Last resort: return a simple message
            return """
            <h1>Loan Approval System</h1>
            <p>Please create a 'static/loan_form.html' or 'templates/loan_form.html' file.</p>
            <p>API is available at:</p>
            <ul>
                <li>POST /predict - Make loan predictions</li>
                <li>GET /health - Check system health</li>
            </ul>
            """

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for loan prediction"""
    try:
        # Get JSON data from request
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = [
            'person_age', 'person_gender', 'person_income', 'person_emp_exp',
            'person_education', 'person_home_ownership', 'loan_amnt', 'loan_intent',
            'loan_int_rate', 'loan_percent_income', 'credit_score',
            'cb_person_cred_hist_length', 'previous_loan_defaults_on_file'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
        
        # Make prediction
        result = loan_model.predict_single(data)
        
        return jsonify(result)
    
    except Exception as e:
        import traceback
        print(f"Prediction error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'model_loaded': loan_model.model is not None,
        'xgboost_version': xgb.__version__
    })

# 3. MAIN EXECUTION

def main():
    """Main function to train model and start Flask app"""
    print("LOAN APPROVAL SYSTEM - XGBoost + Flask")
    print("="*60)
    print(f"XGBoost version: {xgb.__version__}")
    
    # File paths - UPDATE THESE TO YOUR ACTUAL PATHS
    DATA_PATH = r"C:\Users\MY-PC\OneDrive - Sagesse University\Desktop\Bootcamp_Project\cleaned1_loan_data.csv"
    MODEL_PATH = "loan_approval_xgboost_model.pkl"
    
    try:
        # Check if model already exists
        try:
            print("\nChecking for existing model...")
            loan_model.load_model(MODEL_PATH)
            print("Existing model loaded successfully!")
        except FileNotFoundError:
            print("\n1️⃣ TRAINING NEW MODEL")
            print("-" * 30)
            
            # Check if data file exists
            if not os.path.exists(DATA_PATH):
                print(f"Data file not found: {DATA_PATH}")
                print(f"Current directory: {os.getcwd()}")
                print("Please update the DATA_PATH variable with the correct file path.")
                return
            
            # Load and preprocess data
            X, y, df = loan_model.load_and_preprocess_data(DATA_PATH)
            
            # Train model
            X_train, X_test, y_train, y_test = loan_model.train_model(X, y)
            
            # Save model
            loan_model.save_model(MODEL_PATH)
            
            # Test prediction
            print("\n🧪 TESTING SINGLE PREDICTION:")
            test_data = {
                'person_age': 30,
                'person_gender': 'male',
                'person_income': 75000,
                'person_emp_exp': 5,
                'person_education': 'Bachelor',
                'person_home_ownership': 'MORTGAGE',
                'loan_amnt': 15000,
                'loan_intent': 'EDUCATION',
                'loan_int_rate': 8.5,
                'loan_percent_income': 0.2,
                'credit_score': 720,
                'cb_person_cred_hist_length': 8,
                'previous_loan_defaults_on_file': 'No'
            }
            
            prediction = loan_model.predict_single(test_data)
            print(f"Test prediction: {prediction}")
        
    except Exception as e:
        print(f"Error during model preparation: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
        print("📁 Created 'static' directory for HTML files")
    
    # Start Flask app
    print("\n🌐 STARTING FLASK WEB SERVER")
    print("-" * 30)
    print("🔗 Open your browser and go to: http://127.0.0.1:5000")
    print("📊 API Health Check: http://127.0.0.1:5000/health")
    print("🔮 API Predict Endpoint: http://127.0.0.1:5000/predict (POST)")
    print("\n⚡ Ready to accept loan applications!")
    print("\n📝 Note: Make sure to place 'loan_form.html' in the 'static' folder")
    
    # Run Flask app
    try:
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")

if __name__ == "__main__":
    main()