
from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# ===== ENHANCED DATASET =====
recipes = pd.DataFrame({
    'name': [
        'Chicken Salad', 'Keto Beef Bowl', 'Cheesy Bacon Omelette', 'Avocado Egg Bake',
        'Grilled Salmon', 'Keto Fat Bombs', 'Steak with Butter', 'Keto Pizza',
        'Bulletproof Coffee', 'Bacon-Wrapped Chicken', 'Keto Mac & Cheese'
    ],
    'diet': ['keto', 'keto', 'keto', 'keto', 'keto', 'keto', 'keto', 'keto', 'keto', 'keto', 'keto'],
    'calories': [420, 850, 700, 600, 550, 300, 1200, 900, 450, 800, 950],
    'protein': [36, 55, 42, 38, 48, 5, 65, 40, 2, 60, 35],
    'gluten_free': [True, True, True, True, True, True, True, False, True, True, False],
    'ingredients': [
        'chicken, greens, avocado, olive oil',
        'beef, cauliflower rice, cheese, avocado',
        'eggs, cheddar cheese, bacon, butter',
        'eggs, avocado, cheese, heavy cream',
        'salmon, butter, lemon, asparagus',
        'coconut oil, cocoa powder, peanut butter',
        'ribeye steak, butter, garlic, rosemary',
        'almond flour, cheese, pepperoni, eggs',
        'coffee, butter, MCT oil',
        'chicken thighs, bacon, cream cheese',
        'cauliflower, heavy cream, cheddar, bacon'
    ],
    'rating': [4.5, 4.8, 4.6, 4.3, 4.7, 4.1, 4.9, 4.4, 3.9, 4.6, 4.5]
})

# ===== IMPROVED RECOMMENDATION LOGIC =====
def recommend_meals(diet, target_calories, min_protein, gluten_free):
    """Enhanced recommendation with calorie-proportionate matching"""
    try:
        # 1. Filter by diet and gluten preference
        filtered = recipes[
            (recipes['diet'] == diet) &
            (recipes['gluten_free'] == gluten_free)
        ].copy()
        
        # 2. Calculate calorie-protein score (higher is better)
        filtered['score'] = (
            (filtered['protein'] * 0.6) +  # Protein importance (60%)
            (np.minimum(filtered['calories'], target_calories) * 0.4)  # Calorie match (40%)
        )
        
        # 3. Filter by minimum protein requirement
        filtered = filtered[filtered['protein'] >= min_protein]
        
        if len(filtered) == 0:
            # Fallback: Show highest protein options
            return recipes[
                (recipes['diet'] == diet) &
                (recipes['gluten_free'] == gluten_free)
            ].nlargest(3, 'protein').to_dict('records')
        
        # 4. Prioritize meals closest to target calories
        filtered['calorie_diff'] = abs(filtered['calories'] - target_calories)
        
        return (filtered
                .sort_values(['score', 'calorie_diff', 'rating'], 
                           ascending=[False, True, False])
                .head(3)
                .to_dict('records'))
    
    except Exception as e:
        print(f"Recommendation error: {str(e)}")
        return []

# ===== FLASK ROUTES =====
@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    if request.method == 'POST':
        try:
            diet = request.form.get('diet', 'keto')
            calories = int(request.form.get('calories', 1000))
            protein = int(request.form.get('protein', 30))
            gluten_free = request.form.get('gluten_free', 'off') == 'on'
            
            recommendations = recommend_meals(diet, calories, protein, gluten_free)
            print(f"Recommended: {recommendations}")  # Debug output
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    return render_template('index.html', 
                         meals=recommendations,
                         diets=sorted(recipes['diet'].unique()))

if __name__ == '__main__':
    app.run(debug=True)