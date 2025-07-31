from flask import Flask, render_template, request
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# ===== Enhanced Recipe Dataset =====
recipes = pd.DataFrame({
    'name': [
        'Chicken Salad', 'Vegan Bowl', 'Beef Stir Fry', 'Tofu Curry',
        'Avocado Toast', 'Turkey Wrap', 'Quinoa Salad', 'Big Breakfast',
        'Pasta Feast', 'Steak Dinner', 'Egg White Omelette', 'Lentil Soup',
        'Zucchini Noodles', 'Grilled Chicken', 'Stuffed Peppers'
    ],
    'diet': [
        'keto', 'vegan', 'low-carb', 'vegan',
        'vegetarian', 'low-carb', 'vegetarian', 'keto',
        'low-carb', 'low-carb', 'keto', 'vegan',
        'low-carb', 'keto', 'low-carb'
    ],
    'calories': [
        400, 350, 500, 370, 300, 420, 
        330, 1200, 1100, 1300, 250, 280, 
        340, 380, 390
    ],
    'protein': [
        35, 15, 40, 18, 10, 32, 
        12, 45, 30, 50, 20, 14, 
        25, 36, 34
    ],
    'gluten_free': [
        True, True, False, True, False, False,
        True, False, False, True, True, True,
        True, True, True
    ],
    'ingredients': [
        'chicken, lettuce, tomato, olive oil',
        'tofu, quinoa, avocado, spinach',
        'beef, broccoli, soy sauce, garlic',
        'tofu, coconut milk, curry powder',
        'avocado, whole wheat bread, eggs',
        'turkey, tortilla, lettuce, mayo',
        'quinoa, cucumber, feta, olive oil',
        'eggs, bacon, sausage, cheese, avocado',
        'pasta, cream sauce, mushrooms, parmesan',
        'steak, potatoes, butter, asparagus',
        'egg whites, spinach, mushrooms, cheese',
        'lentils, carrots, onions, spices',
        'zucchini, tomato sauce, basil, cheese',
        'chicken, olive oil, herbs, lemon',
        'bell peppers, rice, ground beef, onions'
    ],
    'rating': [
        4.5, 4.2, 4.7, 4.0, 3.9, 4.1,
        4.3, 4.6, 4.4, 4.9, 4.1, 4.2,
        4.3, 4.5, 4.2
    ]
})

# ===== Recommendation Engine =====
def recommend_meals(diet, max_calories, min_protein, gluten_free):
    try:
        # Initial filtering
        filtered = recipes[
            (recipes['diet'] == diet) &
            (recipes['protein'] >= min_protein * 0.7) &  # 70% of requested protein
            (recipes['gluten_free'] == gluten_free)
        ].copy()
        
        if len(filtered) == 0:
            # Fallback: Show closest matches
            filtered = recipes[
                (recipes['diet'] == diet) &
                (recipes['gluten_free'] == gluten_free)
            ].nlargest(3, 'protein')
        
        # Calculate similarity
        features = filtered['ingredients'] + ' ' + filtered['diet']
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform(features)
        
        user_query = f"{diet} {min_protein}g protein {max_calories} calories"
        user_vector = vectorizer.transform([user_query])
        
        filtered['similarity'] = cosine_similarity(user_vector, vectors)[0]
        filtered['calorie_diff'] = abs(filtered['calories'] - max_calories)
        
        return filtered.sort_values(
            ['similarity', 'calorie_diff', 'rating'],
            ascending=[False, True, False]
        ).head(3).to_dict('records')
    
    except Exception as e:
        print(f"Recommendation error: {str(e)}")
        return []

# ===== Flask Routes =====
@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    form_data = {
        'diet': '',
        'calories': 500,
        'protein': 20,
        'gluten_free': False
    }
    
    if request.method == 'POST':
        try:
            form_data['diet'] = request.form.get('diet', '')
            form_data['calories'] = int(request.form.get('calories', 500))
            form_data['protein'] = int(request.form.get('protein', 20))
            form_data['gluten_free'] = request.form.get('gluten_free') == 'on'
            
            recommendations = recommend_meals(
                form_data['diet'],
                form_data['calories'],
                form_data['protein'],
                form_data['gluten_free']
            )
        except Exception as e:
            print(f"Form processing error: {str(e)}")
    
    return render_template('index.html',
                         meals=recommendations,
                         form_data=form_data,
                         diets=sorted(recipes['diet'].unique()))

if __name__ == '__main__':
    app.run(debug=True)