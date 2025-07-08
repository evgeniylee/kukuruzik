import os

# Токен Telegram-бота (устанавливается через переменные окружения)
TOKEN = os.getenv("BOT_TOKEN")

# Имя Telegram-канала без @
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "kukuruzikuz")

# ID админа (устанавливается через переменные окружения или используется значение по умолчанию)
ADMIN_ID = int(os.getenv("ADMIN_ID", "2071181"))

# URL вебхука (Render сам задаёт это значение через переменную RENDER_EXTERNAL_URL)
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Настройки сервера
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", default=8000))
