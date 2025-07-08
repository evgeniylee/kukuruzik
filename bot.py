import os
import json
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.executor import start_webhook

# ========== Конфигурация ==========
TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "kukuruzikuz")
ADMIN_ID = int(os.getenv("ADMIN_ID", "2071181"))

WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", default=8000))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ========== Работа с БД ==========
def load_data():
    os.makedirs("data", exist_ok=True)
    db_path = "data/users.json"
    if not os.path.exists(db_path):
        with open(db_path, "w") as f:
            json.dump({}, f)
    with open(db_path, "r") as f:
        return json.load(f)

def save_data(data):
    with open("data/users.json", "w") as f:
        json.dump(data, f, indent=2)

# ========== Обработчики ==========
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = str(message.from_user.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {"name": None, "phone": None, "subscribed": False, "joined_at": datetime.now().isoformat()}
        save_data(data)

    await message.answer("👋 Добро пожаловать в акцию KUKURUZIK!\nПожалуйста, введите ваше имя:")

@dp.message_handler(lambda m: True)
async def get_name(message: types.Message):
    user_id = str(message.from_user.id)
    data = load_data()

    if data.get(user_id, {}).get("name") is None:
        data[user_id]["name"] = message.text
        save_data(data)

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("📞 Отправить контакт", request_contact=True))
        await message.answer("Отправьте ваш номер телефона:", reply_markup=keyboard)

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def handle_contact(message: types.Message):
    user_id = str(message.from_user.id)
    data = load_data()

    data[user_id]["phone"] = message.contact.phone_number
    save_data(data)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("✅ Я подписался"))
    await message.answer(
        f"Теперь подпишитесь на канал: https://t.me/{CHANNEL_USERNAME}\n"
        f"Затем нажмите кнопку ниже, чтобы подтвердить:",
        reply_markup=keyboard
    )

@dp.message_handler(lambda msg: msg.text == "✅ Я подписался")
async def check_subscription(message: types.Message):
    user_id = message.from_user.id
    try:
        chat_member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if chat_member.status in ("member", "administrator", "creator"):
            data = load_data()
            data[str(user_id)]["subscribed"] = True
            save_data(data)
            await message.answer("🎉 Отлично! Вы участвуете в розыгрыше!", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("❌ Вы ещё не подписаны. Подпишитесь и нажмите кнопку снова.")
    except Exception as e:
        await message.answer("❗ Не удалось проверить подписку. Попробуйте позже.")
        print(e)

@dp.message_handler(commands=["draw"])
async def draw_winner(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    data = load_data()
    participants = [u for u in data.values() if u.get("subscribed")]

    if not participants:
        await message.answer("❌ Нет участников для розыгрыша.")
        return

    winner = random.choice(participants)
    await message.answer(f"🏆 Победитель: {winner['name']} ({winner['phone']})")

# ========== Webhook запуск ==========
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
