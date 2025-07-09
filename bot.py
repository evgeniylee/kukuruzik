import os
import json
import random
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "kukuruzikuz")
ADMIN_ID = int(os.getenv("ADMIN_ID", "2071181"))

RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"

PORT = int(os.getenv("PORT", default=8000))

app = ApplicationBuilder().token(BOT_TOKEN).webhook_path(WEBHOOK_PATH).webhook_url(WEBHOOK_URL).build()


def load_data():
    os.makedirs("data", exist_ok=True)
    path = "data/users.json"
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path, "r") as f:
        return json.load(f)


def save_data(data):
    with open("data/users.json", "w") as f:
        json.dump(data, f, indent=2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {
            "name": None,
            "phone": None,
            "subscribed": False,
            "joined_at": datetime.now().isoformat()
        }
        save_data(data)

    await update.message.reply_text("👋 Добро пожаловать в акцию KUKURUZIK!\nПожалуйста, введите ваше имя:")


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id in data and data[user_id].get("name") is None:
        data[user_id]["name"] = update.message.text
        save_data(data)

        keyboard = [[KeyboardButton("📞 Отправить контакт", request_contact=True)]]
        await update.message.reply_text(
            "Отправьте ваш номер телефона:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    data[user_id]["phone"] = update.message.contact.phone_number
    save_data(data)

    keyboard = [[KeyboardButton("✅ Я подписался")]]
    await update.message.reply_text(
        f"Теперь подпишитесь на канал: https://t.me/{CHANNEL_USERNAME}\n"
        "Затем нажмите кнопку ниже, чтобы подтвердить:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def handle_subscription_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        chat_member = await app.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        if chat_member.status in ("member", "administrator", "creator"):
            data = load_data()
            data[str(user_id)]["subscribed"] = True
            save_data(data)
            await update.message.reply_text("🎉 Отлично! Вы участвуете в розыгрыше!", reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text("❌ Вы ещё не подписаны. Подпишитесь и нажмите кнопку снова.")
    except Exception as e:
        print("Ошибка проверки подписки:", e)
        await update.message.reply_text("❗ Не удалось проверить подписку. Попробуйте позже.")


async def draw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    data = load_data()
    participants = [u for u in data.values() if u.get("subscribed")]

    if not participants:
        await update.message.reply_text("❌ Нет участников для розыгрыша.")
        return

    winner = random.choice(participants)
    await update.message.reply_text(f"🏆 Победитель: {winner['name']} ({winner['phone']})")


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("draw", draw))
app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("✅ Я подписался"), handle_subscription_check))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name))


if __name__ == "__main__":
    print("Starting bot with webhook...")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )
