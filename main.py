# main.py - WarZone Bot Complete با سیستم بکاپ
import os
import asyncio
import logging
import sys
import random
import time
from datetime import datetime
from aiohttp import web  # <-- جدید

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import keyboards as kb
from config import SHOP_ITEMS, ATTACK_TYPES, ADMINS, SABOTAGE_TEAMS, CYBER_TOWER
from database_stable import db
from backup_manager import backup_mgr, auto_backup

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

# ==================== HEALTH CHECK برای Railway ====================
async def health_check(request):
    return web.Response(text="✅ بات WarZone فعال است")

# ایجاد اپلیکیشن aiohttp
app = web.Application()
app.router.add_get('/health', health_check)
print("🌐 Health check endpoint ایجاد شد")

# ==================== هندلر خطای عمومی ====================
@dp.error()
async def error_handler(update: types.Update, exception: Exception):
    logger.error(f"⚠️ خطا در پردازش آپدیت: {exception}")
    try:
        # سعی کن به کاربر اطلاع بدی
        if update.message:
            await update.message.answer("⚠️ خطایی رخ داد! لطفاً دوباره تلاش کنید.")
    except:
        pass
    return True

# ==================== وضعیت کاربران ====================
user_purchase_state = {}
user_admin_state = {}

# شروع سیستم بکاپ خودکار
auto_backup.start()
print("🔄 سیستم بکاپ خودکار فعال شد")

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

# ==================== تست بات ====================
@dp.message(Command("test"))
async def test_cmd(message: types.Message):
    """دستور تست برای بررسی فعال بودن بات"""
    await message.answer("✅ بات WarZone فعال و آماده است!")
    print(f"✅ تست موفق از کاربر {message.from_user.id}")

@dp.message(Command("ping"))
async def ping_cmd(message: types.Message):
    """بررسی latency"""
    start_time = time.time()
    msg = await message.answer("🏓 پینگ...")
    end_time = time.time()
    latency = (end_time - start_time) * 1000
    
    await msg.edit_text(f"🏓 پونگ!\n⏱ زمان پاسخ: {latency:.0f}ms\n✅ بات فعال است")
    
# بقیه کدها دقیقاً مثل قبل...
# [کدهای باقی‌مانده رو اینجا paste کن]# main.py - WarZone Bot Complete با سیستم بکاپ
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
from config import SHOP_ITEMS, ATTACK_TYPES, ADMINS, SABOTAGE_TEAMS, CYBER_TOWER
from database_stable import db  # تغییر شده
from backup_manager import backup_mgr, auto_backup  # جدید

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

# شروع سیستم بکاپ خودکار
auto_backup.start()
print("🔄 سیستم بکاپ خودکار فعال شد")

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
⛏ ماینر - سیستم درآمد خودکار
🦠 خرابکاری - تیم‌های خرابکاری
🏢 برج امنیت - سیستم دفاع سایبری
🏆 لیگ - سیستم رقابتی
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
🎁 هدیه همگانی
💾 مدیریت بکاپ
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
🦠 **تیم خرابکاری**: {len(user['sabotage_teams'])}
🏢 **برج امنیت**: لول {user['cyber_level']}
"""
    await message.answer(profile_text, reply_markup=kb.main_menu())

# ==================== سیستم حمله ====================
@dp.message(F.text == "⚔️ حمله")
async def attack_cmd(message: types.Message):
    await message.answer(
        "⚔️ **سیستم حمله**\n\n"
        "🎯 حمله تکی\n"
        "💥 حمله ترکیبی\n"
        "🛸 حمله پهپادی\n"
        "🛡 حمله به مدافع\n\n"
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

@dp.message(F.text == "🛡 حمله به مدافع")
async def defense_attack_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # بررسی آیا کاربر مدافع داره
    if user['defense_level'] <= 1 and user['cyber_level'] <= 1:
        await message.answer(
            "❌ **هیچ مدافعی برای حمله پیدا نشد!**\n\n"
            "کاربران باید سیستم پدافند یا برج امنیت داشته باشند.",
            reply_markup=kb.main_menu()
        )
        return
    
    base_damage = random.randint(100, 200)
    
    # محاسبه کاهش دمیج توسط دفاع و برج امنیت
    defense_reduction = user['defense_level'] * 10
    cyber_bonus = CYBER_TOWER[user['cyber_level']]['defense_bonus']
    total_reduction = defense_reduction + cyber_bonus
    
    actual_damage = max(50, base_damage - total_reduction)
    
    reward = actual_damage
    xp_gain = random.randint(20, 30)
    
    new_balance = db.update_user_zp(message.from_user.id, reward)
    user['total_attacks'] += 1
    user['total_damage'] += actual_damage
    
    response = (
        f"🛡 **حمله به مدافع موفق!**\n\n"
        f"💥 دمیج: {actual_damage}\n"
        f"🛡 کاهش توسط دفاع: {defense_reduction}\n"
        f"🏢 کاهش توسط برج: {cyber_bonus}\n"
        f"💰 جایزه: {reward} ZP\n"
        f"⭐ XP: +{xp_gain}\n"
        f"💎 موجودی جدید: {new_balance:,} ZP"
    )
    
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
• زلزله - 1,500 ZP
• آتشفشان - 8,000 ZP
• توفان‌نو - 15,000 ZP
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
• شبح‌ساحل - 18,000 ZP
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
• لایه نوری - 20,000 ZP
• پدافند افسانه‌ای - 50,000 ZP
"""
    await message.answer(defense_text, reply_markup=kb.defense_menu())

