from app.database.db import connect
async def add(uid,role,permissions,actor):
 db=await connect(); await db.execute("INSERT INTO admins(user_id,role,permissions,added_by) VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET role=excluded.role,permissions=excluded.permissions",(uid,role,','.join(permissions),actor)); await db.commit(); await db.close()
async def remove(uid):
 db=await connect(); r=await (await db.execute('SELECT role FROM admins WHERE user_id=?',(uid,))).fetchone()
 if not r: await db.close(); return False
 if r['role']=='super_admin' and (await (await db.execute("SELECT COUNT(*) n FROM admins WHERE role='super_admin'")).fetchone())['n']<=1: await db.close(); return False
 await db.execute('DELETE FROM admins WHERE user_id=?',(uid,)); await db.commit(); await db.close(); return True
