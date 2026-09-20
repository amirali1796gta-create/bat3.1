from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import Message,CallbackQuery,InlineKeyboardMarkup,InlineKeyboardButton,FSInputFile
from app.services.core import is_admin,is_super,perm,audit
from app.database.db import connect
from app.keyboards.main import admin as ak
from app.services.backup import backup
r=Router()
@r.message(Command('admin'))
async def panel(m:Message):
 if not await is_admin(m.from_user.id): return await m.answer('دسترسی ندارید.')
 await m.answer('🛡 پنل Super Admin / مدیریت\nFeature Manager و زیرساخت کامل فعال است.',reply_markup=ak())
@r.message(F.text=='⚙️ Feature Manager')
async def fm(m:Message):
 if not await is_super(m.from_user.id): return await m.answer('فقط Super Admin')
 db=await connect(); rows=await (await db.execute('SELECT * FROM feature_flags ORDER BY name')).fetchall(); await db.close(); kb=[[InlineKeyboardButton(text=('🟢 ' if x['enabled'] else '🔴 ')+x['name'],callback_data='feat:'+x['key'])] for x in rows]; await m.answer('⚙️ Feature Manager\nقابلیت‌ها مستقل خاموش/روشن می‌شوند.',reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
@r.callback_query(F.data.startswith('feat:'))
async def toggle(c:CallbackQuery):
 if not await is_super(c.from_user.id): return await c.answer('فقط Super Admin',show_alert=True)
 k=c.data[5:]; db=await connect(); x=await (await db.execute('SELECT enabled FROM feature_flags WHERE key=?',(k,))).fetchone(); n=0 if x['enabled'] else 1; await db.execute('UPDATE feature_flags SET enabled=?,updated_by=?,updated_at=CURRENT_TIMESTAMP WHERE key=?',(n,c.from_user.id,k)); await db.commit(); await db.close(); await audit(c.from_user.id,'feature_toggle','feature',k,x['enabled'],n); await c.answer('تغییر کرد'); await fm(c.message)
@r.message(F.text=='📊 داشبورد')
async def dash(m:Message):
 if not await is_admin(m.from_user.id): return
 db=await connect(); qs={'users':'SELECT COUNT(*) n FROM users','products':'SELECT COUNT(*) n FROM products','orders':'SELECT COUNT(*) n FROM orders','paid':"SELECT COUNT(*) n FROM orders WHERE status='paid'",'revenue':"SELECT COALESCE(SUM(final_price),0) n FROM orders WHERE status='paid'"}; v={}
 for k,q in qs.items(): v[k]=(await (await db.execute(q)).fetchone())['n']
 await db.close(); await m.answer(f"📊 داشبورد\nکاربران: {v['users']}\nمحصولات: {v['products']}\nسفارش‌ها: {v['orders']}\nموفق: {v['paid']}\nدرآمد: {v['revenue']:,.0f}")
@r.message(F.text=='📦 محصولات')
async def product_help(m:Message): await m.answer('محصول جدید: محصول: کد | نام | قیمت | موجودی')
@r.message(F.text.startswith('محصول:'))
async def add_product(m:Message):
 if not await perm(m.from_user.id,'products'): return
 try:
  code,name,price,stock=[x.strip() for x in m.text[6:].split('|')]; db=await connect(); await db.execute('INSERT INTO products(code,name,base_price,stock) VALUES(?,?,?,?)',(code,name,float(price),int(stock))); await db.commit(); await db.close(); await audit(m.from_user.id,'product_create','product',code); await m.answer('محصول اضافه شد.')
 except Exception as e: await m.answer('خطا: '+str(e))
@r.message(F.text=='🧾 سفارش‌ها')
async def orders(m:Message):
 if not await perm(m.from_user.id,'orders'): return
 db=await connect(); rows=await (await db.execute('SELECT o.*,p.name FROM orders o JOIN products p ON p.id=o.product_id ORDER BY o.id DESC LIMIT 30')).fetchall(); await db.close(); await m.answer('\n'.join([f"#{x['id']} {x['order_no']} | {x['user_id']} | {x['name']} | {x['final_price']:,.0f} | {x['status']}" for x in rows]) or 'سفارشی نیست.')
@r.message(F.text=='🗄 پشتیبان‌گیری')
async def bkp(m:Message):
 if not await is_super(m.from_user.id): return await m.answer('فقط Super Admin')
 p=backup(); await m.answer_document(FSInputFile(str(p)),caption='پشتیبان دیتابیس')
@r.message(F.text=='📋 لاگ فعالیت')
async def logs(m:Message):
 if not await is_super(m.from_user.id): return
 db=await connect(); rows=await (await db.execute('SELECT * FROM audit_logs ORDER BY id DESC LIMIT 30')).fetchall(); await db.close(); await m.answer('\n'.join([f"{x['created_at']} | {x['admin_id']} | {x['action']} | {x['target_type']}:{x['target_id']}" for x in rows]) or 'لاگی نیست.')
