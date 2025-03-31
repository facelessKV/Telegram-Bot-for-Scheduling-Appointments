from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_services_keyboard(services):
    """
    Создает клавиатуру с доступными услугами
    
    Args:
        services (list): Список словарей с услугами
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками для выбора услуги
    """
    builder = InlineKeyboardBuilder()
    
    for service in services:
        button_text = f"{service['name']} ({service['duration']} мин, {service['price']} грн.)"
        builder.button(
            text=button_text,
            callback_data=f"service_{service['id']}"
        )
    
    # Размещаем кнопки по одной в строке
    builder.adjust(1)
    
    return builder.as_markup()

def get_time_slots_keyboard(time_slots):
    """
    Создает клавиатуру с доступными временными слотами
    
    Args:
        time_slots (list): Список доступных временных слотов
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками для выбора времени
    """
    builder = InlineKeyboardBuilder()
    
    for time_slot in time_slots:
        builder.button(
            text=time_slot,
            callback_data=f"time_{time_slot}"
        )
    
    # Размещаем кнопки по 3 в строке
    builder.adjust(3)
    
    return builder.as_markup()

def get_my_appointments_keyboard(appointments):
    """
    Создает клавиатуру для просмотра записей пользователя
    
    Args:
        appointments (list): Список словарей с записями
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками для управления записями
    """
    builder = InlineKeyboardBuilder()
    
    for appointment in appointments:
        # Форматируем дату и время для отображения
        appointment_datetime = appointment['appointment_datetime'].split()[0]
        appointment_time = appointment['appointment_datetime'].split()[1]
        
        # Получаем номер записи для отображения
        appointment_id = appointment['id']
        
        builder.button(
            text=f"❌ Отменить запись на {appointment_time} {appointment_datetime}",
            callback_data=f"cancel_appointment_{appointment_id}"
        )
    
    # Размещаем кнопки по одной в строке
    builder.adjust(1)
    
    return builder.as_markup()

def get_cancel_keyboard(appointments):
    """
    Создает клавиатуру для отмены записей
    
    Args:
        appointments (list): Список словарей с записями
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками для отмены записей
    """
    builder = InlineKeyboardBuilder()
    
    for appointment in appointments:
        # Форматируем дату и время для отображения
        appointment_datetime = appointment['appointment_datetime'].split()[0]
        appointment_time = appointment['appointment_datetime'].split()[1]
        
        # Получаем номер записи для отображения
        appointment_id = appointment['id']
        
        builder.button(
            text=f"❌ Отменить запись на {appointment_time} {appointment_datetime}",
            callback_data=f"cancel_appointment_{appointment_id}"
        )
    
    # Размещаем кнопки по одной в строке
    builder.adjust(1)
    
    return builder.as_markup()