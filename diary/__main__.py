import asyncio
import importlib
from pyrogram import idle
from diary.misc import sudo
from diary import LOGGER, DiaryBot,HELPABLE
from diary.modules import ALL_MODULES
from pyrogram.types import BotCommand
async def diary_start():
    try:

        await sudo()
        await DiaryBot.start()
    except Exception as ex:
        LOGGER.error(ex)
        quit(1)
    
    for all_module in ALL_MODULES:
        imported_module=importlib.import_module("diary.modules." + all_module)
        if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
            imported_module.__MODULE__ = imported_module.__MODULE__
            if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
                HELPABLE[imported_module.__MODULE__.lower()] = imported_module
    LOGGER.info(ALL_MODULES)
    LOGGER.info(f"@{DiaryBot.username} Started.")

    await DiaryBot.set_bot_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("verify", "login / register"),
        BotCommand("addpage","add your diary pages"),
        BotCommand("getpages", "find you diary pages")
    ])

    await idle()


if __name__ == "__main__":
    
    asyncio.get_event_loop().run_until_complete(diary_start())
    
    LOGGER.info("Stopping Diary ")
    