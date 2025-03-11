from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient

from config import *
import logging

# Logging Configuration
logging.basicConfig(
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

LOGGER = logging.getLogger(__name__)

# Initialize MongoDB connection
mongo_client = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo_client.diarybot  

class Diary(Client):
    def __init__(self):
        super().__init__(
            name="DiaryBot",
            api_id=API_ID,
            api_hash=API_HASH,
            lang_code="en",
            bot_token=BOT_TOKEN,
            in_memory=True,
        )
        self.user_data = {}  

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

    async def stop(self):
        await super().stop()


DiaryBot = Diary()  
HELPABLE = {}
