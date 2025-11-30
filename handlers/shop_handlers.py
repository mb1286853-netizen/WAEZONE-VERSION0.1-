from aiogram import types
from database import db
from config import MISSILE_DATA, FIGHTER_DATA, DRONE_DATA

async def shop_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🚀 موشک‌ها"), types.KeyboardButton(text="🛩 جنگنده‌ها")],
            [types.KeyboardButton(text="🛸 پهپادها"), types.KeyboardButton(text="💎 ویژه‌ها")],
            [types.KeyboardButton(text="🔙 منوی اصلی")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "🛒 **فروشگاه WarZone**\n\n"
        "🚀 **موشک‌ها** - قدرت حمله اصلی\n"
        "🛩 **جنگنده‌ها** - افزایش قدرت ترکیبی\n" 
        "🛸 **پهپادها** - حمله هوایی\n"
        "💎 **ویژه‌ها** - آیتم‌های خاص\n\n"
        "👇 دسته مورد نظر را انتخاب کنید:",
        reply_markup=keyboard
    )

async def missiles_shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    missiles_text = "🚀 **موشک‌های موجود:**\n\n"
    
    for missile, data in MISSILE_DATA.items():
        level_req = f" - سطح {data['min_level']}+" if data['min_level'] > 0 else ""
        if data.get('special'):
            level_req = f" - {data['special']}"
        
        missiles_text += f"• **{missile}** - {data['price']:,} ZP{level_req}\n"
        missiles_text += f"  💥 دمیج: {data['damage']}\n\n"
    
    missiles_text += f"💰 **موجودی شما**: {user[4]:,} ZP\n"
    missiles_text += "\nبرای خرید ریپلای کنید: <code>خرید موشک نامموشک</code>"
    
    from main import main_menu
    await message.answer(missiles_text, reply_markup=main_menu())

async def fighters_shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    fighters_text = "🛩 **جنگنده‌های موجود:**\n\n"
    
    for fighter, data in FIGHTER_DATA.items():
        fighters_text += f"• **{fighter}** - {data['price']:,} ZP\n"
        fighters_text += f"  💥 دمیج: {data['damage']}\n\n"
    
    fighters_text += f"💰 **موجودی شما**: {user[4]:,} ZP\n"
    fighters_text += "\nبرای خرید ریپلای کنید: <code>خرید جنگنده نامجنگنده</code>"
    
    from main import main_menu
    await message.answer(fighters_text, reply_markup=main_menu())

async def drones_shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    drones_text = "🛸 **پهپادهای موجود:**\n\n"
    
    for drone, data in DRONE_DATA.items():
        drones_text += f"• **{drone}** - {data['price']:,} ZP\n"
        drones_text += f"  💥 دمیج: {data['damage']}\n\n"
    
    drones_text += f"💰 **موجودی شما**: {user[4]:,} ZP\n"
    drones_text += "\nبرای خرید ریپلای کنید: <code>خرید پهپاد نامپهپاد</code>"
    
    from main import main_menu
    await message.answer(drones_text, reply_markup=main_menu())
