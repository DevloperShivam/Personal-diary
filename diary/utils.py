from functools import wraps
from diary.database import get_sudoers 
from config import OWNER_ID

def is_user_free(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        return await func(client, message, *args, **kwargs)
    return wrapper

def sudoers_only(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        user_id = message.from_user.id
        sudoers = await get_sudoers()  # Fetch list of sudoers from DB

        if user_id not in sudoers:
            await message.reply_text("This command is only available to bot admins.")
            return
        
        return await func(client, message, *args, **kwargs)
    
    return wrapper
