# bot.py
import os
import logging
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# load env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # numeric, ex: -100123...
GROUP_ID = os.getenv("GROUP_ID")
WEBAPP_URL = os.getenv("WEBAPP_URL")
JOIN_CHANNEL_LINK = os.getenv("JOIN_CHANNEL_LINK")  # optional invite link
JOIN_GROUP_LINK = os.getenv("JOIN_GROUP_LINK")      # optional invite link

logging.basicConfig(
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# utility to check membership
async def is_member(bot, chat_id, user_id):
    try:
        mem = await bot.get_chat_member(chat_id=int(chat_id), user_id=user_id)
        # statuses where user is effectively joined
        return mem.status in ("member", "creator", "administrator")
    except Exception as e:
        logger.warning("membership check failed: %s", e)
        return False

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        "✅ স্বাগতম!\n\n"
        "অ্যাক্সেস পেতে নিচের নির্দেশগুলো অনুসরণ করুন:\n"
        "1) Channel এবং Group-এ Join করুন\n"
        "2) তারপর Check চাপুন — সব ঠিক থাকলে অ্যাক্সেস (Open App) পাবেন।\n\n"
        "নোট: Channel/Group প্রাইভেট হলে Join করার জন্য link ব্যবহার করুন (নিচে)।"
    )

    buttons = []
    # Join channel link if provided
    if JOIN_CHANNEL_LINK:
        buttons.append([InlineKeyboardButton("Join Channel", url=JOIN_CHANNEL_LINK)])
    else:
        buttons.append([InlineKeyboardButton("Join Channel (Open Channel)", url=f"https://t.me/{CHANNEL_ID.replace('-100','')}")])

    if JOIN_GROUP_LINK:
        buttons.append([InlineKeyboardButton("Join Group", url=JOIN_GROUP_LINK)])
    else:
        buttons.append([InlineKeyboardButton("Join Group (Open Group)", url=f"https://t.me/{GROUP_ID.replace('-100','')}")])

    # Check button (callback)
    buttons.append([InlineKeyboardButton("✅ Check (Join verify)", callback_data="check_join")])
    # Menu/help
    buttons.append([InlineKeyboardButton("ℹ️ Help", callback_data="help")])

    await update.effective_chat.send_message(text=text, reply_markup=InlineKeyboardMarkup(buttons))


# callback handler
async def button_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # acknowledge
    data = query.data

    user = query.from_user
    uid = user.id

    if data == "help":
        await query.message.reply_text(
            "Help — আপনার Telegram অ্যাকাউন্টে channel & group join করা থাকলে Check চাপুন।\n"
            "Access granted হলে Open App বাটন পাবেন।"
        )
        return

    if data == "check_join":
        msg = await query.message.reply_text("⏳ যাচাই করা হচ্ছে — অনুগ্রহ করে অপেক্ষা করুন...")
        # check channel and group membership
        ch_ok = await is_member(context.bot, CHANNEL_ID, uid)
        gp_ok = await is_member(context.bot, GROUP_ID, uid)

        if ch_ok and gp_ok:
            # Access granted — send web_app button
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("Open App (Open in Telegram)", web_app=WebAppInfo(WEBAPP_URL))],
                [InlineKeyboardButton("Open in browser", url=WEBAPP_URL)]
            ])
            await msg.edit_text("✅ Access Granted — নিচের বাটনে ক্লিক করে অ্যাপ খুলুন।", reply_markup=kb)
        else:
            missing = []
            if not ch_ok:
                missing.append("Channel")
            if not gp_ok:
                missing.append("Group")
            await msg.edit_text(f"❌ আপনি এই জিনিসগুলো Join করেননি: {', '.join(missing)}\n\n"
                                "অনুগ্রহ করে Join করে আবার Check চাপুন।")
        return


# optional /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("Check Join", callback_data="check_join")],
        [InlineKeyboardButton("Open App (browser)", url=WEBAPP_URL)]
    ]
    await update.message.reply_text("Menu:", reply_markup=InlineKeyboardMarkup(buttons))


def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set in .env")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_cb))

    logger.info("Bot starting (polling)...")
    app.run_polling()


if __name__ == "__main__":
    main()