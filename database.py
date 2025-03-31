import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_file):
        """
        Инициализация базы данных
        
        Args:
            db_file (str): Путь к файлу базы данных SQLite
        """
        self.db_file = db_file
        self.conn = None
    
    def _connect(self):
        """
        Создает соединение с базой данных
        
        Returns:
            sqlite3.Connection: Объект соединения с базой данных
        """
        self.conn = sqlite3.connect(self.db_file)
        # Настраиваем соединение для возврата строк в виде словарей
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def _close(self):
        """
        Закрывает соединение с базой данных
        """
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def create_tables(self):
        """
        Создает необходимые таблицы в базе данных, если они не существуют
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            # Создаем таблицу услуг
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    price REAL NOT NULL
                )
            ''')
            
            # Создаем таблицу записей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    service_id INTEGER NOT NULL,
                    appointment_datetime TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (service_id) REFERENCES services (id)
                )
            ''')
            
            # Создаем таблицу рабочих часов (для настройки расписания)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS working_hours (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day_of_week INTEGER NOT NULL,  -- 0 = Понедельник, 6 = Воскресенье
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL
                )
            ''')
            
            # Создаем таблицу для хранения информации о напоминаниях
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appointment_id INTEGER NOT NULL,
                    reminder_datetime TEXT NOT NULL,
                    sent BOOLEAN NOT NULL DEFAULT 0,
                    FOREIGN KEY (appointment_id) REFERENCES appointments (id) ON DELETE CASCADE
                )
            ''')
            
            # Заполняем таблицу рабочих часов, если она пуста
            cursor.execute("SELECT COUNT(*) FROM working_hours")
            if cursor.fetchone()[0] == 0:
                # Добавляем рабочие часы для будних дней (9:00 - 18:00)
                for day in range(5):  # Понедельник - Пятница
                    cursor.execute(
                        "INSERT INTO working_hours (day_of_week, start_time, end_time) VALUES (?, ?, ?)",
                        (day, "09:00", "18:00")
                    )
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблиц: {e}")
        finally:
            self._close()
    
    def add_service(self, name, duration, price):
        """
        Добавляет новую услугу в базу данных
        
        Args:
            name (str): Название услуги
            duration (int): Длительность услуги в минутах
            price (float): Стоимость услуги
            
        Returns:
            int: ID созданной услуги
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO services (name, duration, price) VALUES (?, ?, ?)",
                (name, duration, price)
            )
            
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении услуги: {e}")
            return None
        finally:
            self._close()
    
    def get_services(self):
        """
        Получает список всех доступных услуг
        
        Returns:
            list: Список словарей с услугами
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, name, duration, price FROM services")
            
            # Преобразуем результат в список словарей
            services = [dict(row) for row in cursor.fetchall()]
            
            return services
        except sqlite3.Error as e:
            print(f"Ошибка при получении услуг: {e}")
            return []
        finally:
            self._close()
    
    def get_service_by_id(self, service_id):
        """
        Получает информацию об услуге по ID
        
        Args:
            service_id (int): ID услуги
            
        Returns:
            dict: Словарь с информацией об услуге
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, name, duration, price FROM services WHERE id = ?",
                (service_id,)
            )
            
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"Ошибка при получении услуги: {e}")
            return None
        finally:
            self._close()
    
    def add_appointment(self, user_id, user_name, service_id, appointment_datetime, duration):
        """
        Добавляет новую запись на прием
        
        Args:
            user_id (int): ID пользователя Telegram
            user_name (str): Имя пользователя Telegram
            service_id (int): ID услуги
            appointment_datetime (str): Дата и время приема в формате "ГГГГ-ММ-ДД ЧЧ:ММ"
            duration (int): Длительность приема в минутах
            
        Returns:
            int: ID созданной записи
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute(
                """
                INSERT INTO appointments 
                (user_id, user_name, service_id, appointment_datetime, duration, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, user_name, service_id, appointment_datetime, duration, created_at)
            )
            
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении записи: {e}")
            return None
        finally:
            self._close()
    
    def get_user_appointments(self, user_id):
        """
        Получает список записей пользователя
        
        Args:
            user_id (int): ID пользователя Telegram
            
        Returns:
            list: Список словарей с записями
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT id, user_id, service_id, appointment_datetime, duration
                FROM appointments
                WHERE user_id = ? AND datetime(appointment_datetime) > datetime('now')
                ORDER BY datetime(appointment_datetime)
                """,
                (user_id,)
            )
            
            # Преобразуем результат в список словарей
            appointments = [dict(row) for row in cursor.fetchall()]
            
            return appointments
        except sqlite3.Error as e:
            print(f"Ошибка при получении записей пользователя: {e}")
            return []
        finally:
            self._close()
    
    def get_appointment_by_id(self, appointment_id):
        """
        Получает информацию о записи по ID
        
        Args:
            appointment_id (int): ID записи
            
        Returns:
            dict: Словарь с информацией о записи
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT id, user_id, service_id, appointment_datetime, duration
                FROM appointments
                WHERE id = ?
                """,
                (appointment_id,)
            )
            
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"Ошибка при получении записи: {e}")
            return None
        finally:
            self._close()
    
    def delete_appointment(self, appointment_id):
        """
        Удаляет запись на прием
        
        Args:
            appointment_id (int): ID записи
            
        Returns:
            bool: True в случае успешного удаления, False в противном случае
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
            
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении записи: {e}")
            return False
        finally:
            self._close()
    
    def get_appointments_by_date_range(self, start_date, end_date):
        """
        Получает список записей в заданном диапазоне дат
        
        Args:
            start_date (str): Начальная дата в формате "ГГГГ-ММ-ДД"
            end_date (str): Конечная дата в формате "ГГГГ-ММ-ДД"
            
        Returns:
            list: Список словарей с записями
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT id, user_id, service_id, appointment_datetime, duration
                FROM appointments
                WHERE date(appointment_datetime) BETWEEN date(?) AND date(?)
                ORDER BY datetime(appointment_datetime)
                """,
                (start_date, end_date)
            )
            
            # Преобразуем результат в список словарей
            appointments = [dict(row) for row in cursor.fetchall()]
            
            return appointments
        except sqlite3.Error as e:
            print(f"Ошибка при получении записей по диапазону дат: {e}")
            return []
        finally:
            self._close()
    
    def get_working_hours(self, day_of_week):
        """
        Получает информацию о рабочих часах для определенного дня недели
        
        Args:
            day_of_week (int): День недели (0 = Понедельник, 6 = Воскресенье)
            
        Returns:
            dict: Словарь с информацией о рабочих часах
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, day_of_week, start_time, end_time FROM working_hours WHERE day_of_week = ?",
                (day_of_week,)
            )
            
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"Ошибка при получении рабочих часов: {e}")
            return None
        finally:
            self._close()
    
    def add_reminder(self, appointment_id, reminder_datetime):
        """
        Добавляет напоминание о записи
        
        Args:
            appointment_id (int): ID записи
            reminder_datetime (str): Дата и время напоминания в формате "ГГГГ-ММ-ДД ЧЧ:ММ:СС"
            
        Returns:
            int: ID созданного напоминания
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO reminders (appointment_id, reminder_datetime, sent) VALUES (?, ?, 0)",
                (appointment_id, reminder_datetime)
            )
            
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении напоминания: {e}")
            return None
        finally:
            self._close()
    
    def get_pending_reminders(self):
        """
        Получает список неотправленных напоминаний, которые должны быть отправлены
        
        Returns:
            list: Список словарей с напоминаниями
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT r.id, r.appointment_id, r.reminder_datetime,
                       a.user_id, a.service_id, a.appointment_datetime
                FROM reminders r
                JOIN appointments a ON r.appointment_id = a.id
                WHERE r.sent = 0 AND datetime(r.reminder_datetime) <= datetime('now')
                """
            )
            
            # Преобразуем результат в список словарей
            reminders = [dict(row) for row in cursor.fetchall()]
            
            return reminders
        except sqlite3.Error as e:
            print(f"Ошибка при получении напоминаний: {e}")
            return []
        finally:
            self._close()
    
    def mark_reminder_as_sent(self, reminder_id):
        """
        Отмечает напоминание как отправленное
        
        Args:
            reminder_id (int): ID напоминания
            
        Returns:
            bool: True в случае успешного обновления, False в противном случае
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE reminders SET sent = 1 WHERE id = ?",
                (reminder_id,)
            )
            
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении напоминания: {e}")
            return False
        finally:
            self._close()