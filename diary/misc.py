from diary import db,LOGGER
from config import OWNER_ID,SUDOERS
from pyrogram import Client
async def sudo():
    global SUDOERS
    SUDOERS.add(OWNER_ID)
    sudoersdb = db.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers = [] if not sudoers else sudoers["sudoers"]
    if OWNER_ID not in sudoers:
        sudoers.append(OWNER_ID)
        await sudoersdb.update_one(
            {"sudo": "sudo"},
            {"$set": {"sudoers": sudoers}},
            upsert=True,
        )
    if sudoers:
        for user_id in sudoers:
            SUDOERS.add(user_id)
            
         