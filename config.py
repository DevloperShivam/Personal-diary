from os import environ
from pyrogram import filters

API_ID=int(environ.get("API_ID",28600524))
API_HASH=environ.get("API_HASH","64e338b41fbcf80d6ad1dc0ec2d4aa64")
BOT_TOKEN=environ.get("BOT_TOKEN","8106756124:AAGO7oHo7X_Zmq-8XhuEmJrr-L1N3yiWeB0")
MONGO_DB_URI=environ.get("MONGO_DB_URI","mongodb+srv://Shivam00:yMX7zaq9AR7DIDbT@testing.hqmpz.mongodb.net/?retryWrites=true&w=majority&appName=testing")
OWNER_ID=int(environ.get("OWNER_ID",7234206438))
SUDOERS=filters.user()
SUDOERS.add(OWNER_ID) 
SUPPORT_GRP =environ.get("SUPPORT_GRP", "kycsellsofficial")
LOG_ID=environ.get("LOG_ID",-1002278232887)
DATA_CHANNEL=environ.get("DATA_CHANNEL",-1002278232887)

# Images 

AUTH_IMG=environ.get("AUTH_IMG","https://i.imghippo.com/files/lOv4210co.jpg")
START_IMG=environ.get("START_IMG","https://i.imghippo.com/files/lOv4210co.jpg")

STEP_IMAGES = {
    "username": "https://i.imghippo.com/files/lOv4210co.jpg",
    "password": "https://i.imghippo.com/files/lOv4210co.jpg",
    "nickname": "https://i.imghippo.com/files/lOv4210co.jpg",
    "email": "https://i.imghippo.com/files/lOv4210co.jpg",
    "login_username": "https://i.imghippo.com/files/lOv4210co.jpg",
    "login_password": "https://i.imghippo.com/files/lOv4210co.jpg",
}

