import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# .env লোড করা
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
MONETAG_LINK = os.getenv("MONETAG_LINK")

# লগিং সেটআপ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ডাটাবেস কানেকশন ফাংশন
def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None

# স্টার্ট কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"হ্যালো! 👋\n\nএটি আপনার বট।\nআপনার অ্যাড লিঙ্ক: {MONETAG_LINK}"
    )

# ডাটাবেস টেস্ট কমান্ড
async def dbtest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db_connection()
    if conn:
        await update.message.reply_text("✅ ডাটাবেস কানেকশন সফল!")
        conn.close()
    else:
        await update.message.reply_text("❌ ডাটাবেস কানেকশন ব্যর্থ।")

# মেইন ফাংশন
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dbtest", dbtest))

    logging.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()