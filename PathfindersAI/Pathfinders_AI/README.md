# Pathfinders AI – Student Guidance Chatbot

## 🚀 Overview
Pathfinders AI is a web-based student assistant that uses Google's Gemini Pro API (a Large Language Model) to provide smart academic and career guidance through a chatbot interface. It helps students get personalized support on study tips, career paths, and subject-related questions.

## 🧠 Project Theme
This project falls under the **LLM-based AI assistance** category. It does **not use traditional machine learning** but instead integrates a pre-trained large language model (Gemini) via API.

## 🛠️ Technologies Used
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **AI Model**: Gemini Pro API (Google)
- **Deployment**: Flask local server

## 🎯 Features
- User Signup & Login
- Chatbot powered by Gemini API (StudyBuddy)
- Session tracking (number of chats)
- Subject coverage tracking
- Dashboard (activity display and weekly stats)
- Prompt-engineered personality and behavior

## 🤖 Prompt Engineering
Prompt engineering is handled in `static/js/chat.js`, using the `initialSystemInstruction`. It tells Gemini:
- To act as “StudyBuddy,” a helpful academic assistant
- To stay on-topic (academic/career guidance)
- To use plain, conversational language

```js
const initialSystemInstruction = {
  role: "user",
  parts: [{
    text: "You are StudyBuddy, an AI academic guidance assistant..."
  }]
};
```

## 🧩 Project Structure
```
Pathfinders_AI/
├── app.py
├── index.html, login.html, chat.html, ...
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── README.md  ← (this file)
```

## 🔐 Notes
- The API key is hardcoded in `chat.js` for demo purposes. In production, it should be stored securely.
- The chatbot is limited to educational topics and avoids off-topic questions by design.

## 👤 Team Members and Roles
- **Mariam Wehbi** – Frontend development
- **Hussein Haydar** – UI/UX design
- **Yaseen Hakim** – Backend and Gemini API integration
- **Carl Abu Harb** – Testing and QA
- **Hassan El Miari** – Documentation and presentation

## 📌 How to Run
```bash
cd Pathfinders_AI
pip install flask
python app.py
```
Then visit `http://127.0.0.1:5000/` in your browser.
