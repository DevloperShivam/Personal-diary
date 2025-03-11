import re
import asyncio
from diary import DiaryBot
from pyrogram import filters
from diary.help import WELCOME_MESSAGE, AUTH_MESSAGE, REGISTRATION_TEXTS, LOGIN_TEXTS
from diary.inline import START_KEYBOARD, AUTH_BUTTONS, CONFIRM_CANCEL_BUTTONS
from config import START_IMG, STEP_IMAGES, AUTH_IMG
from diary.database import db, add_pending_user, get_login_data, check_password, save_login_session, login_db, users_db
from diary.modules.auth import login_user, register_user
from pyrogram.types import CallbackQuery, Message
import bcrypt

if not hasattr(DiaryBot, "user_data"):
    DiaryBot.user_data = {}

# Password Strength
def is_valid_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password) and
        " " not in password
    )

# Confirmation Texts 
CONFIRMATION_TEXTS = {
    "register": (
        "**📝 Registration Details**\n\n"
        "Please confirm your details before proceeding:\n\n"
        "👤 **Username:** {username}\n"
        "🆔 **Telegram ID:** {user_id}\n"
        "📛 **Nickname:** {nickname}\n"
        "🔐 **Password:** ||{password}||\n"
        "📧 **Email:** {email}\n\n"
        "Click **Confirm** to complete registration or **Cancel** to start over."
    ),
    "login": (
        "**🔑 Login Details**\n\n"
        "Please confirm your details before proceeding:\n\n"
        "👤 **Username:** {username}\n"
        "🆔 **Telegram ID:** {user_id}\n"
        "🔐 **Password:** ||{password}||\n\n"
        "Click **Confirm** to log in or **Cancel** to start over."
    )
}

async def delete_message_after_delay(message, delay=30):
    """Delete a message after a specified delay."""
    await asyncio.sleep(delay)
    await message.delete()

@DiaryBot.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    """✅ Show login/register UI when user starts"""
    
    user_id = message.from_user.id
    await add_pending_user(user_id)  

    user = await users_db.find_one({"telegram_id": user_id})

    if not user:
        bot_msg = await message.reply_photo(
            photo=START_IMG,
            caption=AUTH_MESSAGE.format(message.from_user.mention, DiaryBot.username),
            reply_markup=AUTH_BUTTONS
        )

        DiaryBot.user_data[user_id] = {"bot_msg": bot_msg.id}
        return

    # ✅ Show main page after successful login/registration
    await message.reply_photo(
        photo=START_IMG,
        caption=WELCOME_MESSAGE.format(message.from_user.mention, DiaryBot.username),
        reply_markup=START_KEYBOARD
    )

@DiaryBot.on_callback_query(filters.regex("register"))
async def register(client, callback_query: CallbackQuery):
    """✅ Start registration process"""
    user_id = callback_query.from_user.id
    user = await db.users_db.find_one({"telegram_id": user_id})

    if user:
        await callback_query.answer("❗ You are already registered!", show_alert=True)
        return

    # Schedule the message for deletion after 30 seconds
    asyncio.create_task(delete_message_after_delay(callback_query.message))

    await callback_query.message.reply_photo(
        photo=STEP_IMAGES["username"],
        caption=REGISTRATION_TEXTS["username"]
    )
    DiaryBot.user_data[user_id] = {"step": "username"}

@DiaryBot.on_callback_query(filters.regex("login"))
async def login(client, callback_query: CallbackQuery):
    """✅ Start login process"""
    # Schedule the message for deletion after 30 seconds
    asyncio.create_task(delete_message_after_delay(callback_query.message))

    await callback_query.message.reply_photo(
        photo=STEP_IMAGES["login_username"],
        caption=LOGIN_TEXTS["username"]
    )
    DiaryBot.user_data[callback_query.from_user.id] = {"step": "login_username"}

