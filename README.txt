=====================================================
     ИНСТРУКЦИЯ ПО УСТАНОВКЕ И ЗАПУСКУ TELEGRAM-БОТА
=====================================================

Эта инструкция поможет вам установить и запустить Telegram-бота для записи на прием даже если вы раньше никогда не работали с программированием.

=== ПОДГОТОВКА TELEGRAM-БОТА ===

Перед началом установки вам нужно создать нового бота в Telegram:

1. Откройте Telegram и найдите @BotFather (это официальный бот для создания ботов)
2. Отправьте ему команду /newbot
3. Следуйте инструкциям, укажите имя бота и username (должен заканчиваться на "bot")
4. BotFather выдаст вам токен бота - длинную строку символов. СОХРАНИТЕ ЕЁ!
   Пример: 1234567890:AAEcccdddeeefffggghhhjjjkkklllmmmnnn

=== УСТАНОВКА НА WINDOWS ===

1. УСТАНОВКА PYTHON:
   - Скачайте Python 3.10.11 с официального сайта: https://www.python.org/downloads/release/python-31011/
   - Прокрутите страницу вниз и выберите "Windows installer (64-bit)"
   - Запустите загруженный файл
   - ВАЖНО: Поставьте галочку "Add Python to PATH" перед нажатием "Install Now"
   - Нажмите "Install Now"
   - Дождитесь окончания установки и нажмите "Close"

2. ПОДГОТОВКА ПАПКИ ДЛЯ БОТА:
   - Создайте на диске C: папку "telegram_bot" (C:\telegram_bot)
   - Распакуйте все файлы бота в эту папку

3. СОЗДАНИЕ ФАЙЛА С ТОКЕНОМ:
   - Откройте Блокнот (Notepad)
   - Напишите: TELEGRAM_BOT_TOKEN=ваш_токен
   - Замените "ваш_токен" на токен, который вам дал BotFather
   - Сохраните файл как ".env" (с точкой в начале) в папке C:\telegram_bot
   - ВАЖНО: При сохранении выберите "Тип файла: Все файлы (*.*)" и убедитесь, что файл не сохранился как ".env.txt"

4. УСТАНОВКА ЗАВИСИМОСТЕЙ И ЗАПУСК:
   - Нажмите Win+R, введите "cmd" и нажмите Enter
   - В открывшейся командной строке введите:
     cd C:\telegram_bot
     python -m venv venv
     venv\Scripts\activate
     pip install -r requirements.txt
     python bot.py

Бот запустится и будет работать, пока открыта командная строка. Для проверки найдите вашего бота в Telegram и отправьте ему команду /start.

5. ЗАПУСК В БУДУЩЕМ:
   - Чтобы запустить бота в следующий раз, просто откройте командную строку и введите:
     cd C:\telegram_bot
     venv\Scripts\activate
     python bot.py

=== УСТАНОВКА НА LINUX ===

1. УСТАНОВКА PYTHON И НЕОБХОДИМЫХ ПАКЕТОВ:
   Откройте терминал и введите:

   Для Ubuntu/Debian:
   sudo apt update
   sudo apt install python3.10 python3.10-venv python3-pip git -y

   Для CentOS/RHEL:
   sudo yum install python3 python3-pip git -y

2. СКАЧИВАНИЕ ФАЙЛОВ БОТА:
   - Создайте папку для бота:
     mkdir -p ~/telegram_bot
     cd ~/telegram_bot
   
   - Скопируйте все файлы бота в эту папку

3. СОЗДАНИЕ ФАЙЛА С ТОКЕНОМ:
   - Введите в терминале:
     echo "TELEGRAM_BOT_TOKEN=ваш_токен" > .env
   
   - Замените "ваш_токен" на токен, который вам дал BotFather

4. СОЗДАНИЕ ВИРТУАЛЬНОГО ОКРУЖЕНИЯ И УСТАНОВКА ЗАВИСИМОСТЕЙ:
   - Введите в терминале:
     cd ~/telegram_bot
     python3 -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt

5. ЗАПУСК БОТА:
   - Введите в терминале:
     python bot.py
   
   Бот запустится и будет работать, пока терминал открыт. Для проверки найдите вашего бота в Telegram и отправьте ему команду /start.

6. ЗАПУСК В БУДУЩЕМ:
   - Чтобы запустить бота в следующий раз, откройте терминал и введите:
     cd ~/telegram_bot
     source venv/bin/activate
     python bot.py

7. НАСТРОЙКА АВТОЗАПУСКА (ОПЦИОНАЛЬНО):
   Если вы хотите, чтобы бот запускался автоматически и работал в фоне:

   - Создайте файл службы:
     sudo nano /etc/systemd/system/telegram-bot.service

   - Вставьте в файл (замените "username" на ваше имя пользователя):

     [Unit]
     Description=Telegram Bot Service
     After=network.target

     [Service]
     User=username
     WorkingDirectory=/home/username/telegram_bot
     ExecStart=/home/username/telegram_bot/venv/bin/python bot.py
     Restart=always

     [Install]
     WantedBy=multi-user.target

   - Нажмите Ctrl+O, затем Enter, чтобы сохранить
   - Нажмите Ctrl+X, чтобы выйти из редактора

   - Активируйте и запустите службу:
     sudo systemctl daemon-reload
     sudo systemctl enable telegram-bot.service
     sudo systemctl start telegram-bot.service

   - Проверьте статус службы:
     sudo systemctl status telegram-bot.service

=== ВОЗМОЖНЫЕ ПРОБЛЕМЫ И ИХ РЕШЕНИЕ ===

1. "pip не является внутренней или внешней командой" (Windows):
   - Переустановите Python, убедившись, что отметили галочку "Add Python to PATH"

2. "Модуль не найден" при запуске бота:
   - Проверьте, что активировали виртуальное окружение (venv) перед запуском
   - Убедитесь, что правильно установили зависимости: pip install -r requirements.txt

3. Бот не отвечает в Telegram:
   - Проверьте токен в файле .env
   - Убедитесь, что бот запущен (командная строка/терминал открыты)
   - Проверьте подключение к интернету

4. Ошибка "permission denied" (Linux):
   - Проверьте права доступа: chmod +x bot.py
   - Запустите с правами суперпользователя: sudo python bot.py

=== ИСПОЛЬЗОВАНИЕ БОТА ===

После успешного запуска бота, вы можете использовать следующие команды в Telegram:

/start - начать работу с ботом
/book - забронировать время
/my_appointments - просмотреть ваши записи
/cancel - отменить запись

=== АДМИНИСТРИРОВАНИЕ ===

Для добавления/изменения услуг или рабочего расписания, необходимо редактировать базу данных appointments.db. Это можно сделать с помощью программы SQLite Browser:

Windows: https://sqlitebrowser.org/dl/
Linux: sudo apt install sqlitebrowser (для Ubuntu/Debian)