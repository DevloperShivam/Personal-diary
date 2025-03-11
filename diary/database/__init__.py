import re
import bcrypt
from .. import db, LOGGER
from datetime import datetime
import pytz  

IST = pytz.timezone("Asia/Kolkata") 

# ✅ Databases
users_db = db.users_db  # ✅ Fully registered users
pending_users_db = db.pending_users  # ✅ Users who started but haven't registered
login_db = db.login_db  # ✅ Multiple login sessions
sudoers_db = db.sudoers  # ✅ Admin users

### 🔹 Hash & Verify Password
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

### 🔹 Sudo Users Management
async def get_sudoers() -> list:
    sudoers = await sudoers_db.find_one({"sudo": "sudo"})
    return sudoers["sudoers"] if sudoers else []

async def add_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    if user_id not in sudoers:
        sudoers.append(user_id)
        await sudoers_db.update_one({"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True)
    return True

async def remove_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    if user_id in sudoers:
        sudoers.remove(user_id)
        await sudoers_db.update_one({"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True)
    return True

### 🔹 Check If User is Registered
async def is_registered_user(username: str) -> bool:
    """✅ Checks if a username is already registered"""
    user = await users_db.find_one({"username": username})
    return user is not None

async def is_registered_by_id(telegram_id: int) -> bool:
    """✅ Checks if a Telegram user ID is already registered"""
    user = await users_db.find_one({"telegram_id": telegram_id})
    return user is not None

async def get_user_by_username(username: str):
    """✅ Get user details by username"""
    return await users_db.find_one({"username": username})

async def get_user_by_id(telegram_id: int):
    """✅ Get user details by Telegram ID"""
    return await users_db.find_one({"telegram_id": telegram_id})


### 🔹 Save User When They Start the Bot
async def add_pending_user(user_id):
    """✅ Save user entry when they start the bot (before registration)"""
    user_exists = await pending_users_db.find_one({"telegram_id": user_id})
    
    if not user_exists:
        current_time_utc = datetime.utcnow()
        current_time_ist = current_time_utc.astimezone(IST)

        new_user = {
            "telegram_id": user_id,  
            "registered_at": str(current_time_ist.strftime("%d-%m-%Y %I:%M %p"))
        }
        await pending_users_db.insert_one(new_user)  # ✅ Save in pending_users_db
        return True
    return False


### 🔹 Save Login Sessions for Multiple Accounts
async def save_login_session(user_id, username, password):
    """✅ Save additional login session"""
    hashed_password = hash_password(password)
    await login_db.insert_one({
        "telegram_id": user_id,
        "username": username,
        "password": hashed_password
    })

### 🔹 Fetch All Registered Users
async def get_all_registered_users():
    """✅ Fetch all registered users"""
    cursor = users_db.find({}, {"_id": 0, "username": 1})
    return [doc["username"] async for doc in cursor]

### 🔹 Fetch Login Data by Username
async def get_login_data(username):
    """✅ Get login credentials for a username"""
    return await login_db.find_one({"username": username})

### 🔹 Delete a User from Database
async def delete_user(filter_query):
    """✅ Delete a user from the registered users database"""
    try:
        result = await users_db.delete_one(filter_query)
        if result.deleted_count:
            LOGGER.info("✅ User deleted successfully.")
        else:
            LOGGER.info("❌ No user found to delete.")
    except Exception as e:
        LOGGER.error(f"⚠️ Error deleting user: {e}")