@DiaryBot.on_message(filters.text & filters.private)
async def handle_messages(client, message: Message):
    """✅ Handle both registration and login messages"""
    user_id = message.from_user.id

    if user_id not in DiaryBot.user_data:
        return  

    step = DiaryBot.user_data[user_id].get("step")

    if step and step.startswith("login_"):
        await handle_login(client, message)
    elif step and step in ["username", "nickname", "password", "email"]:
        await handle_registration(client, message)
    else:
        await message.reply_text("❌ An unexpected error occurred. Please try again.", quote=True)
        del DiaryBot.user_data[user_id]

async def handle_login(client, message: Message):
    """✅ Handles user login process"""
    user_id = message.from_user.id

    if user_id not in DiaryBot.user_data:
        return

    step = DiaryBot.user_data[user_id]["step"]

    if step == "login_username":
        username = message.text.strip()

        user = await login_db.find_one({"username": username})

        if not user:
            await message.reply_text("❗ Username not found! Please check or register first.")
            del DiaryBot.user_data[user_id]
            return

        DiaryBot.user_data[user_id]["username"] = username
        DiaryBot.user_data[user_id]["step"] = "login_password"
        await message.reply_photo(
            photo=STEP_IMAGES["login_password"],
            caption=LOGIN_TEXTS["password"]
        )
        await message.delete()  

    elif step == "login_password":
        password = message.text.strip()
        username = DiaryBot.user_data[user_id]["username"]

        user = await login_db.find_one({"username": username})

        if not user:
            await message.reply_text("❌ An unexpected error occurred. Try again.")
            del DiaryBot.user_data[user_id]
            return

        if not check_password(password, user["password"]):
            await message.reply_text("❌ Incorrect password! Try again.")
            return

        DiaryBot.user_data[user_id]["password"] = password  

        confirmation_text = CONFIRMATION_TEXTS["login"].format(
            username=username,
            user_id=user_id
        )
        await message.reply_photo(
            photo=STEP_IMAGES["login_password"],
            caption=confirmation_text,
            reply_markup=CONFIRM_CANCEL_BUTTONS
        )
        DiaryBot.user_data[user_id]["step"] = "login_confirm"
        await message.delete()  

async def handle_registration(client, message: Message):
    """✅ Handle step-by-step registration"""
    user_id = message.from_user.id

    if user_id not in DiaryBot.user_data:
        return

    step = DiaryBot.user_data[user_id]["step"]

    if step == "username":
        if " " in message.text:
            await message.reply_text("❗ Username **cannot contain spaces**. Try again.")
            return

        existing_user = await db.users_db.find_one({"username": message.text})
        if existing_user:
            await message.reply_text("❗ This username is already taken. Try another.")
            del DiaryBot.user_data[user_id]
            return

        DiaryBot.user_data[user_id]["username"] = message.text
        DiaryBot.user_data[user_id]["step"] = "nickname"
        await message.reply_photo(
            photo=STEP_IMAGES["nickname"],
            caption=REGISTRATION_TEXTS["nickname"]
        )
        await message.delete()  

    elif step == "nickname":
        if " " in message.text:
            await message.reply_text("❗ Nickname **cannot contain spaces**. Try again.")
            return

        DiaryBot.user_data[user_id]["nickname"] = message.text
        DiaryBot.user_data[user_id]["step"] = "password"
        await message.reply_photo(
            photo=STEP_IMAGES["password"],
            caption=REGISTRATION_TEXTS["password"]
        )
        await message.delete()  

    elif step == "password":
        if not is_valid_password(message.text):
            await message.reply_text("❗ Password must be **at least 8 characters** long and contain **at least 1 special character** (No spaces). Try again.")
            return

        DiaryBot.user_data[user_id]["password"] = message.text
        DiaryBot.user_data[user_id]["step"] = "email"
        await message.reply_photo(
            photo=STEP_IMAGES["email"],
            caption=REGISTRATION_TEXTS["email"]
        )
        await message.delete()  

    elif step == "email":
        if " " in message.text or not re.match(r"^[a-zA-Z0-9._%+-]+@(gmail|hotmail|outlook)\.com$", message.text):
            await message.reply_text("❗ Invalid email. Only Gmail, Hotmail, and Outlook are allowed (No spaces). Try again.")
            return

        email = message.text.strip()  #
        DiaryBot.user_data[user_id]["email"] = email  

        # ✅ Get All User Data for Confirmation
        username = DiaryBot.user_data[user_id]["username"]
        password = DiaryBot.user_data[user_id]["password"]
        nickname = DiaryBot.user_data[user_id]["nickname"]

        print(f"✅ Email Captured: {email} for Username: {username}")  

        # ✅ Show Confirmation Page Before Registering
        confirmation_text = CONFIRMATION_TEXTS["register"].format(
            username=username,
            user_id=user_id,
            nickname=nickname,
            password=password,
            email=email  
        )
        await message.reply_photo(
            photo=STEP_IMAGES["email"],
            caption=confirmation_text,
            reply_markup=CONFIRM_CANCEL_BUTTONS
        )
        DiaryBot.user_data[user_id]["step"] = "register_confirm"
        await message.delete()  #


