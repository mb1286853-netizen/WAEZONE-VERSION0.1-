# main.py - WarZone Bot Complete
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
from config import SHOP_ITEMS, ATTACK_TYPES, ADMINS
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
    logger.error("❌ توکن یافت نشد!")
    sys.exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# وضعیت کاربران
user_purchase_state = {}
user_admin_state = {}

# ==================== دستورات اصلی ====================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    
    if db.is_admin(message.from_user.id):
        menu = kb.admin_menu()
        admin_text = "\n\n👑 **شما ادمین هستید**"
    else:
        menu = kb.main_menu()
        admin_text = ""
    
    welcome_text = f"""
🎯 **به WarZone خوش آمدید {username}!** ⚔️

💰 **موجودی**: {user['zp']:,} ZP
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

👤 پروفایل - اطلاعات حساب
🛒 فروشگاه - خرید تجهیزات  
⚔️ حمله - سیستم‌های حمله
📦 باکس - جعبه‌های شانس
📞 پشتیبانی - ارسال تیکت
"""
    await message.answer(help_text, reply_markup=kb.main_menu())

@dp.message(Command("admin"))
async def admin_cmd(message: types.Message):
    if not db.is_admin(message.from_user.id):
        await message.answer("❌ دسترسی denied!", reply_markup=kb.main_menu())
        return
    
    admin_text = """
👑 **پنل مدیریت**

📊 آمار بات
👥 مدیریت کاربران
📢 ارسال همگانی
"""
    await message.answer(admin_text, reply_markup=kb.admin_menu())

# ==================== پروفایل ====================
@dp.message(F.text == "👤 پروفایل")
async def profile_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    profile_text = f"""
👤 **پروفایل جنگجو**

⭐ **سطح**: {user['level']}
💰 **ZP**: {user['zp']:,}
💎 **جم**: {user['gem']}
💪 **قدرت**: {user['power']}

🎯 **حملات**: {user['total_attacks']:,}
💥 **دمیج کل**: {user['total_damage']:,}
🛩 **جنگنده‌ها**: {len(user['fighters'])}
🛸 **پهپادها**: {len(user['drones'])}
"""
    await message.answer(profile_text, reply_markup=kb.main_menu())

# ==================== سیستم حمله ====================
@dp.message(F.text == "⚔️ حمله")
async def attack_cmd(message: types.Message):
    await message.answer(
        "⚔️ **سیستم حمله**\n\n"
        "🎯 حمله تکی\n"
        "💥 حمله ترکیبی\n"
        "🛸 حمله پهپادی\n\n"
        "👇 نوع حمله را انتخاب کنید:",
        reply_markup=kb.attack_menu()
    )

@dp.message(F.text == "🎯 حمله تکی")
async def single_attack_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    reward = random.randint(50, 100)
    xp_gain = random.randint(10, 20)
    
    new_balance = db.update_user_zp(message.from_user.id, reward)
    user['total_attacks'] += 1
    user['total_damage'] += reward
    
    response = f"⚔️ **حمله تکی موفق!**\n\n💰 **جایزه**: {reward} ZP\n⭐ **XP**: +{xp_gain}\n💎 **موجودی جدید**: {new_balance:,} ZP"
    
    await message.answer(response, reply_markup=kb.main_menu())

@dp.message(F.text == "💥 حمله ترکیبی")
async def combo_attack_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    user_fighters = user['fighters']
    
    if not user_fighters:
        await message.answer(
            "❌ **جنگنده ندارید!**\n\n"
            "برای حمله ترکیبی نیاز به جنگنده دارید.\n"
            "به فروشگاه مراجعه کنید.",
            reply_markup=kb.main_menu()
        )
        return
    
    base_damage = random.randint(80, 150)
    fighter_bonus = len(user_fighters) * 50
    total_damage = base_damage + fighter_bonus
    
    reward = total_damage
    xp_gain = random.randint(15, 25)
    
    new_balance = db.update_user_zp(message.from_user.id, reward)
    user['total_attacks'] += 1
    user['total_damage'] += total_damage
    
    fighter_text = f" ({len(user_fighters)} جنگنده)"
    response = f"💥 **حمله ترکیبی موفق**{fighter_text}\n\n💥 **دمیج**: {total_damage}\n💰 **جایزه**: {reward} ZP\n⭐ **XP**: +{xp_gain}\n💎 **موجودی جدید**: {new_balance:,} ZP"
    
    await message.answer(response, reply_markup=kb.main_menu())

