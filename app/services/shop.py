from app.database.db import connect
from app.services.core import order_no,service_no
async def categories():
 db=await connect(); r=await (await db.execute('SELECT * FROM categories WHERE active=1 ORDER BY name')).fetchall(); await db.close(); return r
async def products(cid=None):
 db=await connect()
 q='SELECT p.* FROM products p JOIN product_categories pc ON pc.product_id=p.id WHERE p.active=1 AND pc.category_id=? ORDER BY p.pinned DESC,p.id DESC' if cid else 'SELECT * FROM products WHERE active=1 ORDER BY pinned DESC,id DESC'
 r=await (await db.execute(q,(cid,) if cid else ())).fetchall(); await db.close(); return r
async def get_product(pid):
 db=await connect(); r=await (await db.execute('SELECT * FROM products WHERE id=?',(pid,))).fetchone(); await db.close(); return r
async def price(p,u):
 if u['is_reseller'] and p['reseller_price'] is not None:return p['reseller_price']
 if u['level']=='vip' and p['vip_price'] is not None:return p['vip_price']
 return p['campaign_price'] if p['campaign_price'] is not None else p['base_price']
async def create_order(uid,pid,recipient=None,discount=0,key=None):
 db=await connect(); p=await (await db.execute('SELECT * FROM products WHERE id=? AND active=1',(pid,))).fetchone(); u=await (await db.execute('SELECT * FROM users WHERE id=?',(uid,))).fetchone()
 if not p or p['stock']<=0: await db.close(); raise ValueError('محصول موجود نیست')
 if key:
  old=await (await db.execute('SELECT id FROM orders WHERE idempotency_key=?',(key,))).fetchone()
  if old: await db.close(); return old['id']
 pr=float(await price(p,u)); final=max(0,pr-float(discount)); no=order_no()
 cur=await db.execute('INSERT INTO orders(order_no,user_id,product_id,price,discount,final_price,recipient_user_id,idempotency_key) VALUES(?,?,?,?,?,?,?,?)',(no,uid,pid,pr,discount,final,recipient,key)); oid=cur.lastrowid
 await db.execute('INSERT INTO order_history(order_id,status,note,actor_id) VALUES(?,?,?,?)',(oid,'pending_payment','سفارش ایجاد شد',uid)); await db.commit(); await db.close(); return oid
async def approve(oid,admin):
 db=await connect(); o=await (await db.execute('SELECT * FROM orders WHERE id=?',(oid,))).fetchone(); p=await (await db.execute('SELECT * FROM products WHERE id=?',(o['product_id'],))).fetchone() if o else None
 if not o or o['status']=='paid': await db.close(); return None
 if p['stock']<=0: await db.close(); raise ValueError('موجودی تمام شده')
 await db.execute('UPDATE products SET stock=stock-1,active=CASE WHEN stock-1<=0 THEN 0 ELSE active END WHERE id=?',(p['id'],))
 await db.execute("UPDATE orders SET status='paid',updated_at=CURRENT_TIMESTAMP WHERE id=?",(oid,)); await db.execute('INSERT INTO order_history(order_id,status,note,actor_id) VALUES(?,?,?,?)',(oid,'paid','پرداخت تأیید شد',admin))
 sid=service_no(); uid=o['recipient_user_id'] or o['user_id']
 await db.execute('INSERT INTO services(service_id,order_id,user_id,product_id,status,server,volume,unit,duration) VALUES(?,?,?,?,?,?,?,?,?)',(sid,oid,uid,p['id'],'active',p['server'],p['volume'],p['unit'],p['duration']))
 await db.commit(); await db.close(); return sid
async def reject(oid,admin,note=''):
 db=await connect(); await db.execute("UPDATE orders SET status='rejected',updated_at=CURRENT_TIMESTAMP WHERE id=?",(oid,)); await db.execute('INSERT INTO order_history(order_id,status,note,actor_id) VALUES(?,?,?,?)',(oid,'rejected',note,admin)); await db.commit(); await db.close()
