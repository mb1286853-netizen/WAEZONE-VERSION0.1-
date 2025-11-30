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
                'total_damage': 0,
                'last_bronze_box': 0,
                'fighters': [],
                'missiles': {},
                'drones': []
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
    
    def add_missile(self, user_id, missile_type, quantity=1):
        user = self.get_user(user_id)
        if missile_type not in user['missiles']:
            user['missiles'][missile_type] = 0
        user['missiles'][missile_type] += quantity
    
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
        # چک کردن 24 ساعت (86400 ثانیه)
        return current_time - user.get('last_bronze_box', 0) >= 86400
    
    def set_bronze_box_time(self, user_id):
        user = self.get_user(user_id)
        user['last_bronze_box'] = time.time()

db = SimpleDB()

# کیبورد اصلی
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
    
    # محاسبه زمان باقی‌مانده تا جعبه برنزی
    can_open_bronze = db.can_open_bronze_box(message.from_user.id)
    if can_open_bronze:
        box_status = "🟢 آماده"
    else:
        remaining = 86400 - (time.time() - user.get('last_bronze_box', 0))
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        box_status = f"⏳ {hours}h {minutes}m"
    
    profile_text = (
        f"👤 **پروفایل جنگجو**\n\n"
        f"⭐ **سطح**: {user['level']}\n"
        f"📊 **XP**: {user['xp']}/{user['level'] * 100}\n"
        f"💰 **ZP**: {user['zp']:,}\n"
        f"💎 **جم**: {user['gem']}\n"
        f"💪 **قدرت**: {user['power']}\n"
        f"🎯 **حملات**: {user['total_attacks']:,}\n"
        f"💥 **دمیج کل**: {user['total_damage']:,}\n"
        f"📦 **جعبه برنزی**: {box_status}"
    )
    
    await message.answer(profile_text, reply_markup=main_menu())

# هندلر حمله
@dp.message(lambda message: message.text == "⚔️ حمله")
async def attack_handler(message: types.Message):
    keyboard = [
        [types.KeyboardButton(text="🎯 حمله تکی"), types.KeyboardButton(text="💥 حمله ترکیبی")],
        [types.KeyboardButton(text="🔙 بازگشت")]
    ]
    attack_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    await message.answer(
        "⚔️ **سیستم حمله WarZone**\n\n"
        "🎯 **حمله تکی** - استفاده از یک موشک\n"
        "💥 **حمله ترکیبی** - ترکیب جنگنده و موشک\n\n"
        "👇 نوع حمله را انتخاب کنید:",
        reply_markup=attack_markup
    )

@dp.message(lambda message: message.text == "🎯 حمله تکی")
async def single_attack_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # شانس حمله بحرانی
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

@dp.message(lambda message: message.text == "💥 حمله ترکیبی")
async def combo_attack_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    user_fighters = db.get_user_fighters(message.from_user.id)
    
    if not user_fighters:
        await message.answer(
            "❌ **جنگنده ندارید!**\n\n"
            "برای حمله ترکیبی نیاز به حداقل یک جنگنده دارید.\n"
            "به فروشگاه مراجعه کنید و جنگنده بخرید.",
            reply_markup=main_menu()
        )
        return
    
    # محاسبه دمیج ترکیبی
    base_damage = random.randint(80, 150)
    fighter_bonus = len(user_fighters) * 50
    total_damage = base_damage + fighter_bonus
    
    # شانس بحرانی
    is_critical = random.random() < 0.15
    if is_critical:
        total_damage *= 2
    
    reward = total_damage
    xp_gain = random.randint(15, 25)
    
    db.update_user_zp(message.from_user.id, reward)
    level_up = db.update_user_xp(message.from_user.id, xp_gain)
    
    user['total_attacks'] += 1
    user['total_damage'] += total_damage
    
    critical_text = " 🔥**بحرانی**" if is_critical else ""
    fighter_text = f" ({len(user_fighters)} جنگنده)"
    
    response = f"💥 **حمله ترکیبی موفق{critical_text}**{fighter_text}\n\n"
    response += f"💥 **دمیج**: {total_damage}\n"
    response += f"💰 **جایزه**: {reward} ZP\n"
    response += f"⭐ **XP**: +{xp_gain}\n"
    
    if level_up:
        new_level = db.get_user(message.from_user.id)['level']
        response += f"🎉 **سطح شما ارتقا یافت!** (سطح {new_level})\n"
    
    response += f"\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)['zp']:,} ZP"
    
    await message.answer(response, reply_markup=main_menu())