# خرید موشک
@dp.message(F.text.in_(["تیرباران", "رعدآسا", "تندباد", "زلزله", "آتشفشان", "توفان‌نو"]))
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
@dp.message(F.text.in_(["شب‌پرواز", "توفان‌ساز", "آذرخش", "شبح‌ساحل"]))
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
@dp.message(F.text.in_(["سپر-۹۵", "سدیفاکتور", "توربوشیلد", "لایه نوری", "پدافند افسانه‌ای"]))
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

# ==================== سیستم خرابکاری پیشرفته ====================
@dp.message(F.text == "🦠 خرابکاری")
async def sabotage_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    sabotage_text = f"""
🦠 **سیستم خرابکاری**

🔧 **تعداد تیم‌ها**: {len(user['sabotage_teams'])}
🎯 **مجموع شانس موفقیت**: {sum(SABOTAGE_TEAMS[team]['success_rate'] for team in user['sabotage_teams']):.1%}

**تیم‌های شما:**
"""
    
    if user['sabotage_teams']:
        for i, team_level in enumerate(user['sabotage_teams']):
            team_data = SABOTAGE_TEAMS[team_level]
            sabotage_text += f"\n{i+1}. {team_data['name']} (لول {team_level}) - شانس: {team_data['success_rate']:.0%}"
    else:
        sabotage_text += "\n❌ هیچ تیمی ندارید"
    
    sabotage_text += "\n\n👇 اقدامات موجود:"
    
    if len(user['sabotage_teams']) > 0:
        sabotage_text += "\n⚔️ حمله خرابکاری (/sabotage_attack)"
    if len(user['sabotage_teams']) < 5:  # حداکثر 5 تیم
        sabotage_text += "\n👥 استخدام تیم جدید (/hire_sabotage)"
    if user['sabotage_teams']:
        sabotage_text += "\n⬆️ ارتقای تیم (/upgrade_sabotage)"
    
    await message.answer(sabotage_text, reply_markup=kb.main_menu())

@dp.message(Command("hire_sabotage"))
async def hire_sabotage_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    if len(user['sabotage_teams']) >= 5:
        await message.answer("❌ حداکثر 5 تیم می‌توانید داشته باشید!", reply_markup=kb.main_menu())
        return
    
    cost = 2000
    if user['zp'] < cost:
        await message.answer(f"❌ موجودی ناکافی! نیاز به {cost:,} ZP", reply_markup=kb.main_menu())
        return
    
    db.update_user_zp(message.from_user.id, -cost)
    db.add_sabotage_team(message.from_user.id, 1)  # تیم لول 1
    
    await message.answer(
        "✅ **تیم خرابکاری لول 1 استخدام شد!**\n\n"
        "🦠 اکنون می‌توانید حملات خرابکاری انجام دهید\n"
        "⬆️ یا تیم خود را ارتقا دهید",
        reply_markup=kb.main_menu()
    )

@dp.message(Command("upgrade_sabotage"))
async def upgrade_sabotage_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    if not user['sabotage_teams']:
        await message.answer("❌ هیچ تیم خرابکاری ندارید!", reply_markup=kb.main_menu())
        return
    
    # پیدا کردن اولین تیمی که می‌توان ارتقا داد
    for i, team_level in enumerate(user['sabotage_teams']):
        if team_level < 10:
            upgrade_cost = SABOTAGE_TEAMS[team_level]['upgrade_cost']
            
            if user['zp'] >= upgrade_cost:
                db.update_user_zp(message.from_user.id, -upgrade_cost)
                success, new_level = db.upgrade_sabotage_team(message.from_user.id, i)
                
                if success:
                    new_team_data = SABOTAGE_TEAMS[new_level]
                    await message.answer(
                        f"✅ **تیم خرابکاری ارتقا یافت!**\n\n"
                        f"🦠 تیم {i+1} به لول {new_level} رسید\n"
                        f"🏷 نام جدید: {new_team_data['name']}\n"
                        f"🎯 شانس جدید: {new_team_data['success_rate']:.0%}\n"
                        f"💰 هزینه: {upgrade_cost:,} ZP",
                        reply_markup=kb.main_menu()
                    )
                    return
            
            else:
                await message.answer(
                    f"❌ موجودی ناکافی! نیاز به {upgrade_cost:,} ZP",
                    reply_markup=kb.main_menu()
                )
                return
    
    await message.answer("✅ همه تیم‌های شما در حداکثر لول هستند! 🎉", reply_markup=kb.main_menu())

