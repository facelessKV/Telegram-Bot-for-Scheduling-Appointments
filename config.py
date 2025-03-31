import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env (если он существует)
load_dotenv()

# Токен Telegram бота (получается из переменной окружения или задается напрямую)
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')

# Настройки рабочего времени по умолчанию
DEFAULT_WORKING_HOURS = {
    0: {"start_time": "09:00", "end_time": "18:00"},  # Понедельник
    1: {"start_time": "09:00", "end_time": "18:00"},  # Вторник
    2: {"start_time": "09:00", "end_time": "18:00"},  # Среда
    3: {"start_time": "09:00", "end_time": "18:00"},  # Четверг
    4: {"start_time": "09:00", "end_time": "18:00"},  # Пятница
    5: {"start_time": "10:00", "end_time": "15:00"},  # Суббота
    6: None,  # Воскресенье (выходной)
}

# Настройки временных слотов
TIME_SLOT_DURATION = 30  # Длительность временного слота в минутах

# Настройки напоминаний
REMINDER_DAYS_BEFORE = 1  # За сколько дней до записи отправлять напоминание