import shutil
from datetime import datetime
from config import DATABASE_PATH,BACKUP_DIR
def backup():
 BACKUP_DIR.mkdir(parents=True,exist_ok=True); p=BACKUP_DIR/f'bot_{datetime.now():%Y%m%d_%H%M%S}.db'; shutil.copy2(DATABASE_PATH,p); return p
