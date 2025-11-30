# main.py - WarZone Bot Fixed Version
import os
import asyncio
import logging
import sys
import random
import time
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import keyboards as kb
from config import SHOP_ITEMS, DEFENSE_SYSTEM, ATTACK_TYPES, MINER_CONFIG, BOXES, ADMINS
from database import db

print("🚀 شروع WarZone Bot...")

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# بررسی توکن
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    logger.error("❌ توکن یافت نشد! لطفا متغیر محیطی TELEGRAM_TOKEN را تنظیم کنید.")
    sys.exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# وضعیت خرید کاربران
user_purchase_state = {}
user_admin_state = {}

# ==================== دستورات اصلی ====================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    
    # بررسی ادمین بودن
    if db.is_admin(message.from_user.id):
        menu = kb.admin_menu()
        admin_text = "\n\n👑 **شما ادمین هستید** - از پنل مدیریت استفاده کنید"
    else:
        menu = kb.main_menu()
        admin_text = ""
    
    welcome_text = f"""
🎯 **به WarZone خوش آمدید {username}!** ⚔️

💰 **موجودی اولیه**: {user['zp']:,} ZP
⭐ **سطح**: {user['level']}
💪 **قدرت**: {user['power']}
{admin_text}

👇 از منوی زیر انتخاب کنید:
"""
    await message.answer(welcome_text, reply_markup=menu)
    print(f"✅ کاربر {message.from_user.id} استارت زد")

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    help_text = """
🆘 **راهنمای WarZone**

🎮 **منوهای اصلی:**
👤 پروفایل - اطلاعات حساب
🛒 فروشگاه - خرید تجهیزات  
⚔️ حمله - سیستم‌های حمله
📦 باکس - جعبه‌های شانس
⛏ ماینر - تولید ZP
🛡 پدافند - سیستم دفاع
📞 پشتیبانی - ارسال تیکت

💎 **فروشگاه:**
• موشک‌ها - قدرت حمله اصلی
• جنگنده‌ها - حمله ترکیبی
• پهپادها - حمله هوایی
• پدافند - سیستم دفاع
"""
    await message.answer(help_text, reply_markup=kb.main_menu())

@dp.message(Command("admin"))
async def admin_cmd(message: types.Message):
    if not db.is_admin(message.from_user.id):
        await message.answer("❌ دسترسی denied! شما ادمین نیستید.", reply_markup=kb.main_menu())
        return
    
    admin_text = """
👑 **پنل مدیریت WarZone**

📊 **مدیریت کاربران** - افزودن ZP، جم، لول
💎 **انتقال منابع** - انتقال بین کاربران
📈 **آمار بات** - آمار کلی سیستم
📢 **ارسال همگانی** - ارسال پیام به همه کاربران

👇 عملیات مورد نظر را انتخاب کنید:
"""
    await message.answer(admin_text, reply_markup=kb.admin_menu())

# ==================== پروفایل ====================
@dp.message(F.text == "👤 پروفایل")
async def profile_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    profile_text = f"""
👤 **پروفایل جنگجو**

⭐ **سطح**: {user['level']}
📊 **XP**: {user['xp']}/{user['level'] * 100}
💰 **ZP**: {user['zp']:,}
💎 **جم**: {user['gem']}
💪 **قدرت**: {user['power']}

🛡️ **دفاع**: سطح {user['defense_level']}
🔒 **امنیت**: سطح {user['cyber_level']}
⛏ **ماینر**: سطح {user['miner_level']}

🎯 **حملات**: {user['total_attacks']:,}
💥 **دمیج کل**: {user['total_damage']:,}
"""
    await message.answer(profile_text, reply_markup=kb.main_menu())

# ==================== سیستم حمله ====================
@dp.message(F.text == "⚔️ حمله")
async def attack_handler(message: types.Message):
    await message.answer(
        "⚔️ **سیستم حمله WarZone**\n\n"
        "🎯 **حمله تکی** - حمله ساده با موشک\n"
        "💥 **حمله ترکیبی** - با جنگنده (قدرت بیشتر)\n"
        "🛸 **حمله پهپادی** - حمله هوایی\n\n"
        "👇 نوع حمله را انتخاب کنید:",
        reply_markup=kb.attack_menu()
    )

