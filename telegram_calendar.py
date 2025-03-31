from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from calendar import monthrange

# Константы для календаря
MONTHS = [
    'Январь', 'Февраль', 'Март', 'Апрель',
    'Май', 'Июнь', 'Июль', 'Август',
    'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
]
DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

def create_calendar(year=None, month=None):
    """
    Создает клавиатуру с календарем
    
    Args:
        year (int): Год для отображения
        month (int): Месяц для отображения
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с календарем
    """
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    
    builder = InlineKeyboardBuilder()
    
    # Заголовок с месяцем и годом
    builder.button(
        text='<<<',
        callback_data=f'calendar:prev:{year}:{month}'
    )
    builder.button(
        text=f'{MONTHS[month-1]} {year}',
        callback_data='calendar:ignore'
    )
    builder.button(
        text='>>>',
        callback_data=f'calendar:next:{year}:{month}'
    )
    
    # Первый ряд - названия дней недели
    for day in DAYS:
        builder.button(
            text=day,
            callback_data='calendar:ignore'
        )
    
    # Дни месяца
    month_days = monthrange(year, month)[1]
    first_day_of_month = datetime(year, month, 1).weekday()
    
    # Создаем пустые кнопки для выравнивания
    for _ in range(first_day_of_month):
        builder.button(
            text=' ',
            callback_data='calendar:ignore'
        )
    
    # Добавляем кнопки с днями месяца
    for day in range(1, month_days + 1):
        day_date = datetime(year, month, day)
        if day_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            # Делаем неактивной кнопку для прошедших дней
            builder.button(
                text=f'{day}',
                callback_data='calendar:ignore'
            )
        else:
            builder.button(
                text=f'{day}',
                callback_data=f'calendar:day:{year}:{month}:{day}'
            )
    
    # Устанавливаем ширину рядов
    builder.adjust(7, 7, 7, 7, 7, 7)
    
    return builder.as_markup()

def process_calendar_selection(callback_data):
    """
    Обрабатывает данные колбэка календаря
    
    Args:
        callback_data (str): Строка данных колбэка
        
    Returns:
        tuple: Кортеж из трех элементов:
            - result (datetime or None): Выбранная дата или None
            - markup (InlineKeyboardMarkup or None): Обновленная клавиатура календаря или None
            - step (str): Текущий шаг ('day', 'prev', 'next', 'ignore')
    """
    parts = callback_data.split(':')
    
    if len(parts) < 2:
        return None, None, None
    
    prefix, action = parts[:2]
    
    if prefix != 'calendar':
        return None, None, None
    
    # Обработка игнорируемых действий
    if action == 'ignore':
        return None, None, 'ignore'
    
    # Обработка переключения месяцев
    if action in ['prev', 'next']:
        year, month = int(parts[2]), int(parts[3])
        
        if action == 'prev':
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1
        elif action == 'next':
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
        
        return None, create_calendar(year, month), action
    
    # Обработка выбора дня
    if action == 'day':
        year, month, day = int(parts[2]), int(parts[3]), int(parts[4])
        return datetime(year, month, day), None, 'day'
    
    return None, None, None