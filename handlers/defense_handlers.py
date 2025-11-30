from aiogram import types
from database import db
from keyboards import defense_menu, main_menu

async def defense_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    defense_text = (
        f"🛡️ **سیستم دفاع WarZone**\n\n"
        f"**سطح فعلی**: {user[7]}\n"
        f"**شانس بلاک**: {user[7] * 10}%\n"
        f"**کاهش دمیج**: {user[7] * 5}%\n\n"
        f"🔼 **هزینه ارتقا**: {user[7] * 1000} ZP\n\n"
        "گزینه مورد نظر را انتخاب کنید:"
    )
    
    await message.answer(defense_text, reply_markup=defense_menu())

async def upgrade_defense(message: types.Message):
    user = db.get_user(message.from_user.id)
    upgrade_cost = user[7] * 1000
    
    if user[4] >= upgrade_cost:
        db.update_user_zp(message.from_user.id, -upgrade_cost)
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET defense_level = defense_level + 1 WHERE user_id = ?', 
                      (message.from_user.id,))
        conn.commit()
        
        new_level = db.get_user(message.from_user.id)[7]
        new_balance = db.get_user(message.from_user.id)[4]
        
        response = (
            f"🛡️ **ارتقای دفاع موفق!**\n\n"
            f"📊 **سطح جدید**: {new_level}\n"
            f"🎯 **شانس بلاک**: {new_level * 10}%\n"
            f"🛡️ **کاهش دمیج**: {new_level * 5}%\n"
            f"💰 **هزینه**: {upgrade_cost:,} ZP\n"
            f"💎 **موجودی جدید**: {new_balance:,} ZP"
        )
    else:
        response = (
            f"❌ **موجودی ناکافی**\n\n"
            f"💰 **هزینه ارتقا**: {upgrade_cost:,} ZP\n"
            f"💎 **موجودی شما**: {user[4]:,} ZP"
        )
    
    await message.answer(response, reply_markup=defense_menu())
