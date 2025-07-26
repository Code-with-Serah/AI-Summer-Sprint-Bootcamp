🎬 Movie Recommendation System
A content-based movie recommendation system that suggests movies by analyzing genre similarity and score. Built by a 6-member team over 4 days using Python, Pandas, Scikit-learn, and Flask. The project includes data cleaning, exploratory data analysis (EDA), a recommendation engine, and a simple web interface.

🧠 Project Overview
Goal: Recommend movies based on genre similarity and score using a clean and visualized dataset.

Dataset: tmdb_5000_movies.csv or similar from Kaggle Datasets.

Tools Used: Python, Pandas, Matplotlib, Seaborn, Scikit-learn, Flask, Jupyter Notebook

👥 Team Members and Responsibilities

📊 Lara Damaj– Data Collection & Cleaning
Sourced movie data from IMDb/Kaggle

Performed data cleaning: removed duplicates, handled missing values, standardized columns

Delivered clean .csv file for analysis and modeling

🛠 Skills Used: pandas, CSV handling

📈 Hasan Al Soheil – Exploratory Data Analysis (EDA)
Explored genre distribution, average scores, runtime, and release year trends

Created insightful visualizations using Seaborn and Matplotlib

Shared insights with the ML team to guide feature selection

🛠 Skills Used: pandas, matplotlib, seaborn, groupby, value_counts, Jupyter


🧠 Habib Harb/Hasan Al Soheil – Machine Learning / Recommendation System
Built a content-based recommender using genre similarity

Used CountVectorizer to vectorize genres, cosine_similarity to compute movie distances

Wrote get_recommendations(movie_name) to return top-scoring similar movies

🛠 Skills Used: sklearn, cosine_similarity, CountVectorizer, numpy, pandas


🌐 Nader Zalzaly/Hasan Noureddine– Web Interface (Flask)
Created a Movies app with Movies Recommendation System

Integrated recommendation function into the Frontend

Displayed results dynamically

🛠 Skills Used: Flask, ReactJS.

Since the model size is more than 400 mb, i couldn't upload it to GitHub, so i uploaded it to Google Drive here's the link:
https://drive.google.com/file/d/1mx7Uvb7MnpAO4RWkxcDiePwzJhBazUeo/view?usp=sharing