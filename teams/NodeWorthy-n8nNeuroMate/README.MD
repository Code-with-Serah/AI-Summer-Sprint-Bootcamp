# Team NodeWorthy - NeuroMate

This is a smart reminder bot built with **n8n**, integrated with **Telegram**, **Google Sheets**, and **AI** for natural language understanding.

## 📌 What It Does

- Accepts reminder messages via **Telegram**.
- Uses **AI** to understand tasks and reminder times (even with natural language like "remind me to pray at 5").
- Confirms the reminder with the user.
- Saves reminder info to **Google Sheets**.
- Sends the reminder message back at the right time.
- Has a **daily check** feature for upcoming Google Calendar events.

## 🧠 Tech Used

- **n8n**
- **Telegram Bot**
- **Mistral AI (LangChain Node)**
- **Google Sheets**
- **Google Calendar**
- **Custom Code Nodes**

## 🧩 Main Workflow Structure

1. **Telegram Trigger** – Starts when user sends a message.
2. **Date & Time** – Gets the current date and time.
3. **Mistral AI** – Parses the message into task + reminder time.
4. **Code Node** – Formats and confirms the reminder.
5. **Telegram Message** – Sends confirmation to user.
6. **Google Sheets** – Saves the task data.
7. **Wait Node** – Pauses until reminder time.
8. **Final Telegram Message** – Sends actual reminder.
9. **(Optional)** Daily check for calendar events and notifies user.

## ✨ Example

**User says:**  
`remind me to review my notes at 7pm`

**Bot responds:**  

Hi! ✅
I've set your reminder:

📝 Task: review my notes
⏰ Time: July 26, 19:00

## 🤝 Team

- Team NodeWorthy – AI Summer Sprint Bootcamp