# Serah – Smart AI Assistant with Gmail, Calendar & Telegram Automation

**Serah** is an intelligent AI assistant built using **n8n** that automates and streamlines your Gmail, Google Calendar, Google Sheets, and Telegram workflows. It listens to voice or text commands via Telegram and performs tasks such as sending emails, managing events, retrieving contact details, labeling or replying to emails, and more — all with context-aware AI using OpenAI.

---

## Features

### Conversational AI Assistant (`Serah`)
- Powered by OpenAI (`GPT`) for understanding, reasoning, and responding.
- Stores chat memory per Telegram user with **Window Buffer Memory**.
- Responds to voice or text messages intelligently.
- Fluent in **Lebanese Arabic and English**.

### Gmail Automation
- **Send Emails** based on user prompts.
- **Reply to Emails** with context-aware responses.
- **Create Drafts** for later review.
- **Label Emails** using existing or newly created labels.
- **Get Emails** using filters like sender, date, and search query.
- **Delete Emails** by Message ID.
- **Fetch Labels** from the Gmail account.

### Google Calendar Management
- Fetches calendar events by date or range.
- Prevents scheduling conflicts.
- Can notify users 30 minutes before meetings via email.

### Google Sheets Integration
- Retrieves rows from a specific sheet for contact or task-related data.
- Dynamically queries contact details like email, name, or phone number.

### Voice Recognition & Commands
- Supports **audio messages on Telegram**.
- Automatically downloads and transcribes voice input using **OpenAI Whisper**.
- Routes to appropriate logic block via `Switch`.

### AI Logic & Personalization
- Custom system prompt defining detailed assistant behavior.
- Dynamically pulls data from Google Calendar, Gmail, and Google Sheets.
- Responds like a smart personal assistant with memory and reasoning.

---

## Architecture Overview

This n8n workflow includes:

- **Telegram Trigger** → Detects incoming messages.
- **Switch Node** → Distinguishes between audio, text, and errors.
- **Voice Input Path**:
  - Telegram voice → File download → Whisper transcription → OpenAI Chat → Response.
- **Text Input Path**:
  - Direct to OpenAI Chat for handling.
- **AI Agent Node (`Serah`)**:
  - Executes logic (send email, create draft, query calendar, etc.).
- **Window Memory Node**:
  - Maintains consistent conversation per user.
- **Google Calendar/Gmail/Sheets Nodes**:
  - Handles automation triggered by the AI.
- **Telegram Message Response**:
  - Sends back summarized or requested response to user.

---

## Getting Started

### 1. **Requirements**
- n8n (Cloud or Self-hosted)
- Active accounts:
  - Gmail with OAuth2 credentials
  - Google Sheets API
  - Google Calendar API
  - Telegram Bot Token
  - OpenAI API Key (for GPT + Whisper)

### 2. **Environment Setup**
- Clone this workflow into your n8n instance.
- Create and configure OAuth2 credentials for:
  - Gmail
  - Google Calendar
  - Google Sheets
- Add Telegram API credentials and connect your bot.
- Add OpenAI credentials.

### 3. **Usage**
- Send a message to the Telegram bot:
  - **Voice or Text** asking for: 
    - "Send an email to Sarah about the meeting tomorrow at 5"
    - "Show me today’s meetings"
    - "Reply to the last email from Jad"
- The bot processes your request via GPT and automates the relevant action using Google APIs.

---

## AI System Prompt Behavior

The prompt instructs Serah to:
- Act like an intelligent personal assistant.
- Use Google Calendar and Sheets for contact info.
- Manage email actions smartly (reply, label, send, etc.).
- Always assume today if a date is not provided.
- Sign off emails with:

Regards,
n8nNovators


---

## Technical Highlights

| Module           | Role                                                                 |
|------------------|----------------------------------------------------------------------|
| **Telegram Bot** | Frontend interface (text/audio)                                      |
| **Whisper**      | Transcribes voice messages                                           |
| **GPT (OpenAI)** | Main AI logic + context handling                                     |
| **Google APIs**  | Calendar, Gmail, Sheets integration                                  |
| **Window Memory**| Session-based memory per Telegram user                               |
| **n8n Switch**   | Audio/Text/Error detection                                           |

---

## Example Commands

-  “Send an email to Dr. Ahmad about the syllabus.”
- “Label all emails from Jad as IMPORTANT.”
- “What meetings do I have today?”
- “Draft an email to my team about the upcoming demo.”
- Send a voice message saying: “Remind me to email Rami about the internship.”

---

## Author

**Fatima Hijazi**  
Contact: `fatimaahijazii23@gmail.com`  
GitHub: [fatimahijazi23](https://github.com/fatimahijazi23)

