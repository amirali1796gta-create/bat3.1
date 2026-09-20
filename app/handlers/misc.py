from aiogram import Router,F
from aiogram.types import Message
from app.database.db import connect
r=Router()
@r.message(F.text=='💳 کیف پول')
async def wallet(m:Message):
 db=await connect(); u=await (await db.execute('SELECT balance FROM users WHERE id=?',(m.from_user.id,))).fetchone(); await db.close(); await m.answer(f"💳 موجودی: {u['balance']:,.0f}\nبرای شارژ کیف پول با پشتیبانی تماس بگیرید.")
@r.message(F.text=='🤝 نمایندگی')
async def reseller(m:Message):
 db=await connect(); u=await (await db.execute('SELECT is_reseller FROM users WHERE id=?',(m.from_user.id,))).fetchone();
 if u['is_reseller']: await m.answer('🤝 شما نماینده فعال هستید.')
 else:
  await db.execute("INSERT INTO reseller_requests(user_id) VALUES(?)",(m.from_user.id,)); await db.commit(); await m.answer('درخواست نمایندگی ثبت شد.')
 await db.close()
@r.message(F.text=='📚 آموزش')
async def tut(m:Message):
 db=await connect(); r=await (await db.execute('SELECT * FROM tutorials WHERE active=1 ORDER BY sort_order')).fetchall(); await db.close(); await m.answer('\n\n'.join([f"📚 {x['title']}\n{x['description']}\n{x['link']}" for x in r]) or 'آموزشی ثبت نشده.')
@r.message(F.text=='ℹ️ درباره ما')
async def about(m:Message):
 db=await connect(); r=await (await db.execute("SELECT value FROM settings WHERE key='about'")).fetchone(); await db.close(); await m.answer(r['value'] if r else 'اطلاعات درباره ما هنوز تنظیم نشده است.')
@r.message(F.text=='👥 دعوت دوستان')
async def invite(m:Message):
 me=await m.bot.get_me(); await m.answer(f'https://t.me/{me.username}?start=ref_{m.from_user.id}')
@r.message(F.text=='❤️ علاقه‌مندی')
async def fav(m:Message):
 db=await connect(); r=await (await db.execute('SELECT p.name,p.base_price FROM products p JOIN favorites f ON p.id=f.product_id WHERE f.user_id=?',(m.from_user.id,))).fetchall(); await db.close(); await m.answer('\n'.join([f"❤️ {x['name']} | {x['base_price']:,.0f}" for x in r]) or 'خالی است.')
@r.message(F.text=='📞 پشتیبانی')
async def support(m:Message): await m.answer('برای ثبت تیکت: تیکت: موضوع | متن پیام')
@r.message(F.text.startswith('تیکت:'))
async def ticket(m:Message):
 raw=m.text[5:].strip();
 if '|' not in raw:return await m.answer('فرمت: تیکت: موضوع | متن')
 s,b=raw.split('|',1); db=await connect(); import secrets; no='TKT-'+''.join(secrets.choice('ABCDEFGH0123456789') for _ in range(8)); cur=await db.execute('INSERT INTO tickets(ticket_no,user_id,subject) VALUES(?,?,?)',(no,m.from_user.id,s.strip())); tid=cur.lastrowid; await db.execute('INSERT INTO ticket_messages(ticket_id,sender_id,message) VALUES(?,?,?)',(tid,m.from_user.id,b.strip())); await db.commit(); await db.close(); await m.answer(f'تیکت {no} ثبت شد.')
@r.message(F.text=='🎁 گیفت کارت')
async def gift(m:Message): await m.answer('کد را به شکل گیفت: CODE ارسال کنید.')
@r.message(F.text.startswith('گیفت:'))
async def redeem(m:Message):
 code=m.text[5:].strip().upper(); db=await connect(); g=await (await db.execute('SELECT * FROM gift_cards WHERE code=? AND active=1',(code,))).fetchone()
 if not g or g['used_count']>=g['max_uses']: await db.close(); return await m.answer('گیفت کارت نامعتبر یا استفاده‌شده است.')
 await db.execute('UPDATE gift_cards SET used_count=used_count+1 WHERE id=?',(g['id'],)); await db.execute('UPDATE users SET balance=balance+? WHERE id=?',(g['amount'],m.from_user.id)); await db.execute('INSERT OR IGNORE INTO wallet_transactions(user_id,amount,type,reference,note) VALUES(?,?,?,?,?)',(m.from_user.id,g['amount'],'gift_card',code,'گیفت کارت')); await db.commit(); await db.close(); await m.answer(f"{g['amount']:,.0f} به کیف پول اضافه شد.")
