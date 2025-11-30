# main.py - WarZone Bot
import os
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp
import random

print("🚀 شروع WarZone Bot...")

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# دریافت توکن
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logger.error("❌ توکن یافت نشد! لطفا TOKEN را تنظیم کنید.")
    sys.exit(1)

# ساخت بات
bot = Bot(token=TOKEN)
dp = Dispatcher()

# دیتابیس ساده
class SimpleDB:
    def __init__(self):
        self.users = {}
    
    def get_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {
                'user_id': user_id,
                'level': 1,
                'xp': 0,
                'zp': 1000,
                'gem': 0,
                'power': 100,
                'defense_level': 1,
                'cyber_level': 1,
                'miner_level': 1,
                'miner_balance': 0,
                'total_attacks': 0,
                'total_damage': 0
            }
        return self.users[user_id]
    
    def update_user_zp(self, user_id, amount):
        user = self.get_user(user_id)
        user['zp'] += amount
    
    def update_user_xp(self, user_id, amount):
        user = self.get_user(user_id)
        user['xp'] += amount
        xp_needed = user['level'] * 100
        if user['xp'] >= xp_needed:
            user['level'] += 1
            user['xp'] -= xp_needed
            return True
        return False

db = SimpleDB()

# کیبورد ساده
def main_menu():
    keyboard = [
        [types.KeyboardButton(text="👤 پروفایل"), types.KeyboardButton(text="🛒 فروشگاه"), types.KeyboardButton(text="⚔️ حمله")],
        [types.KeyboardButton(text="🕵️ خرابکاری"), types.KeyboardButton(text="🏆 لیگ ها"), types.KeyboardButton(text="📦 باکس")],
        [types.KeyboardButton(text="⛏ ماینر"), types.KeyboardButton(text="🛡 دفاع"), types.KeyboardButton(text="⚙️ تنظیمات")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# هندلر استارت
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    username = f"@{message.from_user.username}" if message.from_user.username else "ناشناس"
    
    welcome_text = (
        f"🎯 **به WarZone خوش آمدید {username}!** ⚔️\n\n"
        f"💰 **موجودی اولیه**: {user['zp']:,} ZP\n"
        "👇 از منوی زیر انتخاب کنید:"
    )
    
    await message.answer(welcome_text, reply_markup=main_menu())

# هندلر پروفایل
@dp.message(lambda message: message.text == "👤 پروفایل")
async def profile_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    profile_text = (
        f"👤 **پروفایل جنگجو**\n\n"
        f"⭐ **سطح**: {user['level']}\n"
        f"📊 **XP**: {user['xp']}/{user['level'] * 100}\n"
        f"💰 **ZP**: {user['zp']:,}\n"
        f"💎 **جم**: {user['gem']}\n"
        f"💪 **قدرت**: {user['power']}\n"
        f"🎯 **حملات**: {user['total_attacks']:,}\n"
        f"💥 **دمیج کل**: {user['total_damage']:,}"
    )
    
    await message.answer(profile_text, reply_markup=main_menu())

# هندلر حمله
@dp.message(lambda message: message.text == "⚔️ حمله")
async def attack_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # حمله ساده
    is_critical = random.random() < 0.15
    base_reward = random.randint(40, 80)
    reward = base_reward * 2 if is_critical else base_reward
    xp_gain = random.randint(8, 15)
    
    db.update_user_zp(message.from_user.id, reward)
    level_up = db.update_user_xp(message.from_user.id, xp_gain)
    
    user['total_attacks'] += 1
    user['total_damage'] += reward
    
    critical_text = " 🔥**بحرانی**" if is_critical else ""
    
    response = f"⚔️ **حمله موفق{critical_text}!**\n\n"
    response += f"💰 **جایزه**: {reward} ZP\n"
    response += f"⭐ **XP**: +{xp_gain}\n"
    
    if level_up:
        new_level = db.get_user(message.from_user.id)['level']
        response += f"🎉 **سطح شما ارتقا یافت!** (سطح {new_level})\n"
    
    response += f"\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)['zp']:,} ZP"
    
    await message.answer(response, reply_markup=main_menu())

# هندلر ماینر
@dp.message(lambda message: message.text == "⛏ ماینر")
async def miner_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    miner_text = (
        f"⛏️ **سیستم ماینر**\n\n"
        f"💰 **تولید**: {user['miner_level'] * 100} ZP/ساعت\n"
        f"📊 **سطح**: {user['miner_level']}\n"
        f"💎 **موجودی**: {user['miner_balance']:,} ZP\n\n"
        f"🔼 **هزینه ارتقا**: {user['miner_level'] * 500} ZP"
    )
    
    await message.answer(miner_text, reply_markup=main_menu())

# هندلر باکس
@dp.message(lambda message: message.text == "📦 باکس")
async def boxes_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # جعبه برنزی ساده
    reward = random.randint(50, 200)
    db.update_user_zp(message.from_user.id, reward)
    
    response = (
        f"📦 **جعبه برنزی** 🎉\n\n"
        f"💰 **جایزه**: {reward} ZP\n"
        f"💎 **موجودی جدید**: {db.get_user(message.from_user.id)['zp']:,} ZP"
    )
    
    await message.answer(response, reply_markup=main_menu())

# هندلر قابلیت‌های آینده
@dp.message(lambda message: message.text in ["🛒 فروشگاه", "🕵️ خرابکاری", "🏆 لیگ ها", "🛡 دفاع", "⚙️ تنظیمات"])
async def coming_soon_handler(message: types.Message):
    await message.answer(
        "🛠 **این قابلیت به زودی فعال می‌شود**\n\n"
        "✅ در حال حاضر از این قابلیت‌ها استفاده کنید:\n"
        "• ⚔️ سیستم حمله\n"
        "• ⛏️ ماینر\n"
        "• 📦 جعبه‌ها",
        reply_markup=main_menu()
    )

# هندلر پیام‌های متنی
@dp.message()
async def all_messages(message: types.Message):
    if message.text and not message.text.startswith('/'):
        await message.answer("🎯 از منوی زیر انتخاب کنید:", reply_markup=main_menu())

# شروع بات
async def main():
    logger.info("🚀 شروع WarZone Bot...")
    
    try:
        # حذف وب‌هوک
        async with aiohttp.ClientSession() as session:
            await session.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
            logger.info("✅ وب‌هوک حذف شد")
        
        # اطلاعات بات
        bot_info = await bot.get_me()
        logger.info(f"✅ بات: @{bot_info.username}")
        
        logger.info("🟢 بات WarZone آنلاین شد!")
        
        # شروع پولینگ
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"❌ خطای بحرانی: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
