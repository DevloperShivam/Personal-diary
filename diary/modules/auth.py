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
    """✅ Hashes a password before storing"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def check_password(password, hashed_password):
    """✅ Checks a plain password against a stored hashed password"""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

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

### 🔹 Register User in `users_db` & Save Login in `login_db`
async def register_user(user_id, username, password, email, nickname):
    """✅ Registers a new user & stores login details"""
    existing_user = await users_db.find_one({"username": username})

    if existing_user:
        return False, "❌ Username already exists! Try another."

    # Hash the password before saving
    hashed_password = hash_password(password)  

    # ✅ Save User Profile in `users_db`
    new_user = {
        "telegram_id": user_id,
        "username": username,
        "email": email,
        "nickname": nickname,
        "total_pages": 0,
        "registered_at": datetime.utcnow().astimezone(IST).strftime("%d-%m-%Y %I:%M %p")
    }
    await users_db.insert_one(new_user)  # ✅ Save in `users_db`

    # ✅ Save Login Data in `login_db` with hashed password
    await login_db.insert_one({
           "telegram_id": user_id,
           "username": username,
           "password": hashed_password, 
           "email": email
       })

    return True, "✅ Registration successful!"

### 🔹 Login User by Checking Password
async def login_user(username, password):
    """✅ Checks username & verifies hashed password"""
    user = await login_db.find_one({"username": username})

    if not user:
        return False, "❌ Username not found!"

    if not check_password(password, user["password"]):
        return False, "❌ Incorrect password! Try again."

    return True, user["telegram_id"]

