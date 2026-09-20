from app.database.db import connect
from app.services.core import token
async def create(percent,count=1,max_uses=1):
 db=await connect(); out=[]
 for _ in range(count):
  c=token(10); await db.execute('INSERT INTO discount_codes(code,percent,max_uses) VALUES(?,?,?)',(c,percent,max_uses)); out.append(c)
 await db.commit(); await db.close(); return out
async def validate(code,uid,pid=None):
 db=await connect(); r=await (await db.execute('SELECT * FROM discount_codes WHERE code=? AND active=1',(code.upper(),))).fetchone()
 if not r: await db.close(); return None,'کد نامعتبر'
 if r['used_count']>=r['max_uses']: await db.close(); return None,'ظرفیت کد تمام شده'
 old=await (await db.execute('SELECT id FROM discount_usages WHERE code_id=? AND user_id=?',(r['id'],uid))).fetchone()
 if old: await db.close(); return None,'قبلاً استفاده شده'
 await db.close(); return r,None
