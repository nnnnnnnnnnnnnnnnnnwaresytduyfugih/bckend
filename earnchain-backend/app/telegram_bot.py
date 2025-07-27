import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
WEB_APP_URL = os.environ.get('WEB_APP_URL', 'https://earnchain-python.onrender.com')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔗 Start Earning Now", web_app={"url": WEB_APP_URL})]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        '🌟 Welcome to Earn Chain! 🌟\n\nClick ads to earn rewards and build your crypto fortune!',
        reply_markup=reply_markup
    )

def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Earn Chain Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    run_bot()