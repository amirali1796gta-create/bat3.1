import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN=os.getenv("BOT_TOKEN","").strip()
DATABASE_PATH=os.getenv("DATABASE_PATH","data/bot.db")
ADMIN_IDS={int(x) for x in os.getenv("ADMIN_IDS","").split(",") if x.strip().isdigit()}
SUPER_ADMIN_IDS={int(x) for x in os.getenv("SUPER_ADMIN_IDS","").split(",") if x.strip().isdigit()}
LOG_LEVEL=os.getenv("LOG_LEVEL","INFO")
BACKUP_DIR=Path(os.getenv("BACKUP_DIR","backups"))
EXPORT_DIR=Path(os.getenv("EXPORT_DIR","exports"))
if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN is missing")
