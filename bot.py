import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import Database
from scheduler import AppointmentScheduler
from keyboards import (
    get_services_keyboard, get_cancel_keyboard, 
    get_time_slots_keyboard, get_my_appointments_keyboard
)
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Определение состояний для FSM (Finite State Machine)
class BookingStates(StatesGroup):
    selecting_service = State()  # Состояние выбора услуги
    selecting_date = State()     # Состояние выбора даты
    selecting_time = State()     # Состояние выбора времени
    confirming = State()         # Состояние подтверждения записи
    cancelling = State()         # Состояние отмены записи

# Инициализация базы данных и планировщика
db = Database('appointments.db')
scheduler = None  # Будет инициализирован позже

# Функция для отправки напоминаний
async def send_reminder(bot: Bot, user_id: int, service_name: str, date: str, time: str):
    """
    Отправляет напоминание пользователю о предстоящей записи
    """
    await bot.send_message(
        user_id,
        f"⏰ Напоминание!\n\n"
        f"Завтра у вас запись на {service_name}\n"
        f"Дата: {date}\n"
        f"Время: {time}\n\n"
        f"Для отмены используйте команду /cancel"
    )

# Инициализация бота и диспетчера
async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    global scheduler
    scheduler = AppointmentScheduler(db)
    
    # Регистрация обработчиков команд
    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        """
        Обработчик команды /start
        Отправляет приветственное сообщение и инструкции по использованию бота
        """
        await message.answer(
            "👋 Добро пожаловать в бот записи на прием!\n\n"
            "Используйте следующие команды:\n"
            "/book - забронировать время\n"
            "/my_appointments - просмотреть ваши записи\n"
            "/cancel - отменить запись"
        )

    @dp.message(Command("book"))
    async def cmd_book(message: Message, state: FSMContext):
        """
        Обработчик команды /book
        Начинает процесс бронирования, показывая доступные услуги
        """
        # Получаем список услуг из базы данных
        services = db.get_services()
        # Создаем клавиатуру с услугами
        keyboard = get_services_keyboard(services)
        
        await message.answer("Выберите услугу:", reply_markup=keyboard)
        # Устанавливаем состояние выбора услуги
        await state.set_state(BookingStates.selecting_service)

    @dp.callback_query(lambda c: c.data.startswith('service_'), BookingStates.selecting_service)
    async def process_service_selection(callback_query: CallbackQuery, state: FSMContext):
        """
        Обработчик выбора услуги
        Сохраняет выбранную услугу и показывает календарь для выбора даты
        """
        # Извлекаем ID услуги из данных колбэка
        service_id = int(callback_query.data.split('_')[1])
        
        # Получаем информацию о выбранной услуге
        service = db.get_service_by_id(service_id)
        
        # Сохраняем выбранную услугу в состоянии
        await state.update_data(
            service_id=service_id,
            service_name=service['name'],
            duration=service['duration']
        )

        # Импортируем календарь только тут, чтобы избежать циклических импортов
        from telegram_calendar import create_calendar
        
        # Получаем текущую дату
        now = datetime.now()
        
        # Создаем клавиатуру календаря
        calendar_markup = create_calendar(
            year=now.year,
            month=now.month,
        )
        
        await callback_query.answer()
        await callback_query.message.answer(
            f"Вы выбрали: {service['name']} (Длительность: {service['duration']} мин)\n\nТеперь выберите дату:",
            reply_markup=calendar_markup
        )
        
        # Устанавливаем состояние выбора даты
        await state.set_state(BookingStates.selecting_date)

    @dp.callback_query(lambda c: c.data.startswith('calendar'), BookingStates.selecting_date)
    async def process_calendar(callback_query: CallbackQuery, state: FSMContext):
        """
        Обработчик выбора даты в календаре
        Проверяет выбранную дату и показывает доступные временные слоты
        """
        from telegram_calendar import process_calendar_selection, create_calendar
        
        # Обрабатываем данные колбэка календаря
        result, key, step = process_calendar_selection(callback_query.data)
        
        if not result and key:
            # Пользователь переключил месяц или год, обновляем календарь
            await callback_query.message.edit_reply_markup(
                reply_markup=key
            )
            return
        
        if result:
            # Пользователь выбрал день
            selected_date = result
            
            # Проверяем, что выбранная дата не в прошлом
            if selected_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                await callback_query.answer(
                    text="Нельзя выбрать дату в прошлом!",
                    show_alert=True
                )
                return
            
            # Сохраняем выбранную дату в состоянии
            data = await state.get_data()
            await state.update_data(selected_date=selected_date.strftime("%Y-%m-%d"))
            service_id = data['service_id']
            duration = data['duration']
            
            # Получаем доступные временные слоты для выбранной даты и услуги
            available_slots = scheduler.get_available_slots(
                selected_date, 
                duration
            )
            
            if not available_slots:
                await callback_query.answer()
                await callback_query.message.answer(
                    "К сожалению, на выбранную дату нет доступных слотов. Пожалуйста, выберите другую дату.",
                    reply_markup=create_calendar(
                        year=selected_date.year,
                        month=selected_date.month
                    )
                )
                return
            
            # Создаем клавиатуру с доступными временными слотами
            time_slots_markup = get_time_slots_keyboard(available_slots)
            
            await callback_query.answer()
            await callback_query.message.answer(
                f"Выбранная дата: {selected_date.strftime('%d.%m.%Y')}\n\nДоступные временные слоты:",
                reply_markup=time_slots_markup
            )
            
            # Устанавливаем состояние выбора времени
            await state.set_state(BookingStates.selecting_time)

    @dp.callback_query(lambda c: c.data.startswith('time_'), BookingStates.selecting_time)
    async def process_time_selection(callback_query: CallbackQuery, state: FSMContext):
        """
        Обработчик выбора временного слота
        Сохраняет выбранное время и запрашивает подтверждение бронирования
        """
        # Извлекаем выбранное время из данных колбэка
        selected_time = callback_query.data.split('_')[1]
        
        # Сохраняем выбранное время в состоянии
        await state.update_data(selected_time=selected_time)
        data = await state.get_data()
        service_name = data['service_name']
        selected_date = data['selected_date']
        
        # Форматируем дату для отображения
        formatted_date = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%d.%m.%Y")
        
        # Создаем клавиатуру для подтверждения бронирования
        builder = InlineKeyboardBuilder()
        builder.button(text="Подтвердить", callback_data="confirm")
        builder.button(text="Отмена", callback_data="cancel")
        builder.adjust(2)  # Размещаем кнопки в один ряд
        
        await callback_query.answer()
        await callback_query.message.answer(
            f"Пожалуйста, подтвердите бронирование:\n\n"
            f"Услуга: {service_name}\n"
            f"Дата: {formatted_date}\n"
            f"Время: {selected_time}\n\n"
            f"Всё верно?",
            reply_markup=builder.as_markup()
        )
        
        # Устанавливаем состояние подтверждения
        await state.set_state(BookingStates.confirming)

    @dp.callback_query(F.data == "confirm", BookingStates.confirming)
    async def process_confirmation(callback_query: CallbackQuery, state: FSMContext):
        """
        Обработчик подтверждения бронирования
        Сохраняет запись в базе данных и отправляет подтверждение пользователю
        """
        user_id = callback_query.from_user.id
        user_name = callback_query.from_user.username or f"{callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}"
        
        # Получаем данные из состояния
        data = await state.get_data()
        service_id = data['service_id']
        service_name = data['service_name']
        selected_date = data['selected_date']
        selected_time = data['selected_time']
        duration = data['duration']
        
        # Форматируем дату и время для сохранения в базе данных
        appointment_datetime = f"{selected_date} {selected_time}"
        
        # Сохраняем запись в базе данных
        appointment_id = db.add_appointment(
            user_id=user_id,
            user_name=user_name,
            service_id=service_id,
            appointment_datetime=appointment_datetime,
            duration=duration
        )
        
        # Форматируем дату для отображения
        formatted_date = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%d.%m.%Y")
        
        # Планируем напоминание о записи
        reminder_date = datetime.strptime(appointment_datetime, "%Y-%m-%d %H:%M") - timedelta(days=1)
        scheduler.schedule_reminder(appointment_id, user_id, service_name, formatted_date, selected_time, reminder_date)
        
        await callback_query.answer()
        await callback_query.message.answer(
            f"✅ Запись успешно создана!\n\n"
            f"Услуга: {service_name}\n"
            f"Дата: {formatted_date}\n"
            f"Время: {selected_time}\n\n"
            f"Вы получите напоминание за день до приема. "
            f"Чтобы отменить запись, используйте команду /cancel."
        )
        
        # Сбрасываем состояние
        await state.clear()

    @dp.callback_query(F.data == "cancel", BookingStates.confirming)
    async def process_cancel_confirmation(callback_query: CallbackQuery, state: FSMContext):
        """
        Обработчик отмены во время подтверждения бронирования
        Отменяет процесс бронирования и сбрасывает состояние
        """
        await callback_query.answer()
        await callback_query.message.answer(
            "❌ Бронирование отменено. Чтобы начать заново, используйте команду /book."
        )
        
        # Сбрасываем состояние
        await state.clear()

    @dp.message(Command("my_appointments"))
    async def cmd_my_appointments(message: Message):
        """
        Обработчик команды /my_appointments
        Показывает список записей пользователя
        """
        user_id = message.from_user.id
        
        # Получаем список записей пользователя из базы данных
        appointments = db.get_user_appointments(user_id)
        
        if not appointments:
            await message.answer("У вас нет активных записей.")
            return
        
        # Создаем текст сообщения со списком записей
        appointments_text = "Ваши записи:\n\n"
        
        for idx, appointment in enumerate(appointments, 1):
            service_name = db.get_service_by_id(appointment['service_id'])['name']
            appointment_datetime = datetime.strptime(appointment['appointment_datetime'], "%Y-%m-%d %H:%M")
            formatted_date = appointment_datetime.strftime("%d.%m.%Y")
            formatted_time = appointment_datetime.strftime("%H:%M")
            
            appointments_text += f"{idx}. {service_name}\n" \
                               f"   Дата: {formatted_date}\n" \
                               f"   Время: {formatted_time}\n\n"
        
        # Создаем клавиатуру для отмены записей
        keyboard = get_my_appointments_keyboard(appointments)
        
        await message.answer(appointments_text, reply_markup=keyboard)

    @dp.callback_query(lambda c: c.data.startswith('cancel_appointment_'))
    async def process_cancel_appointment_button(callback_query: CallbackQuery):
        """
        Обработчик кнопки отмены конкретной записи
        Запрашивает подтверждение отмены
        """
        # Извлекаем ID записи из данных колбэка
        appointment_id = int(callback_query.data.split('_')[2])
        
        # Получаем информацию о записи из базы данных
        appointment = db.get_appointment_by_id(appointment_id)
        
        if not appointment:
            await callback_query.answer(text="Запись не найдена!")
            return
        
        # Проверяем, что запись принадлежит текущему пользователю
        if appointment['user_id'] != callback_query.from_user.id:
            await callback_query.answer(text="Эта запись не принадлежит вам!")
            return
        
        # Получаем информацию об услуге
        service = db.get_service_by_id(appointment['service_id'])
        
        # Форматируем дату и время для отображения
        appointment_datetime = datetime.strptime(appointment['appointment_datetime'], "%Y-%m-%d %H:%M")
        formatted_date = appointment_datetime.strftime("%d.%m.%Y")
        formatted_time = appointment_datetime.strftime("%H:%M")
        
        # Создаем клавиатуру для подтверждения отмены
        builder = InlineKeyboardBuilder()
        builder.button(text="Да, отменить", callback_data=f"confirm_cancel_{appointment_id}")
        builder.button(text="Нет, оставить", callback_data="cancel_confirmation")
        builder.adjust(2)  # Размещаем кнопки в один ряд
        
        await callback_query.answer()
        await callback_query.message.answer(
            f"Вы уверены, что хотите отменить запись?\n\n"
            f"Услуга: {service['name']}\n"
            f"Дата: {formatted_date}\n"
            f"Время: {formatted_time}",
            reply_markup=builder.as_markup()
        )

    @dp.callback_query(lambda c: c.data.startswith('confirm_cancel_'))
    async def process_confirm_cancel(callback_query: CallbackQuery):
        """
        Обработчик подтверждения отмены записи
        Удаляет запись из базы данных и отправляет подтверждение пользователю
        """
        # Извлекаем ID записи из данных колбэка
        appointment_id = int(callback_query.data.split('_')[2])
        
        # Удаляем запись из базы данных
        success = db.delete_appointment(appointment_id)
        
        if success:
            await callback_query.answer()
            await callback_query.message.answer(
                "✅ Запись успешно отменена."
            )
        else:
            await callback_query.answer()
            await callback_query.message.answer(
                "❌ Произошла ошибка при отмене записи. Пожалуйста, попробуйте снова."
            )

    @dp.callback_query(F.data == "cancel_confirmation")
    async def process_cancel_confirmation_cancel(callback_query: CallbackQuery):
        """
        Обработчик отмены подтверждения отмены записи
        Отменяет процесс отмены и отправляет сообщение пользователю
        """
        await callback_query.answer()
        await callback_query.message.answer(
            "Отмена записи отменена. Ваша запись сохранена."
        )

    @dp.message(Command("cancel"))
    async def cmd_cancel(message: Message):
        """
        Обработчик команды /cancel
        Показывает список записей пользователя с возможностью отмены
        """
        user_id = message.from_user.id
        
        # Получаем список записей пользователя из базы данных
        appointments = db.get_user_appointments(user_id)
        
        if not appointments:
            await message.answer("У вас нет активных записей для отмены.")
            return
        
        # Создаем текст сообщения со списком записей
        appointments_text = "Выберите запись для отмены:\n\n"
        
        for idx, appointment in enumerate(appointments, 1):
            service_name = db.get_service_by_id(appointment['service_id'])['name']
            appointment_datetime = datetime.strptime(appointment['appointment_datetime'], "%Y-%m-%d %H:%M")
            formatted_date = appointment_datetime.strftime("%d.%m.%Y")
            formatted_time = appointment_datetime.strftime("%H:%M")
            
            appointments_text += f"{idx}. {service_name}\n" \
                               f"   Дата: {formatted_date}\n" \
                               f"   Время: {formatted_time}\n\n"
        
        # Создаем клавиатуру для отмены записей
        keyboard = get_cancel_keyboard(appointments)
        
        await message.answer(appointments_text, reply_markup=keyboard)

    @dp.message()
    async def process_other_messages(message: Message):
        """
        Обработчик для любых других сообщений
        Отправляет инструкции по использованию бота
        """
        await message.answer(
            "Пожалуйста, используйте команды:\n"
            "/book - забронировать время\n"
            "/my_appointments - просмотреть ваши записи\n"
            "/cancel - отменить запись"
        )

    # Запускаем планировщик для напоминаний
    asyncio.create_task(scheduler.start_scheduler(lambda user_id, service, date, time: 
                                                send_reminder(bot, user_id, service, date, time)))
    
    # Создаем таблицы в базе данных и добавляем тестовые данные
    db.create_tables()
    services = db.get_services()
    if not services:
        db.add_service("Консультация", 30, 1000)
        db.add_service("Диагностика", 60, 2000)
        db.add_service("Тренировка", 90, 3000)
    
    logger.info("Бот успешно запущен!")
    
    try:
        # Запускаем поллинг
        await dp.start_polling(bot)
    finally:
        # Закрываем сессию бота при завершении
        await bot.session.close()
        scheduler.stop_scheduler()

if __name__ == '__main__':
    # Запускаем бота
    asyncio.run(main())