# main.py - WarZone Bot
import os
import asyncio
import logging
import sys
import random
import time

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp

print("🚀 شروع WarZone Bot...")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logger.error("❌ توکن یافت نشد!")
    sys.exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

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
                'miner_level': 1,
                'miner_balance': 0,
                'total_attacks': 0,
                'total_damage': 0,
                'last_bronze_box': 0,
                'fighters': [],
                'missiles': {}
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
    
    def add_missile(self, user_id, missile_type):
        user = self.get_user(user_id)
        if missile_type not in user['missiles']:
            user['missiles'][missile_type] = 0
        user['missiles'][missile_type] += 1
    
    def add_fighter(self, user_id, fighter_type):
        user = self.get_user(user_id)
        if fighter_type not in user['fighters']:
            user['fighters'].append(fighter_type)
    
    def get_user_fighters(self, user_id):
        user = self.get_user(user_id)
        return user.get('fighters', [])
    
    def can_open_bronze_box(self, user_id):
        user = self.get_user(user_id)
        current_time = time.time()
        return current_time - user.get('last_bronze_box', 0) >= 86400
    
    def set_bronze_box_time(self, user_id):
        user = self.get_user(user_id)
        user['last_bronze_box'] = time.time()

db = SimpleDB()

def main_menu():
    keyboard = [
        [types.KeyboardButton(text="👤 پروفایل"), types.KeyboardButton(text="🛒 فروشگاه"), types.KeyboardButton(text="⚔️ حمله")],
        [types.KeyboardButton(text="🕵️ خرابکاری"), types.KeyboardButton(text="🏆 لیگ ها"), types.KeyboardButton(text="📦 باکس")],
        [types.KeyboardButton(text="⛏ ماینر"), types.KeyboardButton(text="🛡 دفاع"), types.KeyboardButton(text="⚙️ تنظیمات")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    username = f"@{message.from_user.username}" if message.from_user.username else "ناشناس"
    
    welcome_text = f"🎯 **به WarZone خوش آمدید {username}!** ⚔️\n\n💰 **موجودی اولیه**: {user['zp']:,} ZP\n👇 از منوی زیر انتخاب کنید:"
    
    await message.answer(welcome_text, reply_markup=main_menu())

@dp.message(lambda message: message.text == "👤 پروفایل")
async def profile_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    can_open_bronze = db.can_open_bronze_box(message.from_user.id)
    if can_open_bronze:
        box_status = "🟢 آماده"
    else:
        remaining = 86400 - (time.time() - user.get('last_bronze_box', 0))
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        box_status = f"⏳ {hours}h {minutes}m"
    
    profile_text = f"👤 **پروفایل جنگجو**\n\n⭐ **سطح**: {user['level']}\n📊 **XP**: {user['xp']}/{user['level'] * 100}\n💰 **ZP**: {user['zp']:,}\n💎 **جم**: {user['gem']}\n🎯 **حملات**: {user['total_attacks']:,}\n💥 **دمیج کل**: {user['total_damage']:,}\n📦 **جعبه برنزی**: {box_status}"
    
    await message.answer(profile_text, reply_markup=main_menu())

@dp.message(lambda message: message.text == "⚔️ حمله")
async def attack_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    is_critical = random.random() < 0.15
    base_reward = random.randint(40, 80)
    reward = base_reward * 2 if is_critical else base_reward
    xp_gain = random.randint(8, 15)
    
    db.update_user_zp(message.from_user.id, reward)
    level_up = db.update_user_xp(message.from_user.id, xp_gain)
    
    user['total_attacks'] += 1
    user['total_damage'] += reward
    
    critical_text = " 🔥**بحرانی**" if is_critical else ""
    
    response = f"⚔️ **حمله موفق{critical_text}!**\n\n💰 **جایزه**: {reward} ZP\n⭐ **XP**: +{xp_gain}\n"
    
    if level_up:
        new_level = db.get_user(message.from_user.id)['level']
        response += f"🎉 **سطح شما ارتقا یافت!** (سطح {new_level})\n"
    
    response += f"\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)['zp']:,} ZP"
    
    await message.answer(response, reply_markup=main_menu())

@dp.message(lambda message: message.text == "🛒 فروشگاه")
async def shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    shop_text = "🛒 **فروشگاه WarZone**\n\nبرای خرید ریپلای کنید:\n• خرید موشک تیرباران\n• خرید موشک رعدآسا\n• خرید موشک تندباد\n• خرید جنگنده شب‌پرواز\n\n💰 **موجودی شما**: {user['zp']:,} ZP"
    
    await message.answer(shop_text, reply_markup=main_menu())

@dp.message(lambda message: message.text == "📦 باکس")
async def boxes_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    if not db.can_open_bronze_box(message.from_user.id):
        remaining = 86400 - (time.time() - user.get('last_bronze_box', 0))
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        
        response = f"⏳ **جعبه برنزی آماده نیست!**\n\n⏰ **زمان باقی‌مانده**: {hours} ساعت و {minutes} دقیقه\n\n💡 هر ۲۴ ساعت می‌توانید یک جعبه برنزی رایگان باز کنید."
    else:
        reward_type = random.choices(['zp', 'missile'], weights=[70, 30])[0]
        
        if reward_type == 'zp':
            reward = random.randint(50, 200)
            db.update_user_zp(message.from_user.id, reward)
            response = f"📦 **جعبه برنزی** 🎉\n\n💰 **جایزه**: {reward} ZP"
        else:
            missiles = ["تیرباران", "رعدآسا"]
            missile = random.choice(missiles)
            db.add_missile(message.from_user.id, missile)
            response = f"📦 **جعبه برنزی** 🎉\n\n🚀 **جایزه**: ۱ عدد {missile}"
        
        response += f"\n\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)['zp']:,} ZP"
        db.set_bronze_box_time(message.from_user.id)
    
    await message.answer(response, reply_markup=main_menu())

@dp.message(lambda message: message.text == "⛏ ماینر")
async def miner_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    miner_text = f"⛏️ **سیستم ماینر**\n\n💰 **تولید**: {user['miner_level'] * 100} ZP/ساعت\n📊 **سطح**: {user['miner_level']}\n💎 **موجودی**: {user['miner_balance']:,} ZP\n\nبرای برداشت از دستور زیر استفاده کنید: برداشت ماینر"
    
    await message.answer(miner_text, reply_markup=main_menu())

@dp.message(lambda message: message.text in ["🕵️ خرابکاری", "🏆 لیگ ها", "🛡 دفاع", "⚙️ تنظیمات"])
async def coming_soon_handler(message: types.Message):
    await message.answer("🛠 **این قابلیت به زودی فعال می‌شود**\n\n✅ در حال حاضر از سیستم حمله، فروشگاه، ماینر و جعبه‌ها استفاده کنید.", reply_markup=main_menu())

@dp.message()
async def all_messages(message: types.Message):
    try:
        text = message.text.lower()
        
        if "خرید موشک" in text:
            user = db.get_user(message.from_user.id)
            missile_name = text.replace("خرید موشک", "").strip()
            
            missile_prices = {
                "تیرباران": 400,
                "رعدآسا": 700, 
                "تندباد": 1000
            }
            
            if missile_name in missile_prices:
                price = missile_prices[missile_name]
                
                if user['zp'] >= price:
                    db.update_user_zp(message.from_user.id, -price)
                    db.add_missile(message.from_user.id, missile_name)
                    
                    response = f"✅ **خرید موفق**\n\n🚀 **موشک**: {missile_name}\n💰 **قیمت**: {price:,} ZP\n💎 **موجودی جدید**: {user['zp'] - price:,} ZP"
                else:
                    response = f"❌ **موجودی ناکافی**\n\n💰 **قیمت**: {price:,} ZP\n💎 **موجودی شما**: {user['zp']:,} ZP"
                
                await message.answer(response, reply_markup=main_menu())
                return
                
        elif "برداشت ماینر" in text:
            user = db.get_user(message.from_user.id)
            income = user['miner_balance'] + (user['miner_level'] * 100)
            db.update_user_zp(message.from_user.id, income)
            user['miner_balance'] = 0
            
            response = f"⛏️ **برداشت موفق!**\n\n💰 **مبلغ برداشت**: {income:,} ZP\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)['zp']:,} ZP"
            
            await message.answer(response, reply_markup=main_menu())
            return
            
        elif message.text and not message.text.startswith('/'):
            await message.answer("🎯 از منوی زیر انتخاب کنید:", reply_markup=main_menu())
            
    except Exception as e:
        await message.answer("❌ خطا در پردازش دستور", reply_markup=main_menu())

async def main():
    logger.info("🚀 شروع WarZone Bot...")
    
    try:
        async with aiohttp.ClientSession() as session:
            await session.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
        
        bot_info = await bot.get_me()
        logger.info(f"✅ بات: @{bot_info.username}")
        
        logger.info("🟢 بات WarZone آنلاین شد!")
        
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"❌ خطای بحرانی: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
