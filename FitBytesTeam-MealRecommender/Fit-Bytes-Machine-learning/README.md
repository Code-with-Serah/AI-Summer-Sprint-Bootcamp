# FitMeal AI 🍽️🤖

An AI-powered meal recommender that helps users find suitable meals based on their dietary preferences, calorie needs, and protein intake.

## 🚀 What it does

- Takes user input: calories, protein, diet type (e.g., Keto, Vegan, etc.)
- Uses **Scikit-learn** with `OneHotEncoder` and `NearestNeighbors` to suggest the closest meals from the dataset.
- Helps people quickly find meals that match their nutrition goals.

## 🧠 Tech Stack

- **Python**
- **Flask** (for the web interface)
- **Scikit-learn** (AI logic: Nearest Neighbor Algorithm)
- **HTML + Bootstrap** (Frontend)

## 📊 Example Inputs

- Calories: 500
- Protein: 20
- Diet Type: Low Carb

## 🔍 How it works

1. User enters their meal preferences in the web interface.
2. The system encodes input features and compares them to a meal dataset.
3. It finds the most similar meals using a nearest-neighbor algorithm.
4. Shows matching results in a clean, responsive layout.

## 📦 How to run

```bash
pip install -r requirements.txt
python Meal-prep.py
Then open your browser and go to:  
http://127.0.0.1:5000

## 📁 Dataset

A custom meal dataset including calories, protein, diet types, and gluten-free labels.

## 🎯 Goal
 
To provide users with smart, personalized meal suggestions using simple AI — no training or deep learning required.

## 🏷️ Tags

AI, Nutrition, Health, Flask, Machine Learning, Recommendation System

## 👤 Made by

Fatima Alsayone 
Alaa Abdalla 
Fatima Dbouk
sara Dbouk
-2025 Bootcamp Project 