# هندلر فروشگاه
@dp.message(lambda message: message.text == "🛒 فروشگاه")
async def shop_handler(message: types.Message):
    keyboard = [
        [types.KeyboardButton(text="🚀 موشک‌ها"), types.KeyboardButton(text="🛩 جنگنده‌ها")],
        [types.KeyboardButton(text="🛸 پهپادها"), types.KeyboardButton(text="💎 ویژه‌ها")],
        [types.KeyboardButton(text="🔙 بازگشت")]
    ]
    shop_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    await message.answer(
        "🛒 **فروشگاه WarZone**\n\n"
        "🚀 **موشک‌ها** - قدرت حمله اصلی\n"
        "🛩 **جنگنده‌ها** - افزایش قدرت ترکیبی\n" 
        "🛸 **پهپادها** - حمله هوایی\n"
        "💎 **ویژه‌ها** - آیتم‌های خاص\n\n"
        "👇 دسته مورد نظر را انتخاب کنید:",
        reply_markup=shop_markup
    )

@dp.message(lambda message: message.text == "🚀 موشک‌ها")
async def missiles_shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    missiles_text = (
        "🚀 **موشک‌های موجود:**\n\n"
        "• **تیرباران** - 400 ZP\n  💥 دمیج: 60\n  🎯 سطح ۱\n\n"
        "• **رعدآسا** - 700 ZP\n  💥 دمیج: 90\n  🎯 سطح ۳\n\n"
        "• **تندباد** - 1,000 ZP\n  💥 دمیج: 120\n  🎯 سطح ۵\n\n"
        f"💰 **موجودی شما**: {user['zp']:,} ZP\n\n"
        "برای خرید ریپلای کنید: <code>خرید موشک نامموشک</code>"
    )
    
    await message.answer(missiles_text, reply_markup=main_menu())

@dp.message(lambda message: message.text == "🛩 جنگنده‌ها")
async def fighters_shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    fighters_text = (
        "🛩 **جنگنده‌های موجود:**\n\n"
        "• **شب‌پرواز** - 5,000 ZP\n  💥 دمیج: 200\n\n"
        "• **توفان‌ساز** - 8,000 ZP\n  💥 دمیج: 320\n\n"
        "• **آذرخش** - 12,000 ZP\n  💥 دمیج: 450\n\n"
        "• **شبح‌ساحل** - 18,000 ZP\n  💥 دمیج: 700\n\n"
        f"💰 **موجودی شما**: {user['zp']:,} ZP\n\n"
        "برای خرید ریپلای کنید: <code>خرید جنگنده نامجنگنده</code>"
    )
    
    await message.answer(fighters_text, reply_markup=main_menu())

@dp.message(lambda message: message.text == "🛸 پهپادها")
async def drones_shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    drones_text = (
        "🛸 **پهپادهای موجود:**\n\n"
        "• **زنبورک** - 3,000 ZP\n  💥 دمیج: 90\n\n"
        "• **سایفر** - 5,000 ZP\n  💥 دمیج: 150\n\n"
        "• **ریزپرنده V** - 8,000 ZP\n  💥 دمیج: 250\n\n"
        f"💰 **موجودی شما**: {user['zp']:,} ZP\n\n"
        "برای خرید ریپلای کنید: <code>خرید پهپاد نامپهپاد</code>"
    )
    
    await message.answer(drones_text, reply_markup=main_menu())

@dp.message(lambda message: message.text == "💎 ویژه‌ها")
async def special_shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    special_text = (
        "💎 **آیتم‌های ویژه:**\n\n"
        "• **آتشفشان** - 8,000 ZP\n  💥 دمیج: 2,000\n\n"
        "• **توفان‌نو** - 15,000 ZP\n  💥 دمیج: 3,000\n\n"
        "• **خاموش‌کن** - 20,000 ZP\n  🔧 قطع سیستم\n\n"
        f"💰 **موجودی شما**: {user['zp']:,} ZP\n\n"
        "برای خرید ریپلای کنید: <code>خرید ویژه نامآیتم</code>"
    )
    
    await message.answer(special_text, reply_markup=main_menu())

