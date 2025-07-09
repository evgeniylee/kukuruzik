import os

BOT_TOKEN = os.getenv("7207628297:AAHMB7xcxu9-CbnWGzsAZLYnjp9sHgqPle4")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "kukuruzikuz")
ADMIN_ID = int(os.getenv("ADMIN_ID", "2071181"))
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL", "")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