@dp.message(F.text == "🛸 حمله پهپادی")
async def drone_attack_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    user_drones = user['drones']
    
    if not user_drones:
        await message.answer(
            "❌ **پهپاد ندارید!**\n\n"
            "برای حمله پهپادی نیاز به پهپاد دارید.\n"
            "به فروشگاه مراجعه کنید.",
            reply_markup=kb.main_menu()
        )
        return
    
    base_damage = random.randint(60, 120)
    drone_bonus = len(user_drones) * 30
    total_damage = base_damage + drone_bonus
    
    reward = total_damage
    xp_gain = random.randint(12, 20)
    
    new_balance = db.update_user_zp(message.from_user.id, reward)
    user['total_attacks'] += 1
    user['total_damage'] += total_damage
    
    drone_text = f" ({len(user_drones)} پهپاد)"
    response = f"🛸 **حمله پهپادی موفق**{drone_text}\n\n💥 **دمیج**: {total_damage}\n💰 **جایزه**: {reward} ZP\n⭐ **XP**: +{xp_gain}\n💎 **موجودی جدید**: {new_balance:,} ZP"
    
    await message.answer(response, reply_markup=kb.main_menu())

# ==================== فروشگاه ====================
@dp.message(F.text == "🛒 فروشگاه")
async def shop_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    shop_text = f"""
🛒 **فروشگاه WarZone**

💰 **موجودی شما**: {user['zp']:,} ZP

👇 دسته مورد نظر را انتخاب کنید:

🚀 موشک‌ها
🛩 جنگنده‌ها  
🛸 پهپادها
🛡 پدافند
"""
    await message.answer(shop_text, reply_markup=kb.shop_main_menu())

@dp.message(F.text == "🚀 موشک‌ها")
async def missiles_shop_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    missiles_text = f"""
🚀 **موشک‌های موجود**

💰 **موجودی شما**: {user['zp']:,} ZP

• تیرباران - 400 ZP
• رعدآسا - 700 ZP  
• تندباد - 1,000 ZP
"""
    await message.answer(missiles_text, reply_markup=kb.missiles_menu())

@dp.message(F.text == "🛩 جنگنده‌ها")
async def fighters_shop_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    fighters_text = f"""
🛩 **جنگنده‌های موجود**

💰 **موجودی شما**: {user['zp']:,} ZP

• شب‌پرواز - 5,000 ZP
• توفان‌ساز - 8,000 ZP
• آذرخش - 12,000 ZP
"""
    await message.answer(fighters_text, reply_markup=kb.fighters_menu())

@dp.message(F.text == "🛸 پهپادها")
async def drones_shop_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    drones_text = f"""
🛸 **پهپادهای موجود**

💰 **موجودی شما**: {user['zp']:,} ZP

• زنبورک - 3,000 ZP
• سایفر - 5,000 ZP
• ریزپرنده V - 8,000 ZP
"""
    await message.answer(drones_text, reply_markup=kb.drones_menu())

@dp.message(F.text == "🛡 پدافند")
async def defense_shop_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    defense_text = f"""
🛡 **سیستم پدافند**

💰 **موجودی شما**: {user['zp']:,} ZP

• سپر-۹۵ - 2,000 ZP
• سدیفاکتور - 5,000 ZP
• توربوشیلد - 10,000 ZP
"""
    await message.answer(defense_text, reply_markup=kb.defense_menu())

# خرید موشک
@dp.message(F.text.in_(["تیرباران", "رعدآسا", "تندباد"]))
async def buy_missile_cmd(message: types.Message):
    missile_name = message.text
    user_id = message.from_user.id
    
    if missile_name in SHOP_ITEMS["موشک‌ها"]:
        item_data = SHOP_ITEMS["موشک‌ها"][missile_name]
        user = db.get_user(user_id)
        
        if not db.can_afford(user_id, item_data['price']):
            await message.answer(
                f"❌ **موجودی ناکافی!**\n\n"
                f"قیمت {missile_name}: {item_data['price']:,} ZP\n"
                f"موجودی شما: {user['zp']:,} ZP",
                reply_markup=kb.missiles_menu()
            )
            return
        
        if db.purchase_item(user_id, item_data['price']):
            db.add_missile(user_id, missile_name, 1)
            new_count = user['missiles'][missile_name]
            
            response = f"✅ **خرید موفق!**\n\n🚀 {missile_name} خریداری شد\n💰 هزینه: {item_data['price']:,} ZP\n📦 تعداد: {new_count} عدد\n💎 موجودی جدید: {user['zp']:,} ZP"
            await message.answer(response, reply_markup=kb.shop_main_menu())