# هندلر باکس
@dp.message(lambda message: message.text == "📦 باکس")
async def boxes_handler(message: types.Message):
    keyboard = [
        [types.KeyboardButton(text="📦 برنزی"), types.KeyboardButton(text="🥈 نقره‌ای")],
        [types.KeyboardButton(text="🥇 طلایی"), types.KeyboardButton(text="💎 الماس")],
        [types.KeyboardButton(text="🔙 بازگشت")]
    ]
    boxes_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    await message.answer(
        "📦 **جعبه‌های شانس**\n\n"
        "📦 **برنزی** - رایگان (هر ۲۴ ساعت)\n"
        "🥈 **نقره‌ای** - 5,000 ZP\n"
        "🥇 **طلایی** - ۲ جم\n"
        "💎 **الماس** - ۵ جم\n\n"
        "👇 نوع جعبه را انتخاب کنید:",
        reply_markup=boxes_markup
    )

@dp.message(lambda message: message.text == "📦 برنزی")
async def bronze_box_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    if not db.can_open_bronze_box(message.from_user.id):
        remaining = 86400 - (time.time() - user.get('last_bronze_box', 0))
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        
        response = (
            f"⏳ **جعبه برنزی آماده نیست!**\n\n"
            f"⏰ **زمان باقی‌مانده**: {hours} ساعت و {minutes} دقیقه\n\n"
            f"💡 هر ۲۴ ساعت می‌توانید یک جعبه برنزی رایگان باز کنید."
        )
    else:
        # شانس‌ها
        reward_type = random.choices(['zp', 'missile'], weights=[70, 30])[0]
        
        if reward_type == 'zp':
            reward = random.randint(50, 200)
            db.update_user_zp(message.from_user.id, reward)
            response = f"📦 **جعبه برنزی** 🎉\n\n💰 **جایزه**: {reward} ZP"
        else:
            missiles = ["تیرباران", "رعدآسا"]
            missile = random.choice(missiles)
            db.add_missile(message.from_user.id, missile, 1)
            response = f"📦 **جعبه برنزی** 🎉\n\n🚀 **جایزه**: ۱ عدد {missile}"
        
        response += f"\n\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)['zp']:,} ZP"
        db.set_bronze_box_time(message.from_user.id)
    
    await message.answer(response, reply_markup=main_menu())

@dp.message(lambda message: message.text == "🥈 نقره‌ای")
async def silver_box_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    price = 5000
    
    if user['zp'] >= price:
        db.update_user_zp(message.from_user.id, -price)
        reward = random.randint(200, 500)
        db.update_user_zp(message.from_user.id, reward)
        
        response = (
            f"🥈 **جعبه نقره‌ای** 🎉\n\n"
            f"💰 **هزینه**: {price:,} ZP\n"
            f"💰 **جایزه**: {reward} ZP\n"
            f"💎 **موجودی جدید**: {db.get_user(message.from_user.id)['zp']:,} ZP"
        )
    else:
        response = (
            f"❌ **موجودی ناکافی**\n\n"
            f"💰 **قیمت جعبه**: {price:,} ZP\n"
            f"💎 **موجودی شما**: {user['zp']:,} ZP"
        )
    
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
        f"🔼 **هزینه ارتقا**: {user['miner_level'] * 500} ZP\n\n"
        "برای برداشت از دستور زیر استفاده کنید:\n<code>برداشت ماینر</code>"
    )
    
    await message.answer(miner_text, reply_markup=main_menu())

# هندلر قابلیت‌های آینده
@dp.message(lambda message: message.text in ["🕵️ خرابکاری", "🏆 لیگ ها", "🛡 دفاع", "⚙️ تنظیمات"])
async def coming_soon_handler(message: types.Message):
    feature_name = {
        "🕵️ خرابکاری": "سیستم خرابکاری",
        "🏆 لیگ ها": "سیستم لیگ‌ها", 
        "🛡 دفاع": "سیستم دفاع",
        "⚙️ تنظیمات": "تنظیمات پیشرفته"
    }[message.text]
    
    await message.answer(
        f"🛠 **{feature_name}**\n\n"
        f"🔜 به زودی فعال می‌شود\n\n"
        f"✅ در حال حاضر از این قابلیت‌ها استفاده کنید:\n"
        f"• ⚔️ سیستم حمله\n"
        f"• 🛒 فروشگاه\n"
        f"• ⛏️ ماینر\n"
        f"• 📦 جعبه‌ها",
        reply_markup=main_menu()
    )