@DiaryBot.on_callback_query(filters.regex("confirm"))
async def confirm_action(client, callback_query: CallbackQuery):
    """✅ Handle confirmation for login/register"""
    user_id = callback_query.from_user.id

    if user_id not in DiaryBot.user_data:
        await callback_query.answer("❌ No active session found. Please start again.", show_alert=True)
        return

    step = DiaryBot.user_data[user_id]["step"]

    if step == "login_confirm":
        username = DiaryBot.user_data[user_id]["username"]
        entered_password = DiaryBot.user_data[user_id]["password"]  

        user_data = await db.login_db.find_one({"username": username})

        if not user_data:
            await callback_query.answer("❌ User not found. Please register.", show_alert=True)
            return

        stored_hashed_password = user_data.get("password")  

        # ✅ Verify Password with Hash (Corrected)
        if bcrypt.checkpw(entered_password.encode("utf-8"), stored_hashed_password.encode("utf-8")):
            await save_login_session(user_id, username, stored_hashed_password)  

            await callback_query.answer(f"✅ Welcome back, {username}!", show_alert=True)


            await callback_query.message.delete()
            await start_command(client, callback_query.message)
        else:
            await callback_query.answer("❌ Incorrect password. Please try again.", show_alert=True)
            return

        stored_hashed_password = user_data.get("password")  

        if bcrypt.checkpw(entered_password.encode("utf-8"), stored_hashed_password.encode("utf-8")):
            await save_login_session(user_id, username, stored_hashed_password)  

            await callback_query.answer(f"✅ Welcome back, {username}!", show_alert=True)

            await callback_query.message.delete()

            await start_command(client, callback_query.message)
        else:
            await callback_query.answer("❌ Incorrect password. Please try again.", show_alert=True)

    elif step == "register_confirm":
        username = DiaryBot.user_data[user_id]["username"]
        entered_password = DiaryBot.user_data[user_id]["password"]
        nickname = DiaryBot.user_data[user_id]["nickname"]
        email = DiaryBot.user_data[user_id].get("email") 

        # Hash the password before storing
        hashed_password = bcrypt.hashpw(entered_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")  

        # Check if the user already exists in users_db
        existing_user = await db.users_db.find_one({"username": username})
        if existing_user:
            await callback_query.answer("❌ User already exists. Please log in.", show_alert=True)
            return

        success, response = await register_user(user_id, username, hashed_password, email, nickname)

        if success:
            await callback_query.answer(f"✅ Welcome, {nickname}!", show_alert=True)

            await callback_query.message.delete()

            await start_command(client, callback_query.message)
        else:
            await callback_query.answer(response, show_alert=True)

    del DiaryBot.user_data[user_id]

@DiaryBot.on_callback_query(filters.regex("cancel"))
async def cancel_action(client, callback_query: CallbackQuery):
    """✅ Handle cancellation for login/register"""
    user_id = callback_query.from_user.id

    if user_id in DiaryBot.user_data:
        del DiaryBot.user_data[user_id] 

    await callback_query.answer("❌ Action canceled.", show_alert=True)

    await callback_query.message.delete()

    await callback_query.message.reply_photo(
        photo=AUTH_IMG,
        caption=AUTH_MESSAGE.format(callback_query.from_user.mention, DiaryBot.username),
        reply_markup=AUTH_BUTTONS
    )