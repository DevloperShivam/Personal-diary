from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Login / register buttons
AUTH_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("📝 Register", callback_data="register")],
    [InlineKeyboardButton("🔑 Login", callback_data="login")]
])

# Start buttons
START_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("📝 Add pages", callback_data="add_pages")],
    [
        InlineKeyboardButton("📖 My Diary", callback_data="my_diary"),
        InlineKeyboardButton("owner", user_id=7234206438)
    ],
])

CONFIRM_CANCEL_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("confirm", callback_data="confirm")],
    [InlineKeyboardButton("cancel", callback_data="cancel")]
])