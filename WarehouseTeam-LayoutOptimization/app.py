from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import numpy as np
import joblib
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # Add this after initializing the app

# Load model and encoder
model = load_model("warehouse_model.h5")
rack_encoder = joblib.load("rack_encoder.pkl")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        pallet_type = data.get("pallet_type")
        quantity = float(data.get("quantity", 0))          # 🔁 Force to float
        demand_score = float(data.get("demand_score", 0))  # 🔁 Force to float

        # Convert pallet type to number
        pallet_id = {"Small": 1, "Medium": 2, "Large": 3}.get(pallet_type, 0)
        pallet_id = float(pallet_id)  # 🔁 Also cast pallet_id to float

        # Create input as float32
        input_features = np.array([[pallet_id, quantity, demand_score]], dtype=np.float32)

        prediction = model.predict(input_features)
        pred_index = np.argmax(prediction)
        recommended_cell = rack_encoder.classes_[pred_index]

        return jsonify({"recommended_cell": recommended_cell})

    except Exception as e:
        print("🔥 ERROR:", e)
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(debug=True)
