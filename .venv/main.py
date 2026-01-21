"""
AI Payroll Agent - Telegram Bot
Author: Patryk Adamski
Description: An AI-powered assistant that extracts work hours from images
             using Google Gemini and calculates monthly payroll.
"""

import os
import io
import logging
import sqlite3
import warnings
from typing import Final
import PIL.Image
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
import google.generativeai as genai

# Suppress unnecessary warnings
warnings.filterwarnings("ignore")

# --- CONFIGURATION ---
# In production, these should be loaded from environment variables
TOKEN: Final = "YOUR_TELEGRAM_TOKEN_HERE"
API_KEY: Final = "YOUR_GEMINI_API_KEY_HERE"
HOURLY_RATE: Final = 31.7

# Configure Gemini AI
genai.configure(api_key=API_KEY)


class PayrollBot:
    def __init__(self):
        self.db_path = "payroll_data.db"
        self._init_db()
        self.model = self._setup_model()

    def _init_db(self):
        """Initializes the SQLite database for storing hours."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS work_log "
                "(user_id INTEGER, date TEXT, hours REAL)"
            )

    def _setup_model(self):
        """Auto-detects and initializes the best available Gemini vision model."""
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if 'flash' in m.name:
                        return genai.GenerativeModel(m.name)
            return genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            logging.error(f"Model initialization failed: {e}")
            return None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message and command overview."""
        await update.message.reply_text(
            "🚀 **AI Payroll Agent Active**\n\n"
            "Commands:\n"
            "📸 Send a schedule photo to log hours\n"
            "➕ /add [n] - Manually add n hours\n"
            "📊 /summary - View monthly earnings\n"
            "🗑️ /reset - Clear all data",
            parse_mode="Markdown"
        )

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processes uploaded images to extract work hours via OCR/AI."""
        status = await update.message.reply_text("🔍 Analyzing schedule...")

        try:
            # Download image from Telegram
            photo = await update.message.photo[-1].get_file()
            photo_bytes = await photo.download_as_bytearray()
            img = PIL.Image.open(io.BytesIO(photo_bytes))

            # AI Prompt for specific data extraction
            prompt = (
                "Identify 'Patryk Adamski' in this schedule table. "
                "Calculate total work hours for this person. "
                "Format: SUM_HOURS: [number]. If not found, reply: NOT_FOUND."
            )

            response = self.model.generate_content([prompt, img])
            result = response.text.strip()

            if "SUM_HOURS:" in result:
                hours = float(result.split(":")[1].strip().replace(',', '.'))
                self._log_hours(update.effective_user.id, hours)
                total_value = hours * HOURLY_RATE
                await status.edit_text(f"✅ Logged {hours}h from image. Earnings: ${total_value:.2f}$")
            else:
                await status.edit_text(f"⚠️ Could not find hours for specified user.")
        except Exception as e:
            await status.edit_text(f"❌ Processing error: {str(e)}")

    def _log_hours(self, user_id: int, hours: float):
        """Saves hour entries to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO work_log VALUES (?, date('now'), ?)", (user_id, hours))

    async def get_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Calculates total hours and earnings from the database."""
        user_id = update.effective_user.id
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT SUM(hours) FROM work_log WHERE user_id = ?", (user_id,))
            total_hours = cursor.fetchone()[0] or 0.0

        total_pay = total_hours * HOURLY_RATE
        await update.message.reply_text(
            f"📊 **Monthly Summary**\n"
            f"Total Hours: {total_hours}h\n"
            f"Rate: {HOURLY_RATE} PLN/h\n"
            f"-------------------\n"
            f"**Total Payout: {total_pay:.2f} PLN**",
            parse_mode="Markdown"
        )


if __name__ == "__main__":
    bot = PayrollBot()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", bot.start_command))
    app.add_handler(CommandHandler("summary", bot.get_summary))
    app.add_handler(MessageHandler(filters.PHOTO, bot.handle_photo))

    print("Agent is running...")
    app.run_polling()