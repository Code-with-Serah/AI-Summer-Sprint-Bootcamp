# News4LazyDudes Telegram Bot

A Telegram bot that fetches and summarizes news from Al Jazeera based on keywords or categories.

---

## Features

- `/start` — Welcome message and basic usage instructions.
- `/search [keywords]` — Search news articles by keywords and get a summarized result.
- `/categories` — Show a list of predefined news categories as buttons.
- Category buttons — When clicked, fetch and summarize news related to the selected category.
- Summarization and translation placeholders (to be replaced with real scraping/LLM and translation logic).
- Bot token securely loaded from a `.env` file.

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/news4lazydudes-bot.git
cd news4lazydudes-bot
```

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** If you don’t have a `requirements.txt`, install these manually:

```bash
pip install python-telegram-bot python-dotenv
```

### 4. Create a `.env` file in the project root

Add your Telegram bot token inside `.env` like this:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

**Important:** Make sure `.env` is included in `.gitignore` so your token is never pushed publicly.

> **Note:** If you don’t have a `.gitignore` file, create it manually and write inside:
```
.env
```

---

## Running the Bot

```bash
python BotController.py
```

You should see:

```
Bot is running...
```

Your bot will start polling Telegram for updates.

---

## Bot Usage

- Send `/start` to get welcome instructions.
- Send `/search your keywords` to search and get summarized news.
- Send `/categories` to see buttons of categories and tags.
- Click on a category button to get summarized news for that category.

---

## Notes

- The current summarization and translation functions are placeholders. *MUST BE IMPLEMENTED*
- The bot loads the token securely from `.env` using `python-dotenv`.
- Inline keyboards provide interactive category selection.
