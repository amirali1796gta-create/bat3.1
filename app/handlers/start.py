from aiogram import Router,F
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.services.core import ensure_user,user
from app.keyboards.main import user as uk
r=Router()
@r.message(CommandStart())
async def start(m:Message):
 await ensure_user(m.from_user); await m.answer('سلام 👋\n\nربات فروش خدمات آماده است. از منوی زیر استفاده کنید.',reply_markup=uk())
@r.message(F.text=='👤 پروفایل')
async def profile(m:Message):
 u=await user(m.from_user.id); await m.answer(f"👤 پروفایل\nID: {u['id']}\nموجودی: {u['balance']:,.0f}\nسطح: {u['level']}\nنماینده: {'بله' if u['is_reseller'] else 'خیر'}")
