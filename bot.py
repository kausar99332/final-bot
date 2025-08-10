import os
import telebot
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GROUP_ID = os.getenv("GROUP_ID")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    first_name = message.from_user.first_name
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton("📱 Open App", web_app=telebot.types.WebAppInfo(WEBAPP_URL))
    markup.add(btn1)
    bot.send_message(chat_id, f"👋 হ্যালো {first_name}!\nআপনার অ্যাপ ওপেন করতে নিচের বাটনে ক্লিক করুন।", reply_markup=markup)

# Webhook route for Render
@server.route("/" + BOT_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBAPP_URL}/{BOT_TOKEN}")
    return "Webhook set!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))