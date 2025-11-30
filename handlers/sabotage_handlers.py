from aiogram import types
from aiogram.filters import Command
from database import db
from keyboards import sabotage_menu, main_menu
import random

async def sabotage_handler(message: types.Message):
    await message.answer(
        "🕵️ **سیستم خرابکاری WarZone**\n\n"
        "**انواع تیم خرابکاری:**\n"
        "• **نفوذی** - کاهش پدافند دشمن\n"
        "• **الکترونیکی** - غیرفعال کردن امنیت\n"
        "• **اطلاعاتی** - افزایش غارت\n\n"
        "تیم مورد نظر را انتخاب کنید:",
        reply_markup=sabotage_menu()
    )

async def infiltrate_sabotage(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # شانس موفقیت
    success_chance = 0.7
    is_success = random.random() < success_chance
    
    if is_success:
        reward = random.randint(100, 300)
        db.update_user_zp(message.from_user.id, reward)
        
        response = (
            f"🕵️ **خرابکاری نفوذی موفق!**\n\n"
            f"✅ **عملیات**: نفوذ به سیستم دفاعی\n"
            f"💰 **جایزه**: {reward} ZP\n"
            f"🎯 **اثر**: کاهش ۲۰٪ پدافند دشمن\n"
            f"💎 **موجودی جدید**: {db.get_user(message.from_user.id)[4]:,} ZP"
        )
    else:
        response = (
            f"🕵️ **خرابکاری ناموفق!**\n\n"
            f"❌ **عملیات**: نفوذ به سیستم دفاعی\n"
            f"⚠️ **هشدار**: تیم شما شناسایی شد\n"
            f"💡 **توصیه**: سطح تیم را ارتقا دهید"
        )
    
    db.log_activity(message.from_user.id, "sabotage", "خرابکاری نفوذی")
    await message.answer(response, reply_markup=sabotage_menu())
