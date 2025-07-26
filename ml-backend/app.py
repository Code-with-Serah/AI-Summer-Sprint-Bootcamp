from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Load dataset and models
try:
    df = pd.read_csv("pickAi_movies.csv")
    with open("trained_tfidf.pkl", "rb") as f:
        tfidf = pickle.load(f)
    with open("trained_cosine_sim.pkl", "rb") as f:
        cosine_sim = pickle.load(f)
    print("Models loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")

# Recommendation function
def recommend_movies(movie_name, top_n=10):
    try:
        movie_name = movie_name.lower().strip()
        matches = df[df['Name'].str.lower() == movie_name]
        
        if matches.empty:
            return []
        
        input_genre = matches.iloc[0]['Genre']
        same_genre_movies = df[(df['Genre'] == input_genre) & (df['Name'].str.lower() != movie_name)]
        
        if same_genre_movies.shape[0] < 1:
            return []
        
        recommended = same_genre_movies.sort_values(by='Score', ascending=False).head(top_n)
        return recommended[['Name', 'Genre', 'Score']].to_dict(orient='records')
    except Exception as e:
        print(f"Error in recommend_movies: {e}")
        return []

# Flask route
@app.route("/recommend", methods=["GET"])
def recommend():
    try:
        movie_name = request.args.get("movie")
        if not movie_name:
            return jsonify({"error": "No movie name provided"}), 400
        
        results = recommend_movies(movie_name)
        
        if not results:
            return jsonify({"error": f"No recommendations found for '{movie_name}'. Please check the movie name."}), 404
        
        return jsonify(results)
    except Exception as e:
        print(f"Error in recommend route: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
