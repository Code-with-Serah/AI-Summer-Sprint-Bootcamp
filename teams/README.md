# AI Summer Sprint Bootcamp - Team Projects

Welcome to the AI Summer Sprint Bootcamp repository! This repository contains projects from multiple teams participating in the bootcamp program.

## Repository Structure

This repository has been organized to clearly separate each team's work:

```
AI-Summer-Sprint-Bootcamp/
├── teams/
│   ├── OBFFS-BabyCryClassifier/      # Baby Cry Sound Classification System
│   ├── NateN-DreamInterpreter/       # Dream Interpretation AI with Arabic Support
│   ├── Group12-HealthPredictor/      # Health Score Prediction & Analysis
│   ├── N8Nnovators-N8n/              # Smart AI Assistant with Gmail & Telegram
│   ├── CodingTheSpace-AsteroidPredictor/ # Space Hazard Predictor for Asteroids
│   ├── FitBytesTeam-MealRecommender/ # AI-Powered Meal Recommender System
│   ├── WarehouseTeam-LayoutOptimization/ # Warehouse Layout Optimization with AI
│   ├── GroupLLMao-NewsAutomation/    # News4LazyDudes Telegram Bot
│   └── Group24-DataExploration/      # Calories Prediction System
└── README.md                         # This file
```

## Team Projects

### OBFFS - Baby Cry Classifier
**Location:** `teams/OBFFS-BabyCryClassifier/`
**Team:** Mohammad Fad & Team

A deep learning system that classifies baby crying sounds into different categories (hunger, discomfort, pain, tiredness, etc.). Uses multiple CNN architectures including YAMNet for audio classification.

**Key Features:**
- Multiple model architectures (CNN, ResNet, MobileNet, EfficientNet, YAMNet)
- Live inference demo with Flask API
- Best performance: 65% accuracy with YAMNet

### N ate N - Dream Interpreter
**Location:** `teams/NateN-DreamInterpreter/`
**Team:** N ate N (mosleima)

An AI-powered dream interpretation system that processes Arabic and English dream descriptions using classical dream interpretation books.

**Key Features:**
- Arabic/English dream text processing
- Integration with Google Gemini AI
- PDF processing of classical dream books
- Streamlit and Flask web interfaces

### Group 12 - Health Score Predictor  
**Location:** `teams/Group12-HealthPredictor/`
**Team:** Group 12 Health Analytics

A machine learning web application that predicts health scores based on lifestyle factors using Random Forest regression with 83% accuracy.

**Key Features:**
- Health score prediction based on lifestyle data
- Multiple regression models (Linear, Ridge, Random Forest)
- Interactive web interface with Streamlit
- Live demo available online

### N8Nnovators - N8n AI Assistant
**Location:** `teams/N8Nnovators-N8n/`
**Team:** N8Nnovators (Fatima Hijazi)

An intelligent AI assistant built with N8N that automates Gmail, Google Calendar, and Telegram workflows with voice and text commands.

**Key Features:**
- Voice recognition with OpenAI Whisper
- Gmail automation (send, reply, label, delete)
- Google Calendar integration
- Telegram bot interface
- Fluent in Lebanese Arabic and English

### Coding The Space - Asteroid Predictor
**Location:** `teams/CodingTheSpace-AsteroidPredictor/`
**Team:** Ali Kawar, Hanine Khalil, Aya Rayed, Samira Jawish, Jinan Rachid, Batoul Hamieh

A full-stack machine learning web application that predicts whether near-Earth objects (asteroids) are hazardous using NASA data.

**Key Features:**
- Random Forest classifier with 99% accuracy
- Flask REST API backend
- CSV file validation and preprocessing
- Real-time hazard prediction

### FitBytes Team - Meal Recommender
**Location:** `teams/FitBytesTeam-MealRecommender/`
**Team:** Fatima Alsayone, Alaa Abdalla, Fatima Dbouk, Sara Dbouk

An AI-powered meal recommender that helps users find suitable meals based on their dietary preferences, calorie needs, and protein intake.

**Key Features:**
- Nearest Neighbor Algorithm for meal matching
- Flask web interface with Bootstrap UI
- Custom meal dataset with nutrition information
- Support for various diet types (Keto, Vegan, Low Carb, etc.)

### Warehouse Team - Layout Optimization
**Location:** `teams/WarehouseTeam-LayoutOptimization/`
**Team:** Deep Learning Warehouse Team

A deep learning system that optimizes warehouse layout and predicts optimal storage locations for different pallet types using neural networks.

**Key Features:**
- TensorFlow/Keras neural network model
- Flask API for real-time predictions
- Pallet type and demand-based optimization
- Warehouse cell recommendation system

### Group LLMao - News Automation Bot
**Location:** `teams/GroupLLMao-NewsAutomation/`
**Team:** Group LLMao

A Telegram bot called News4LazyDudes that fetches and summarizes news from Al Jazeera based on keywords or categories, featuring automated workflows with N8N.

**Key Features:**
- Keyword-based news search functionality
- Predefined category buttons for easy navigation
- News summarization and translation capabilities
- Secure bot token management with environment variables
- N8N workflow automation integration
- Interactive inline keyboards for category selection

### Group 24 - Data Exploration & Calories Prediction
**Location:** `teams/Group24-DataExploration/`
**Team:** Group 24

A machine learning application that predicts calories burned during exercise based on personal and activity parameters using linear regression modeling.

**Key Features:**
- Streamlit web interface for user input
- Linear regression model for calorie prediction
- Normalized input processing for accurate predictions
- Interactive user interface with real-time predictions
- Support for gender, age, height, weight, duration, heart rate, and body temperature inputs

## Getting Started

Each team project has its own setup instructions. Navigate to the specific team directory and follow their README files for detailed setup instructions.

### General Prerequisites
- Python 3.8+
- Git
- Various Python packages (see individual team requirements)

## Contributing

This repository represents the collaborative work of multiple teams. Each team maintains their own project structure within their designated directory.

### Team Guidelines
1. Keep all team files within your designated `teams/[team-name]/` directory
2. Include a comprehensive README in your team directory
3. Document dependencies in a requirements.txt file
4. Follow proper git practices with meaningful commit messages

## Issues & Support

If you encounter issues with any specific project, please:
1. Check the team's individual README file
2. Ensure all dependencies are properly installed
3. Contact the respective team members for project-specific issues

## Bootcamp Information

This repository is part of the AI Summer Sprint Bootcamp program, showcasing various AI and machine learning projects developed by participating teams.

**Program Focus Areas:**
- Machine Learning & Deep Learning
- Natural Language Processing
- Computer Vision
- Data Analysis & Visualization
- Workflow Automation
- AI Application Development

## License

Each project may have its own licensing terms. Please refer to individual team directories for specific license information.

---

**Last Updated:** July 2025  
**Bootcamp:** AI Summer Sprint Bootcamp  
**Repository Maintainer:** Code-with-Serah
