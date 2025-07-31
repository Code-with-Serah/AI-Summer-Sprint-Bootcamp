from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import asyncio
from dotenv import load_dotenv
import os

# If you have the token, create .env file and write inside it TELEGRAM_BOT_TOKEN={the token}
# create .gitignore file and write inside it: .env

load_dotenv()  # loads the hidden bot token from .env file

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # read token
CATEGORIES = ["news", "sports", "economy", "politics", "technology","health", "opinion", "human rights", "palestine", "israel", "gaza", "war", "conflict"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the News4LazyDudes Bot!\n\n"
        "Commands:\n"
        "🔍 /search [keywords]: Search for specific keywords\n"
        "❓/help"
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /search [keywords]\nExample: /search barcelona vs real madrid")
        return

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search))


print("Bot is running...")
app.run_polling()