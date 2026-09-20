import logging
from aiogram import Bot,Dispatcher
from config import BOT_TOKEN,ADMIN_IDS,SUPER_ADMIN_IDS,LOG_LEVEL
from app.database.db import connect
from app.services.core import seed
from app.handlers.start import r as start
from app.handlers.shop import r as shop
from app.handlers.admin import r as admin
from app.handlers.misc import r as misc
async def run():
 logging.basicConfig(level=getattr(logging,LOG_LEVEL,logging.INFO),format='%(asctime)s | %(levelname)s | %(message)s')
 await connect(); await seed(ADMIN_IDS,SUPER_ADMIN_IDS)
 bot=Bot(BOT_TOKEN); dp=Dispatcher(); dp.include_router(start); dp.include_router(shop); dp.include_router(admin); dp.include_router(misc); await dp.start_polling(bot)