@dp.message(F.text == "🎯 حمله تکی")
async def single_attack_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # محاسبات حمله
    attack_config = ATTACK_TYPES["تکی"]
    is_critical = random.random() < attack_config["critical_chance"]
    base_reward = random.randint(attack_config["base_damage"][0], attack_config["base_damage"][1])
    reward = base_reward * 2 if is_critical else base_reward
    xp_gain = random.randint(attack_config["xp_gain"][0], attack_config["xp_gain"][1])
    
    # آپدیت کاربر
    new_balance = db.update_user_zp(message.from_user.id, reward)
    level_up, new_level = db.update_user_xp(message.from_user.id, xp_gain)
    
    user['total_attacks'] += 1
    user['total_damage'] += reward
    
    # ساخت پاسخ
    critical_text = " 🔥**بحرانی**" if is_critical else ""
    
    response = f"⚔️ **حمله تکی موفق{critical_text}!**\n\n💰 **جایزه**: {reward} ZP\n⭐ **XP**: +{xp_gain}\n"
    
    if level_up:
        response += f"🎉 **سطح شما ارتقا یافت!** (سطح {new_level})\n"
    
    response += f"\n💎 **موجودی جدید**: {new_balance:,} ZP"
    
    await message.answer(response, reply_markup=kb.main_menu())

# ==================== سیستم فروشگاه ====================
@dp.message(F.text == "🛒 فروشگاه")
async def shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    shop_text = f"""
🛒 **فروشگاه WarZone**

💰 **موجودی شما**: {user['zp']:,} ZP

👇 دسته مورد نظر را انتخاب کنید:

🚀 **موشک‌ها** - قدرت حمله اصلی
🛩 **جنگنده‌ها** - حمله ترکیبی  
🛸 **پهپادها** - حمله هوایی
🛡 **پدافند** - سیستم دفاع
"""
    await message.answer(shop_text, reply_markup=kb.shop_main_menu())

@dp.message(F.text == "🚀 موشک‌ها")
async def missiles_shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    missiles_text = f"""
🚀 **موشک‌های موجود**

💰 **موجودی شما**: {user['zp']:,} ZP

👇 موشک مورد نظر را انتخاب کنید:

• **تیرباران** - 400 ZP
  💥 دمیج: 60 | 🎯 سطح ۱

• **رعدآسا** - 700 ZP  
  💥 دمیج: 90 | 🎯 سطح ۳

• **تندباد** - 1,000 ZP
  💥 دمیج: 120 | 🎯 سطح ۵
"""
    await message.answer(missiles_text, reply_markup=kb.missiles_menu())

# خرید موشک
@dp.message(F.text.in_(["تیرباران", "رعدآسا", "تندباد"]))
async def buy_missile_handler(message: types.Message):
    missile_name = message.text
    user_id = message.from_user.id
    
    if missile_name in SHOP_ITEMS["موشک‌ها"]:
        item_data = SHOP_ITEMS["موشک‌ها"][missile_name]
        user = db.get_user(user_id)
        
        # بررسی سطح کاربر
        if user['level'] < item_data['level_required']:
            await message.answer(
                f"❌ **سطح شما کافی نیست!**\n\n"
                f"برای خرید {missile_name} نیاز به سطح {item_data['level_required']} دارید.\n"
                f"سطح فعلی شما: {user['level']}",
                reply_markup=kb.missiles_menu()
            )
            return
        
        # بررسی موجودی
        if not db.can_afford(user_id, item_data['price']):
            await message.answer(
                f"❌ **موجودی ناکافی!**\n\n"
                f"قیمت {missile_name}: {item_data['price']:,} ZP\n"
                f"موجودی شما: {user['zp']:,} ZP",
                reply_markup=kb.missiles_menu()
            )
            return
        
        # انجام خرید
        if db.purchase_item(user_id, item_data['price']):
            db.add_missile(user_id, missile_name, 1)
            new_count = user['missiles'][missile_name]
            
            response = f"✅ **خرید موفق!**\n\n🚀 {missile_name} خریداری شد\n💰 هزینه: {item_data['price']:,} ZP\n📦 تعداد: {new_count} عدد\n💎 موجودی جدید: {user['zp']:,} ZP"
            await message.answer(response, reply_markup=kb.shop_main_menu())
        else:
            await message.answer("❌ خطا در انجام خرید!", reply_markup=kb.shop_main_menu())

