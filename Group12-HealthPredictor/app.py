import streamlit as st
import numpy as np
import joblib

# Load the trained model
model = joblib.load("health_model.pkl")

# Mapping for Smoking_Status
smoking_map = {
    "Never smoked": 0,
    "Occasional smoker": 1,
    "Daily smoker": 2
}

def health_score_category(score):
    if score < 0:
        return "🚨 Really Bad — Please consult a healthcare professional immediately."
    elif 0 <= score < 25:
        return "⚠️ Low — There’s room for improvement in your health."
    elif 25 <= score < 50:
        return "🙂 Good — You’re doing fairly well!"
    elif 50 <= score < 75:
        return "😊 Very Good — Keep up the great habits!"
    else:
        return "🏆 Excellent — Outstanding health status!"

# App title and description
st.title("🏥 Health Score Predictor")
st.write("""
Enter your health details below and get an estimated health score along with advice.
""")

# User inputs with better UI and helpful tooltips
age = st.number_input("Age", min_value=0, max_value=120, value=30, help="Your age in years")
bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, value=22.0, step=0.1, help="Body Mass Index (weight/height²)")
exercise = st.slider("Exercise Frequency (days/week)", 0, 7, 3, help="How many days per week you exercise")
diet_quality = st.slider("Diet Quality (1 = Poor, 10 = Excellent)", 1, 10, 5, help="Rate your diet quality")
sleep_hours = st.slider("Average Sleep Hours per Night", 0.0, 12.0, 7.0, step=0.5, help="How many hours you sleep on average")
alcohol = st.slider("Alcohol Consumption (units/week)", 0, 30, 2, help="Average units of alcohol consumed per week")
smoking_status = st.selectbox("Smoking Status", options=list(smoking_map.keys()), help="Select your smoking habit")

if st.button("Calculate Health Score"):
    try:
        smoking_encoded = smoking_map[smoking_status]
        features = np.array([[age, bmi, exercise, diet_quality, sleep_hours, alcohol, smoking_encoded]])
        
        predicted_score = model.predict(features)[0]
        category = health_score_category(predicted_score)
        
        st.success(f"✨ Your Predicted Health Score: {predicted_score:.2f}")
        st.info(f"🔍 Health Category: {category}")

        # Extra friendly advice based on category
        if predicted_score < 0:
            st.warning("Please consider seeing a healthcare professional as soon as possible.")
        elif predicted_score < 25:
            st.warning("Try to improve your lifestyle by focusing on diet, exercise, and sleep.")
        elif predicted_score < 50:
            st.info("You're on a decent track, but there’s still room to improve!")
        elif predicted_score < 75:
            st.success("Great job maintaining a healthy lifestyle!")
        else:
            st.balloons()
            st.success("Excellent health! Keep it up! 🎉")

    except Exception as e:
        st.error(f"Oops, something went wrong: {e}")
