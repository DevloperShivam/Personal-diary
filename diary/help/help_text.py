# Help texts for all events!!
# Welcome message and keyboard layout
from pyexpat.errors import messages

WELCOME_MESSAGE ="""<b>Hey {0}, 
welcome to the​ <a href="https://telegram.me/{1}">Diary bot​</a> !</b>

"""

AUTH_MESSAGE= """<b>Hey {0}, 
welcome to the​ <a href="https://telegram.me/{1}">Diary bot​</a> !</b>

Please Register or login you account . 

"""

REGISTRATION_TEXTS = {
    "username": "📝 Please enter a **username** (No spaces):",
    "nickname": "😊 Enter your **nickname** (No spaces):",
    "password": "🔒 Enter a **password** (Min 8 characters, 1 special character, No spaces):",
    "email": "📧 Enter your **backup email** (Gmail, Hotmail, Outlook only, No spaces):",
}

LOGIN_TEXTS = {
    "username": "🔑 Please enter your **username**:",
    "password": "🔑 Now enter your **password**:",
}
