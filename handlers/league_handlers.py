from aiogram import types
from database import db
from keyboards import league_menu, main_menu

async def league_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # تعیین لیگ بر اساس سطح
    if user[2] >= 20:
        league = "افسانه‌ای"
        reward = 30000
    elif user[2] >= 15:
        league = "پلاتین" 
        reward = 15000
    elif user[2] >= 10:
        league = "طلا"
        reward = 7000
    elif user[2] >= 5:
        league = "نقره"
        reward = 3000
    else:
        league = "برنز"
        reward = 1000
    
    league_text = (
        f"🏆 **سیستم لیگ WarZone**\n\n"
        f"**لیگ فعلی**: {league}\n"
        f"**سطح شما**: {user[2]}\n"
        f"**پاداش هفتگی**: {reward:,} ZP\n\n"
        f"📊 **رتبه جهانی**: Top {max(1, int((user[2] / db.get_total_users()) * 100))}%\n\n"
        "گزینه مورد نظر را انتخاب کنید:"
    )
    
    await message.answer(league_text, reply_markup=league_menu())

async def claim_league_reward(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # محاسبه پاداش بر اساس سطح
    if user[2] >= 20:
        reward = 30000
    elif user[2] >= 15:
        reward = 15000
    elif user[2] >= 10:
        reward = 7000
    elif user[2] >= 5:
        reward = 3000
    else:
        reward = 1000
    
    db.update_user_zp(message.from_user.id, reward)
    new_balance = db.get_user(message.from_user.id)[4]
    
    response = (
        f"🏆 **دریافت پاداش لیگ!**\n\n"
        f"💰 **مبلغ پاداش**: {reward:,} ZP\n"
        f"💎 **موجودی جدید**: {new_balance:,} ZP\n\n"
        f"⏰ **پاداش بعدی**: ۷ روز دیگر"
    )
    
    db.log_activity(message.from_user.id, "league_reward", f"{reward} ZP")
    await message.answer(response, reply_markup=league_menu())