# خرید جنگنده
@dp.message(F.text.in_(["شب‌پرواز", "توفان‌ساز", "آذرخش"]))
async def buy_fighter_cmd(message: types.Message):
    fighter_name = message.text
    user_id = message.from_user.id
    
    if fighter_name in SHOP_ITEMS["جنگنده‌ها"]:
        item_data = SHOP_ITEMS["جنگنده‌ها"][fighter_name]
        user = db.get_user(user_id)
        
        if not db.can_afford(user_id, item_data['price']):
            await message.answer(
                f"❌ **موجودی ناکافی!**\n\n"
                f"قیمت {fighter_name}: {item_data['price']:,} ZP\n"
                f"موجودی شما: {user['zp']:,} ZP",
                reply_markup=kb.fighters_menu()
            )
            return
        
        if fighter_name in user['fighters']:
            await message.answer(
                f"❌ **شما قبلاً این جنگنده را دارید!**",
                reply_markup=kb.fighters_menu()
            )
            return
        
        if db.purchase_item(user_id, item_data['price']):
            db.add_fighter(user_id, fighter_name)
            response = f"✅ **خرید موفق!**\n\n🛩 {fighter_name} خریداری شد\n💰 هزینه: {item_data['price']:,} ZP\n💎 موجودی جدید: {user['zp']:,} ZP"
            await message.answer(response, reply_markup=kb.shop_main_menu())

# خرید پهپاد
@dp.message(F.text.in_(["زنبورک", "سایفر", "ریزپرنده V"]))
async def buy_drone_cmd(message: types.Message):
    drone_name = message.text
    user_id = message.from_user.id
    
    if drone_name in SHOP_ITEMS["پهپادها"]:
        item_data = SHOP_ITEMS["پهپادها"][drone_name]
        user = db.get_user(user_id)
        
        if not db.can_afford(user_id, item_data['price']):
            await message.answer(
                f"❌ **موجودی ناکافی!**\n\n"
                f"قیمت {drone_name}: {item_data['price']:,} ZP\n"
                f"موجودی شما: {user['zp']:,} ZP",
                reply_markup=kb.drones_menu()
            )
            return
        
        if drone_name in user['drones']:
            await message.answer(
                f"❌ **شما قبلاً این پهپاد را دارید!**",
                reply_markup=kb.drones_menu()
            )
            return
        
        if db.purchase_item(user_id, item_data['price']):
            db.add_drone(user_id, drone_name)
            response = f"✅ **خرید موفق!**\n\n🛸 {drone_name} خریداری شد\n💰 هزینه: {item_data['price']:,} ZP\n💎 موجودی جدید: {user['zp']:,} ZP"
            await message.answer(response, reply_markup=kb.shop_main_menu())

# خرید پدافند
@dp.message(F.text.in_(["سپر-۹۵", "سدیفاکتور", "توربوشیلد"]))
async def buy_defense_cmd(message: types.Message):
    defense_name = message.text
    user_id = message.from_user.id
    
    if defense_name in SHOP_ITEMS["پدافند"]:
        item_data = SHOP_ITEMS["پدافند"][defense_name]
        user = db.get_user(user_id)
        
        if not db.can_afford(user_id, item_data['price']):
            await message.answer(
                f"❌ **موجودی ناکافی!**\n\n"
                f"قیمت {defense_name}: {item_data['price']:,} ZP\n"
                f"موجودی شما: {user['zp']:,} ZP",
                reply_markup=kb.defense_menu()
            )
            return
        
        if db.purchase_item(user_id, item_data['price']):
            user['defense_level'] += 1
            response = f"✅ **خرید موفق!**\n\n🛡 {defense_name} خریداری شد\n💰 هزینه: {item_data['price']:,} ZP\n🛡️ سطح دفاع جدید: {user['defense_level']}\n💎 موجودی جدید: {user['zp']:,} ZP"
            await message.answer(response, reply_markup=kb.shop_main_menu())

# ==================== سیستم باکس ====================
@dp.message(F.text == "📦 باکس")
async def boxes_cmd(message: types.Message):
    boxes_text = """
📦 **جعبه‌های شانس**

📦 جعبه برنزی - رایگان
🥈 جعبه نقره‌ای - 5,000 ZP

👇 نوع جعبه را انتخاب کنید:
"""
    await message.answer(boxes_text, reply_markup=kb.boxes_menu())

@dp.message(F.text == "📦 برنزی")
async def bronze_box_cmd(message: types.Message):
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