# ==================== سیستم باکس ====================
@dp.message(F.text == "📦 باکس")
async def boxes_handler(message: types.Message):
    boxes_text = """
📦 **جعبه‌های شانس WarZone**

📦 **جعبه برنزی** - رایگان (هر ۲۴ ساعت)
• جایزه: 50-200 ZP یا موشک

🥈 **جعبه نقره‌ای** - 5,000 ZP  
• جایزه: 200-500 ZP

👇 نوع جعبه را انتخاب کنید:
"""
    await message.answer(boxes_text, reply_markup=kb.boxes_menu())

@dp.message(F.text == "📦 برنزی")
async def bronze_box_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    if not db.can_open_bronze_box(message.from_user.id):
        remaining = 86400 - (time.time() - user.get('last_bronze_box', 0))
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        
        response = f"⏳ **جعبه برنزی آماده نیست!**\n\n⏰ **زمان باقی‌مانده**: {hours} ساعت و {minutes} دقیقه"
    else:
        reward_type = random.choices(['zp', 'missile'], weights=[70, 30])[0]
        
        if reward_type == 'zp':
            reward = random.randint(50, 200)
            new_balance = db.update_user_zp(message.from_user.id, reward)
            response = f"📦 **جعبه برنزی** 🎉\n\n💰 **جایزه**: {reward} ZP\n💎 **موجودی جدید**: {new_balance:,} ZP"
        else:
            missiles = ["تیرباران", "رعدآسا"]
            missile = random.choice(missiles)
            db.add_missile(message.from_user.id, missile)
            new_count = db.get_user(message.from_user.id)['missiles'][missile]
            response = f"📦 **جعبه برنزی** 🎉\n\n🚀 **جایزه**: ۱ عدد {missile}\n📦 **تعداد جدید**: {new_count} عدد"
        
        db.set_bronze_box_time(message.from_user.id)
    
    await message.answer(response, reply_markup=kb.main_menu())

# ==================== بازگشت‌ها ====================
@dp.message(F.text.contains("بازگشت"))
async def back_handlers(message: types.Message):
    if message.text == "🔙 بازگشت":
        if db.is_admin(message.from_user.id):
            await message.answer("🔙 به منوی اصلی بازگشتید", reply_markup=kb.admin_menu())
        else:
            await message.answer("🔙 به منوی اصلی بازگشتید", reply_markup=kb.main_menu())
    
    elif message.text == "🔙 بازگشت به فروشگاه":
        await message.answer("🔙 به فروشگاه بازگشتید", reply_markup=kb.shop_main_menu())

# ==================== هندلر پیش‌فرض ====================
@dp.message()
async def echo_handler(message: types.Message):
    await message.answer("از منوی زیر انتخاب کنید:", reply_markup=kb.main_menu())

# ==================== تابع اصلی ====================
async def main():
    logger.info("🤖 بات WarZone در حال راه‌اندازی...")
    print("✅ همه هندلرها ثبت شدند")
    
    try:
        logger.info("🚀 شروع polling...")
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted")
        await dp.start_polling(bot)
        print("✅ Polling started successfully")
    except Exception as e:
        logger.error(f"❌ خطا در polling: {e}")
        print(f"❌ Polling error: {e}")

if __name__ == "__main__":
    print("🔧 Starting bot...")
    asyncio.run(main())
