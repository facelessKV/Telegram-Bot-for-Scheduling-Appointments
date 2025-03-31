import asyncio
from datetime import datetime, timedelta

class AppointmentScheduler:
    def __init__(self, db):
        """
        Инициализация планировщика
        
        Args:
            db (Database): Экземпляр класса для работы с базой данных
        """
        self.db = db
        self.running = False
    
    def get_available_slots(self, date, duration):
        """
        Получает доступные временные слоты для выбранной даты и длительности услуги
        
        Args:
            date (datetime): Дата для проверки
            duration (int): Длительность услуги в минутах
            
        Returns:
            list: Список доступных временных слотов в формате "ЧЧ:ММ"
        """
        # Получаем день недели (0 = Понедельник, 6 = Воскресенье)
        day_of_week = date.weekday()
        
        # Получаем рабочие часы для выбранного дня недели
        working_hours = self.db.get_working_hours(day_of_week)
        
        # Если для выбранного дня нет рабочих часов (например, выходной), возвращаем пустой список
        if not working_hours:
            return []
        
        # Разбираем время начала и окончания работы
        start_time = datetime.strptime(working_hours['start_time'], "%H:%M")
        end_time = datetime.strptime(working_hours['end_time'], "%H:%M")
        
        # Создаем временные слоты с интервалом в 30 минут
        slots = []
        current_time = start_time
        
        while current_time <= end_time - timedelta(minutes=duration):
            slot = current_time.strftime("%H:%M")
            slots.append(slot)
            current_time += timedelta(minutes=30)
        
        # Получаем все записи на выбранную дату
        date_str = date.strftime("%Y-%m-%d")
        next_date = (date + timedelta(days=1)).strftime("%Y-%m-%d")
        appointments = self.db.get_appointments_by_date_range(date_str, date_str)
        
        # Исключаем занятые слоты
        available_slots = slots.copy()
        for appointment in appointments:
            appointment_time = datetime.strptime(appointment['appointment_datetime'], "%Y-%m-%d %H:%M").time()
            appointment_duration = appointment['duration']
            
            # Проверяем каждый доступный слот
            for slot in slots:
                slot_time = datetime.strptime(slot, "%H:%M").time()
                slot_end_time = (datetime.strptime(slot, "%H:%M") + timedelta(minutes=duration)).time()
                appointment_end_time = (datetime.strptime(appointment_time.strftime("%H:%M"), "%H:%M") + timedelta(minutes=appointment_duration)).time()
                
                # Если слот пересекается с уже существующей записью, удаляем его из доступных
                if (slot_time <= appointment_time < slot_end_time) or \
                   (slot_time < appointment_end_time <= slot_end_time) or \
                   (appointment_time <= slot_time and appointment_end_time >= slot_end_time):
                    if slot in available_slots:
                        available_slots.remove(slot)
        
        return available_slots
    
    def schedule_reminder(self, appointment_id, user_id, service_name, date, time, reminder_datetime):
        """
        Планирует напоминание о записи
        
        Args:
            appointment_id (int): ID записи
            user_id (int): ID пользователя
            service_name (str): Название услуги
            date (str): Дата приема
            time (str): Время приема
            reminder_datetime (datetime): Дата и время напоминания
        """
        # Форматируем дату и время напоминания
        reminder_datetime_str = reminder_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        # Добавляем напоминание в базу данных
        self.db.add_reminder(appointment_id, reminder_datetime_str)
    
    async def start_scheduler(self, send_reminder_callback):
        """
        Запускает планировщик для отправки напоминаний
        
        Args:
            send_reminder_callback (function): Функция обратного вызова для отправки напоминаний
        """
        self.running = True
        
        while self.running:
            # Получаем все напоминания, которые должны быть отправлены
            reminders = self.db.get_pending_reminders()
            
            for reminder in reminders:
                # Получаем информацию о записи
                appointment = self.db.get_appointment_by_id(reminder['appointment_id'])
                
                if appointment:
                    # Получаем информацию об услуге
                    service = self.db.get_service_by_id(appointment['service_id'])
                    
                    # Форматируем дату и время для отображения
                    appointment_datetime = datetime.strptime(appointment['appointment_datetime'], "%Y-%m-%d %H:%M")
                    formatted_date = appointment_datetime.strftime("%d.%m.%Y")
                    formatted_time = appointment_datetime.strftime("%H:%M")
                    
                    # Отправляем напоминание
                    await send_reminder_callback(
                        appointment['user_id'],
                        service['name'],
                        formatted_date,
                        formatted_time
                    )
                    
                    # Отмечаем напоминание как отправленное
                    self.db.mark_reminder_as_sent(reminder['id'])
            
            # Проверяем напоминания каждые 5 минут
            await asyncio.sleep(300)
    
    def stop_scheduler(self):
        """
        Останавливает планировщик
        """
        self.running = False