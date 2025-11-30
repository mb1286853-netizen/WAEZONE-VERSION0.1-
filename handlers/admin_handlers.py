from aiogram import types
from aiogram.filters import Command
from database import db
from config import ADMIN_IDS

async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ دسترسی denied!")
        return
    
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📊 آمار کلی"), types.KeyboardButton(text="👥 مدیریت کاربران")],
            [types.KeyboardButton(text="💰 انتقال ZP"), types.KeyboardButton(text="🎁 هدیه همگانی")],
            [types.KeyboardButton(text="🔙 منوی اصلی")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "👑 **پنل مدیریت WarZone**\n\n"
        "📊 **آمار کلی** - وضعیت ربات\n"
        "👥 **مدیریت کاربران** - بن/آنبن\n" 
        "💰 **انتقال ZP** - ارسال به کاربر\n"
        "🎁 **هدیه همگانی** - ارسال به همه\n\n"
        "👇 گزینه مورد نظر را انتخاب کنید:",
        reply_markup=keyboard
    )

async def admin_stats(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    total_users = db.get_total_users()
    total_attacks = db.get_total_attacks()
    
    # محاسبه ZP کل
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(zp) FROM users')
    total_zp = cursor.fetchone()[0] or 0
    
    stats_text = (
        "📊 **آمار کلی ربات**\n\n"
        f"👥 **کل کاربران**: {total_users:,}\n"
        f"⚔️ **کل حملات**: {total_attacks:,}\n"
        f"💰 **ZP در گردش**: {total_zp:,}\n"
        f"🆔 **آخرین کاربر**: {get_last_user()}\n\n"
        f"🟢 **وضعیت**: فعال"
    )
    
    await message.answer(stats_text)

def get_last_user():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users ORDER BY created_at DESC LIMIT 1')
    result = cursor.fetchone()
    return result[0] if result else "نامشخص"
