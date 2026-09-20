from aiogram import Router,F
from aiogram.types import Message,CallbackQuery,InlineKeyboardMarkup,InlineKeyboardButton
from app.services.shop import categories,products,get_product,create_order
from app.services.core import money
r=Router()
@r.message(F.text=='🛒 خرید سرویس')
async def buy(m:Message):
 cs=await categories(); kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=c['name'],callback_data=f'cat:{c["id"]}')] for c in cs]); await m.answer('دسته‌بندی را انتخاب کنید:',reply_markup=kb) if cs else await m.answer('محصولی تعریف نشده است.')
@r.callback_query(F.data.startswith('cat:'))
async def cat(c:CallbackQuery):
 ps=await products(int(c.data.split(':')[1])); kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{p['label']} {p['name']} | {money(p['base_price'])}",callback_data=f'prod:{p["id"]}')] for p in ps]); await c.message.edit_text('محصول را انتخاب کنید:',reply_markup=kb); await c.answer()
@r.callback_query(F.data.startswith('prod:'))
async def prod(c:CallbackQuery):
 p=await get_product(int(c.data.split(':')[1])); kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ ثبت سفارش',callback_data=f'buy:{p["id"]}')],[InlineKeyboardButton(text='❤️ علاقه‌مندی',callback_data=f'fav:{p["id"]}')]]); await c.message.edit_text(f"📦 {p['name']}\n\n{p['description']}\nحجم: {p['volume']} {p['unit']}\nمدت: {p['duration']}\nسرور: {p['server']}\nموجودی: {p['stock']}\nقیمت: {money(p['base_price'])}",reply_markup=kb); await c.answer()
@r.callback_query(F.data.startswith('buy:'))
async def order(c:CallbackQuery):
 try: oid=await create_order(c.from_user.id,int(c.data.split(':')[1])); await c.message.answer(f'سفارش #{oid} ثبت شد. پرداخت دستی است و پس از بررسی مدیر تأیید می‌شود.')
 except Exception as e: await c.answer(str(e),show_alert=True)
@r.message(F.text=='📦 سرویس‌های من')
async def services(m:Message):
 from app.database.db import connect
 db=await connect(); rows=await (await db.execute('SELECT * FROM services WHERE user_id=? ORDER BY id DESC',(m.from_user.id,))).fetchall(); await db.close(); await m.answer('\n\n'.join([f"🆔 {x['service_id']} | {x['status']} | {x['server']} | {x['volume']} {x['unit']} | {x['duration']}" for x in rows]) or 'سرویسی ندارید.')
