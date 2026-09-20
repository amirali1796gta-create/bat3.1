import secrets,string
from datetime import datetime
from app.database.db import connect
def token(n=8): return ''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(n))
def money(x): return f"{float(x):,.0f}"
def order_no(): return 'ORD-'+datetime.now().strftime('%y%m%d%H%M%S')+'-'+token(4)
def service_no(): return 'SVC-'+datetime.now().strftime('%y%m%d')+'-'+token(7)
async def ensure_user(tg):
 db=await connect(); await db.execute('INSERT INTO users(id,username,first_name,last_name) VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET username=excluded.username,first_name=excluded.first_name,last_name=excluded.last_name',(tg.id,tg.username,tg.first_name,tg.last_name)); await db.commit(); await db.close()
async def user(uid):
 db=await connect(); r=await (await db.execute('SELECT * FROM users WHERE id=?',(uid,))).fetchone(); await db.close(); return r
async def is_admin(uid):
 db=await connect(); r=await (await db.execute('SELECT role FROM admins WHERE user_id=?',(uid,))).fetchone(); await db.close(); return r is not None
async def is_super(uid):
 db=await connect(); r=await (await db.execute('SELECT role FROM admins WHERE user_id=?',(uid,))).fetchone(); await db.close(); return bool(r and r['role']=='super_admin')
async def perm(uid,p):
 if await is_super(uid): return True
 db=await connect(); r=await (await db.execute('SELECT permissions FROM admins WHERE user_id=?',(uid,))).fetchone(); await db.close(); return bool(r and (p in r['permissions'].split(',') or '*' in r['permissions']))
async def audit(uid,action,target='',tid='',old='',new=''):
 db=await connect(); await db.execute('INSERT INTO audit_logs(admin_id,action,target_type,target_id,old_value,new_value) VALUES(?,?,?,?,?,?)',(uid,action,target,str(tid),str(old),str(new))); await db.commit(); await db.close()
async def seed(admins,supers):
 db=await connect()
 for uid in admins: await db.execute("INSERT OR IGNORE INTO admins(user_id,role,permissions) VALUES(?,?,?)",(uid,'admin','users,products,orders,payments,discounts,resellers,tickets,broadcast,analytics,excel'))
 for uid in supers: await db.execute("INSERT INTO admins(user_id,role,permissions) VALUES(?,?,?) ON CONFLICT(user_id) DO UPDATE SET role='super_admin',permissions='*'",(uid,'super_admin','*'))
 await db.commit(); await db.close()
