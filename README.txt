📅 Telegram Bot for Scheduling Appointments

Looking for a way to simplify making appointments for clients? This bot will solve your problem!
Allow users to easily choose a convenient time for a meeting without wasting time on calls.

 ✅ What can he do?

 • 🕒 Shows the available time slots for recording
 • 📝 Allows you to book an appointment time
 • ⏰ Sends recording reminders
 • 📂 Stores information about all records

🔧 Functionality

✅ Automatic reminders about upcoming appointments
✅ Easy to set up available time slots
✅ User-friendly interface for users and administrators

Are you ready to simplify the appointment process?

Contact me on Telegram and I will help you set up this bot for your business! 🚀

=====================================================
     INSTRUCTIONS FOR INSTALLING AND LAUNCHING A TELEGRAM BOT
=====================================================

This guide will help you install and launch a Telegram bot to make an appointment, even if you have never worked with programming before.

=== TELEGRAM BOT PREPARATION ===

Before starting the installation, you need to create a new bot in Telegram.:

1. Open Telegram and find @BotFather (this is the official bot for creating bots)
2. Send him a command /newbot
3. Follow the instructions, enter the bot's name and username (must end with "bot")
4. BotFather will give you a bot token - a long string of characters. SAVE HER!
   Example: 1234567890:AAECCCDDDEEFFFGGGHHHJJKKKLLLMMMNNN

=== INSTALLATION ON WINDOWS ===

1. INSTALL PYTHON:
- Download Python 3.10.11 from the official website: https://www.python.org/downloads/release/python-31011 /
- Scroll down and select "Windows installer (64-bit)"
- Run the downloaded file
   - IMPORTANT: Check the box "Add Python to PATH" before clicking "Install Now"
- Click "Install Now"
- Wait for the installation to finish and click "Close"

2. PREPARING A FOLDER FOR THE BOT:
- Create a "telegram_bot" folder on disk C (C:\telegram_bot )
- Unzip all the bot files to this folder

3. CREATING A FILE WITH A TOKEN:
   - Open Notepad
- Write: TELEGRAM_BOT_TOKEN=your_token
- Replace "your_token" with the token that BotFather gave you
   - Save the file as ".env" (with a dot at the beginning) in the C folder:\telegram_bot
   - IMPORTANT: When saving, select "File Type: All Files (*.*)" and make sure that the file is not saved as ".env.txt "

4. INSTALLING DEPENDENCIES AND RUNNING:
   - Press Win+R, type "cmd" and press Enter
   - In the command prompt that opens, type:
     cd C:\telegram_bot
     python -m venv venv
     venv\Scripts\activate
     pip install -r requirements.txt
     python bot.py

The bot will start and run while the command prompt is open. To check, find your bot in Telegram and send it the /start command.

5. LAUNCH IN THE FUTURE:
   - To launch the bot next time, just open the command prompt and type:
     cd C:\telegram_bot
     venv\Scripts\activate
     python bot.py

=== INSTALLATION ON LINUX ===

1. INSTALL PYTHON AND NECESSARY PACKAGES:
   Open the terminal and enter:

   For Ubuntu/Debian:
   sudo apt update
   sudo apt install python3.10 python3.10-venv python3-pip git -y

   For CentOS/RHEL:
   sudo yum install python3 python3-pip git -y

2. DOWNLOAD THE BOT FILES:
- Create a folder for the bot:
     mkdir -p ~/telegram_bot
     cd ~/telegram_bot
   
   - Copy all the bot files to this folder

3. CREATING A FILE WITH A TOKEN:
   - Enter in the terminal:
     echo "TELEGRAM_BOT_TOKEN=your_token" > .env

- Replace "your_token" with the token that BotFather gave you

4. CREATE A VIRTUAL ENVIRONMENT AND INSTALL DEPENDENCIES:
- Enter in the terminal:
     cd ~/telegram_bot
     python3 -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt

5. LAUNCHING THE BOT:
- Enter in the terminal:
     python bot.py
   
   The bot will start and run while the terminal is open. To check, find your bot in Telegram and send it the /start command.

6. LAUNCH IN THE FUTURE:
   - To launch the bot next time, open the terminal and enter:
     cd ~/telegram_bot
     source venv/bin/activate
     python bot.py

7. AUTO-START SETTINGS (OPTIONAL):
   If you want the bot to start automatically and work in the background:

   - Create a service file:
     sudo nano /etc/systemd/system/telegram-bot.service

   - Paste it into the file (replace "username" with your username):

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

   - Press Ctrl+O, then Enter to save
- Press Ctrl+X to exit the editor

   - Activate and launch the service:
     sudo systemctl daemon-reload
     sudo systemctl enable telegram-bot.service
     sudo systemctl start telegram-bot.service

   - Check the service status:
     sudo systemctl status telegram-bot.service

=== POSSIBLE PROBLEMS AND THEIR SOLUTIONS ===

1. "pip is not an internal or external command" (Windows):
   - Reinstall Python, making sure to check the "Add Python to PATH" box

2. "Module not found" when launching the bot:
   - Check that you have activated the virtual environment (venv) before launching
- Make sure that you have correctly installed the dependencies: pip install -r requirements.txt

3. The bot does not respond in Telegram:
- Check the token in the .env file
- Make sure that the bot is running (command prompt/terminal are open)
   - Check your internet connection

4. Error "permission denied" (Linux):
- Check access rights: chmod +x bot.py
   - Run with superuser rights: sudo python bot.py

=== USING A BOT ===

After successfully launching the bot, you can use the following commands in Telegram:

/start - get started with the bot
/book - book time
/my_appointings - view your recordings
/cancel - cancel recording

=== ADMINISTRATION ===

To add/change services or work schedules, you need to edit the appointments.db database. This can be done using the SQLite Browser program.:

Windows: https://sqlitebrowser.org/dl/
Linux: sudo apt install sqlitebrowser (for Ubuntu/Debian)