@dp.message(Command("sabotage_attack"))
async def sabotage_attack_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    if not user['sabotage_teams']:
        await message.answer("❌ هیچ تیم خرابکاری ندارید!", reply_markup=kb.main_menu())
        return
    
    # محاسبه میانگین شانس موفقیت
    total_success_rate = sum(SABOTAGE_TEAMS[team]['success_rate'] for team in user['sabotage_teams'])
    avg_success_rate = total_success_rate / len(user['sabotage_teams'])
    
    success = random.random() < avg_success_rate
    
    if success:
        base_reward = 500 * len(user['sabotage_teams'])
        bonus = sum(team * 100 for team in user['sabotage_teams'])
        total_reward = base_reward + bonus
        
        db.update_user_zp(message.from_user.id, total_reward)
        
        response = (
            f"✅ **حمله خرابکاری موفق!**\n\n"
            f"💰 جایزه: {total_reward:,} ZP\n"
            f"🎯 شانس موفقیت: {avg_success_rate:.1%}\n"
            f"🦠 همه تیم‌ها سالم ماندند"
        )
    else:
        # شانس از دست دادن یک تیم
        if random.random() < 0.3 and len(user['sabotage_teams']) > 1:
            lost_team_index = random.randint(0, len(user['sabotage_teams']) - 1)
            lost_team_level = user['sabotage_teams'].pop(lost_team_index)
            response = (
                f"❌ **حمله خرابکاری شکست خورد!**\n\n"
                f"💔 تیم لول {lost_team_level} از دست رفت\n"
                f"🎯 شانس موفقیت: {avg_success_rate:.1%}\n"
                f"🔄 تیم جدید استخدام کنید"
            )
        else:
            response = (
                f"❌ **حمله خرابکاری شکست خورد!**\n\n"
                f"🎯 شانس موفقیت: {avg_success_rate:.1%}\n"
                f"🦠 خوشبختانه هیچ تیمی از دست نرفت\n"
                f"🔄 دوباره تلاش کنید"
            )
    
    await message.answer(response, reply_markup=kb.main_menu())

# ==================== سیستم برج امنیت سایبری ====================
@dp.message(F.text == "🏢 برج امنیت")
async def cyber_tower_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    current_level = user['cyber_level']
    tower_data = CYBER_TOWER[current_level]
    
    cyber_text = f"""
🏢 **برج امنیت سایبری**

🏷 **نام**: {tower_data['name']}
⭐ **سطح**: {current_level}/10
🛡 **مزیت دفاعی**: +{tower_data['defense_bonus']} قدرت

"""
    
    if current_level < 10:
        next_level_data = CYBER_TOWER[current_level + 1]
        cyber_text += (
            f"⬆️ **ارتقا به سطح {current_level + 1}**\n"
            f"💰 هزینه: {tower_data['upgrade_cost']:,} ZP\n"
            f"🛡 مزیت جدید: +{next_level_data['defense_bonus']} قدرت\n\n"
            f"🔧 /upgrade_cyber برای ارتقا"
        )
    else:
        cyber_text += "🎉 **حداکثر سطح رسیده‌اید!** 🎉\n🏢 برج شما ضد ضربه است!"
    
    await message.answer(cyber_text, reply_markup=kb.main_menu())

@dp.message(Command("upgrade_cyber"))
async def upgrade_cyber_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    current_level = user['cyber_level']
    
    if current_level >= 10:
        await message.answer("🎉 برج شما در حداکثر سطح است! 🏢", reply_markup=kb.main_menu())
        return
    
    upgrade_cost = CYBER_TOWER[current_level]['upgrade_cost']
    
    if user['zp'] < upgrade_cost:
        await message.answer(f"❌ موجودی ناکافی! نیاز به {upgrade_cost:,} ZP", reply_markup=kb.main_menu())
        return
    
    db.update_user_zp(message.from_user.id, -upgrade_cost)
    success, new_level = db.upgrade_cyber_tower(message.from_user.id)
    
    if success:
        new_tower_data = CYBER_TOWER[new_level]
        await message.answer(
            f"✅ **برج امنیت ارتقا یافت!**\n\n"
            f"🏢 اکنون: {new_tower_data['name']}\n"
            f"⭐ سطح: {new_level}\n"
            f"🛡 مزیت دفاعی: +{new_tower_data['defense_bonus']} قدرت\n"
            f"💰 هزینه: {upgrade_cost:,} ZP",
            reply_markup=kb.main_menu()
    )
