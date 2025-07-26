def recommend_movies(movie_name, top_n=10):
    movie_name = movie_name.lower()

    # Match the input movie (case-insensitive)
    matches = df[df['Name'].str.lower() == movie_name]
    if matches.empty:
        return f"❌ Movie '{movie_name}' not found in the dataset."

    # Get the genre of the input movie
    input_genre = matches.iloc[0]['Genre']

    # Find movies with the exact same genre (excluding the input movie)
    same_genre_movies = df[(df['Genre'] == input_genre) & (df['Name'].str.lower() != movie_name)]

    # If not enough recommendations are available
    if same_genre_movies.shape[0] < 1:
        return f"❌ Not enough movies in the same genre to make recommendations."

    # Sort by Score descending
    recommended = same_genre_movies.sort_values(by='Score', ascending=False).head(top_n)

    return recommended[['Name', 'Genre', 'Score']]