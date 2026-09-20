import aiosqlite
from pathlib import Path
from config import DATABASE_PATH
SCHEMA="""
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS feature_flags(key TEXT PRIMARY KEY,name TEXT NOT NULL,enabled INTEGER NOT NULL DEFAULT 1,updated_by INTEGER,updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT,first_name TEXT,last_name TEXT,joined_at TEXT DEFAULT CURRENT_TIMESTAMP,balance REAL DEFAULT 0,is_blocked INTEGER DEFAULT 0,is_reseller INTEGER DEFAULT 0,level TEXT DEFAULT 'normal',referred_by INTEGER,notes TEXT DEFAULT '',tags TEXT DEFAULT '',notification_orders INTEGER DEFAULT 1,notification_payments INTEGER DEFAULT 1,notification_service INTEGER DEFAULT 1,notification_marketing INTEGER DEFAULT 1,notification_support INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS admins(user_id INTEGER PRIMARY KEY,role TEXT DEFAULT 'admin',permissions TEXT DEFAULT '',added_by INTEGER,added_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS audit_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,admin_id INTEGER,action TEXT,target_type TEXT,target_id TEXT,old_value TEXT,new_value TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS categories(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE,active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,code TEXT UNIQUE,name TEXT,description TEXT DEFAULT '',base_price REAL DEFAULT 0,reseller_price REAL,vip_price REAL,campaign_price REAL,volume TEXT DEFAULT '',unit TEXT DEFAULT '',duration TEXT DEFAULT '',server TEXT DEFAULT '',stock INTEGER DEFAULT 0,low_stock_threshold INTEGER DEFAULT 2,active INTEGER DEFAULT 1,pinned INTEGER DEFAULT 0,label TEXT DEFAULT '',created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS product_categories(product_id INTEGER,category_id INTEGER,PRIMARY KEY(product_id,category_id));
CREATE TABLE IF NOT EXISTS product_links(id INTEGER PRIMARY KEY AUTOINCREMENT,product_id INTEGER,title TEXT,url TEXT,active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS payment_cards(id INTEGER PRIMARY KEY AUTOINCREMENT,card_number TEXT,owner TEXT,active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,order_no TEXT UNIQUE,user_id INTEGER,product_id INTEGER,price REAL,discount REAL DEFAULT 0,final_price REAL,payment_method TEXT DEFAULT 'card',status TEXT DEFAULT 'pending_payment',payment_card_id INTEGER,recipient_user_id INTEGER,referral_user_id INTEGER,reseller_id INTEGER,idempotency_key TEXT UNIQUE,created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS order_history(id INTEGER PRIMARY KEY AUTOINCREMENT,order_id INTEGER,status TEXT,note TEXT DEFAULT '',actor_id INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS services(id INTEGER PRIMARY KEY AUTOINCREMENT,service_id TEXT UNIQUE,order_id INTEGER,user_id INTEGER,product_id INTEGER,config TEXT DEFAULT '',status TEXT DEFAULT 'active',server TEXT DEFAULT '',volume TEXT DEFAULT '',unit TEXT DEFAULT '',duration TEXT DEFAULT '',expires_at TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS discount_codes(id INTEGER PRIMARY KEY AUTOINCREMENT,code TEXT UNIQUE,percent REAL,max_uses INTEGER DEFAULT 1,used_count INTEGER DEFAULT 0,expires_at TEXT,active INTEGER DEFAULT 1,scope TEXT DEFAULT 'all',scope_ids TEXT DEFAULT '',campaign_id INTEGER);
CREATE TABLE IF NOT EXISTS discount_usages(id INTEGER PRIMARY KEY AUTOINCREMENT,code_id INTEGER,user_id INTEGER,order_id INTEGER,used_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(code_id,user_id,order_id));
CREATE TABLE IF NOT EXISTS campaigns(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,message TEXT DEFAULT '',percent REAL,start_at TEXT,end_at TEXT,max_uses INTEGER DEFAULT 0,active INTEGER DEFAULT 1,scope TEXT DEFAULT 'all',scope_ids TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS referrals(id INTEGER PRIMARY KEY AUTOINCREMENT,inviter_id INTEGER,invited_id INTEGER UNIQUE,created_at TEXT DEFAULT CURRENT_TIMESTAMP,locked INTEGER DEFAULT 1,reward REAL DEFAULT 0);
CREATE TABLE IF NOT EXISTS reseller_requests(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,status TEXT DEFAULT 'pending',created_at TEXT DEFAULT CURRENT_TIMESTAMP,reviewed_by INTEGER,reviewed_at TEXT);
CREATE TABLE IF NOT EXISTS withdrawals(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,amount REAL,destination TEXT,status TEXT DEFAULT 'pending',created_at TEXT DEFAULT CURRENT_TIMESTAMP,reviewed_by INTEGER,reviewed_at TEXT);
CREATE TABLE IF NOT EXISTS wallet_transactions(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,amount REAL,type TEXT,reference TEXT,note TEXT DEFAULT '',created_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(user_id,type,reference));
CREATE TABLE IF NOT EXISTS gift_cards(id INTEGER PRIMARY KEY AUTOINCREMENT,code TEXT UNIQUE,amount REAL,max_uses INTEGER DEFAULT 1,used_count INTEGER DEFAULT 0,expires_at TEXT,active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS tutorials(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,category TEXT DEFAULT 'common',link TEXT,description TEXT DEFAULT '',sort_order INTEGER DEFAULT 0,active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY AUTOINCREMENT,ticket_no TEXT UNIQUE,user_id INTEGER,subject TEXT,status TEXT DEFAULT 'open',created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS ticket_messages(id INTEGER PRIMARY KEY AUTOINCREMENT,ticket_id INTEGER,sender_id INTEGER,message TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS favorites(user_id INTEGER,product_id INTEGER,PRIMARY KEY(user_id,product_id));
CREATE TABLE IF NOT EXISTS notification_events(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,event_type TEXT,message TEXT,sent INTEGER DEFAULT 0,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS system_idempotency(key TEXT PRIMARY KEY,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""
FEATURES=[('shop','فروشگاه'),('wallet','کیف پول'),('payments','پرداخت'),('discounts','تخفیف'),('reseller','نمایندگی'),('referrals','دعوت دوستان'),('tutorials','آموزش'),('tickets','پشتیبانی'),('broadcast','همگانی'),('gift_cards','گیفت کارت'),('gifts','هدیه سرویس'),('analytics','گزارش‌ها'),('excel','اکسل'),('backup','پشتیبان‌گیری'),('maintenance','حالت تعمیر'),('service_suspend','تعلیق سرویس'),('auto_renew','تمدید خودکار'),('favorites','علاقه‌مندی'),('campaigns','کمپین فروش')]
async def connect():
 Path(DATABASE_PATH).parent.mkdir(parents=True,exist_ok=True)
 db=await aiosqlite.connect(DATABASE_PATH); db.row_factory=aiosqlite.Row; await db.executescript(SCHEMA)
 for k,n in FEATURES: await db.execute('INSERT OR IGNORE INTO feature_flags(key,name) VALUES(?,?)',(k,n))
 await db.commit(); return db