# هندلر پیام‌های متنی برای خرید و دستورات
@dp.message()
async def all_messages(message: types.Message):
    try:
        text = message.text.lower()
        
        if "خرید" in text and "موشک" in text:
            user = db.get_user(message.from_user.id)
            missile_name = text.replace("خرید", "").replace("موشک", "").strip()
            
            missile_prices = {
                "تیرباران": 400,
                "رعدآسا": 700, 
                "تندباد": 1000
            }
            
            if missile_name in missile_prices:
                price = missile_prices[missile_name]
                
                if user['zp'] >= price:
                    db.update_user_zp(message.from_user.id, -price)
                    db.add_missile(message.from_user.id, missile_name, 1)
                    
                    response = (
                        f"✅ **خرید موفق**\n\n"
                        f"🚀 **موشک**: {missile_name}\n"
                        f"💰 **قیمت**: {price:,} ZP\n"
                        f"💎 **موجودی جدید**: {user['zp'] - price:,} ZP"
                    )
                else:
                    response = (
                        f"❌ **موجودی ناکافی**\n\n"
                        f"💰 **قیمت**: {price:,} ZP\n"
                        f"💎 **موجودی شما**: {user['zp']:,} ZP"
                    )
                
                await message.answer(response, reply_markup=main_menu())
                return
                
        elif "خرید" in text and "جنگنده" in text:
            user = db.get_user(message.from_user.id)
            fighter_name = text.replace("خرید", "").replace("جنگنده", "").strip()
            
            fighter_prices = {
                "شب‌پرواز": 5000,
                "توفان‌ساز": 8000,
                "آذرخش": 12000,
                "شبح‌ساحل": 18000
            }
            
            if fighter_name in fighter_prices:
                price = fighter_prices[fighter_name]
                
                if user['zp'] >= price:
                    db.update_user_zp(message.from_user.id, -price)
                    db.add_fighter(message.from_user.id, fighter_name)
                    
                    response = (
                        f"✅ **خرید موفق**\n\n"
                        f"🛩 **جنگنده**: {fighter_name}\n"
                        f"💰 **قیمت**: {price:,} ZP\n"
                        f"💎 **موجودی جدید**: {user['zp'] - price:,} ZP\n\n"
                        f"🎯 اکنون می‌توانید از حمله ترکیبی استفاده کنید!"
                    )
                else:
                    response = (
                        f"❌ **موجودی ناکافی**\n\n"
                        f"💰 **قیمت**: {price:,} ZP\n"
                        f"💎 **موجودی شما**: {user['zp']:,} ZP"
                    )
                
                await message.answer(response, reply_markup=main_menu())
                return
                
        elif "برداشت" in text and "ماینر" in text:
            user = db.get_user(message.from_user.id)
            income = user['miner_balance'] + (user['miner_level'] * 100)
            db.update_user_zp(message.from_user.id, income)
            user['miner_balance'] = 0
            
            response = (
                f"⛏️ **برداشت موفق!**\n\n"
                f"💰 **مبلغ برداشت**: {income:,} ZP\n"
                f"💎 **موجودی جدید**: {db.get_user(message.from_user.id)['zp']:,} ZP\n\n"
                f"✅ برداشت بعدی: ۱ ساعت دیگر"
            )
            
            await message.answer(response, reply_markup=main_menu())
            return
            
        elif message.text == "🔙 بازگشت":
            await message.answer("🔙 بازگشت به منوی اصلی", reply_markup=main_menu())
            return
            
        elif message.text and not message.text.startswith('/'):
            await message.answer("🎯 از منوی زیر انتخاب کنید:", reply_markup=main_menu())
            
    except Exception as e:
        await message.answer("❌ خطا در پردازش دستور", reply_markup=main_menu())

# شروع بات
async def main():
    logger.info("🚀 شروع WarZone Bot...")
    
    try:
        # حذف وب‌هوک
        async with aiohttp.ClientSession() as session:
            await 
