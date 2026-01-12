import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 6185367393))
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')

# Валюты для отслеживания
CURRENCIES = ['USD', 'EUR']

# Интервал обновления курсов (в секундах)
UPDATE_INTERVAL = 300  # 5 минут

# Путь к данным
DATA_DIR = 'data'
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://darnitsacash.netlify.app')

