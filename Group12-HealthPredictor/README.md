Why This Project?
Since our health is one of the most valuable blessings that God has given us, we shouldn’t neglect it. Many people live only on the surface ignoring what's happening inside. But in reality, every system in our body could be slowly getting exhausted, sending silent signals for help.
Life requires a healthy body and a healthy mind. We cannot fulfill our responsibilities if we are always tired, addicted to screens, unaware of what our bodies need, or disconnected from our health.
________________________________________
What is the Solution?
For the sake of our bodies, our minds, and our purpose in this life, we built a simple and easy-to-use web application.
This app offers everyone the chance to show mercy to their body and start making real lifestyle changes now. It’s not complicated or hard to use—just enter your daily lifestyle habits, and the app will do the rest. Based on our research and data, it predicts your Health Score using supervised machine learning regression models.
Our goal is to give every person a clear, science-based way to measure and improve their well-being.
________________________________________
How We Did It?
1. Working with the Data
•	First, we searched for a dataset that matches our goal: predicting health status based on lifestyle.
•	Then, we explored the dataset by:
 	Inspecting the data and types
 	Checking for missing values
 	Detecting and handling outliers
 	Encoding categorical values (even if they were numbers) so they follow machine learning rules
•	After that, we selected the features: defining our target (Health Score) and independent variables (like sleep, diet, etc.).
•	Finally, we applied feature scaling (standardization) to bring all features to the same scale.
2. Descriptive Analysis
•	We performed a detailed analysis of the data and visualized the relationships between features and Health Score.
•	We found that Diet Quality had the strongest positive relationship with Health Score both increased together.
•	We visualized this using scatter plots to better understand the impact.
________________________________________
Machine Learning Models
We applied several regression models to predict Health Score:
1️. Simple Linear Regression
•	Focused on Diet Quality as the only feature.
•	Visualized the regression line.
•	R² score was about 0.5, meaning it explained around 50% of the variation in health scores.
2️. Multiple Linear Regression
•	Used all lifestyle features together and our target is the heath score
•	Evaluated using:
o	R² Score
o	Mean Squared Error (MSE)
o	Mean Absolute Error (MAE)
3️. Ridge Regression & Random Forest Regression
1.	Ridge Regression:

A type of linear regression that adds a penalty to the model for having large coefficients. This helps reduce overfitting and improves predictions when features are highly correlated by adding regularization, with doing the same as what we do in linear regression from calculating errors and R² Score with sampling prediction to visualize our work.
2.	Random Forest Regression:
Same we proceed for Random Forest model, an ensemble learning method that builds multiple decision trees and combines their results. It improves accuracy, handles complex data well, and reduces the risk of overfitting
•	Random Forest performed the best:
o	Lowest errors
o	Highest R² score about 0.83 which is very good ensuring that the models fits the data about 83%.
o	Most accurate and stable predictions
________________________________________
Final Conclusion
After testing all models, we found that Random Forest Regression gave the best results for predicting Health Score. It offered accurate predictions, handled different kinds of data well, and had the least error. And this shown by the bar charts we have do to compare the errors that are provided by the three multiple regression model and there coefficient of determinations.                                   

**Live Demo**: [Click here to try the app](https://healthcare-prediction-ebqnw9qsw3xlhiur2ahvcf.streamlit.app/)