@dp.message(F.text == "🥈 نقره‌ای")
async def silver_box_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    price = 5000
    
    if user['zp'] >= price:
        db.update_user_zp(message.from_user.id, -price)
        reward = random.randint(200, 500)
        new_balance = db.update_user_zp(message.from_user.id, reward)
        
        response = f"🥈 **جعبه نقره‌ای** 🎉\n\n💰 **هزینه**: {price:,} ZP\n💰 **جایزه**: {reward} ZP\n💎 **موجودی جدید**: {new_balance:,} ZP"
    else:
        response = f"❌ **موجودی ناکافی**\n\n💰 **قیمت جعبه**: {price:,} ZP\n💎 **موجودی شما**: {user['zp']:,} ZP"
    
    await message.answer(response, reply_markup=kb.main_menu())

# ==================== سیستم ادمین ====================
@dp.message(F.text == "📊 آمار بات")
async def admin_stats_cmd(message: types.Message):
    if not db.is_admin(message.from_user.id):
        return
    
    stats = db.get_all_stats()
    stats_text = f"""
📈 **آمار کلی WarZone**

👥 **کاربران**: {stats['total_users']}
⚔️ **حملات**: {stats['total_attacks']}
💥 **دمیج کل**: {stats['total_damage']:,}

🕒 **زمان**: {datetime.now().strftime('%H:%M:%S')}
"""
    await message.answer(stats_text, reply_markup=kb.admin_menu())

@dp.message(F.text == "👥 مدیریت کاربران")
async def admin_users_cmd(message: types.Message):
    if not db.is_admin(message.from_user.id):
        return
    
    users_text = """
👥 **مدیریت کاربران**

➕ افزودن ZP
💎 افزودن جم  
⭐ افزودن لول
📊 اطلاعات کاربر
"""
    await message.answer(users_text, reply_markup=kb.admin_users_menu())

@dp.message(F.text == "📢 ارسال همگانی")
async def admin_broadcast_cmd(message: types.Message):
    if not db.is_admin(message.from_user.id):
        return
    
    user_admin_state[message.from_user.id] = {'action': 'broadcast'}
    await message.answer(
        "📢 **ارسال پیام همگانی**\n\n"
        "لطفاً پیام خود را ارسال کنید:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="🔙 بازگشت به پنل ادمین")]],
            resize_keyboard=True
        )
    )

# پردازش ارسال همگانی
@dp.message(F.text & ~F.text.startswith('/') & ~F.text.startswith('🔙'))
async def process_broadcast_cmd(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in user_admin_state and user_admin_state[user_id]['action'] == 'broadcast':
        users = db.users
        success_count = 0
        
        for user_data in users.values():
            try:
                await bot.send_message(
                    user_data['user_id'],
                    f"📢 **پیام همگانی از مدیریت**\n\n{message.text}"
                )
                success_count += 1
            except:
                pass
        
        response = f"✅ **پیام همگانی ارسال شد!**\n\n✅ موفق: {success_count}\n👥 کل کاربران: {len(users)}"
        await message.answer(response, reply_markup=kb.admin_menu())
        del user_admin_state[user_id]

# ==================== سیستم پشتیبانی ====================
@dp.message(F.text == "📞 پشتیبانی")
async def support_cmd(message: types.Message):
    support_text = """
📞 **پشتیبانی WarZone**

📩 ارسال تیکت
📋 تیکت‌های من  
🆘 راهنمای سریع
"""
    await message.answer(support_text, reply_markup=kb.support_menu())

# ==================== بازگشت‌ها ====================
@dp.message(F.text.contains("بازگشت"))
async def back_cmd(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in user_admin_state:
        del user_admin_state[user_id]
    
    if message.text == "🔙 بازگشت":
        if db.is_admin(user_id):
            await message.answer("🔙 به منوی اصلی بازگشتید", reply_markup=kb.admin_menu())
        else:
            await message.answer("🔙 به منوی اصلی بازگشتید", reply_markup=kb.main_menu())
    
    elif message.text == "🔙 بازگشت به فروشگاه":
        await message.answer("🔙 به فروشگاه بازگشتید", reply_markup=kb.shop_main_menu())
    
    elif message.text == "🔙 بازگشت به پنل ادمین":
        await message.answer("🔙 به پنل ادمین بازگشتید", reply_markup=kb.admin_menu())

# ==================== هندلر پیش‌فرض ====================
@dp.message()
async def echo_cmd(message: types.Message):
    await message.answer("از منوی زیر انتخاب کنید:", reply_markup=kb.main_menu())

# ==================== تابع اصلی ====================
async def main():
    logger.info("🤖 بات WarZone در حال راه‌اندازی...")
    print("✅ همه هندلرها ثبت شدند")
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted")
        await dp.start_polling(bot)
        print("✅ Polling started successfully")
    except Exception as e:
        logger.error(f"❌ خطا: {e}")

if __name__ == "__main__":
    asyncio.run(main())
