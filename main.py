# main.py - WarZone Bot نسخه کامل با Keep Alive
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
from database_stable import db

print("🚀 شروع WarZone Bot...")

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
user_states = {}

# ==================== KEEP ALIVE SYSTEM ====================
keep_alive_running = True

async def keep_alive():
    """سیستم Keep Alive برای Railway"""
    print("🔗 سیستم Keep Alive فعال شد")
    
    while keep_alive_running:
        try:
            # هر 30 ثانیه یکبار بات رو چک کن
            await asyncio.sleep(30)
            
            # تست اتصال با گرفتن اطلاعات بات
            me = await bot.get_me()
            print(f"✅ Keep Alive - بات فعال: @{me.username}")
            
            # لاگ زمان
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"🕒 آخرین Keep Alive: {current_time}")
            
        except Exception as e:
            print(f"⚠️ Keep Alive خطا: {e}")
            
            # تلاش مجدد بعد از 10 ثانیه
            await asyncio.sleep(10)

# ==================== دستورات اصلی ====================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    username = message.from_user.username or message.from_user.first_name
    
    if db.is_admin(message.from_user.id):
        menu = kb.admin_menu()
        admin_text = "\n\n👑 **شما ادمین هستید**"
    else:
        menu = kb.main_menu()
        admin_text = ""
    
    welcome = f"""🎯 **به WarZone خوش آمدید {username}!** ⚔️

💰 موجودی: {user['zp']:,} ZP
⭐ سطح: {user['level']}
💪 قدرت: {user['power']}
{admin_text}

👇 از منوی زیر انتخاب کنید:"""
    
    await message.answer(welcome, reply_markup=menu)
    print(f"✅ کاربر {message.from_user.id} استارت زد")

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    help_text = """🆘 **راهنمای WarZone**

👤 پروفایل - اطلاعات حساب
🛒 فروشگاه - خرید تجهیزات  
⚔️ حمله - سیستم‌های حمله
📦 باکس - جعبه‌های شانس
⛏ ماینر - سیستم درآمد خودکار
🦠 خرابکاری - تیم‌های خرابکاری
🏢 برج امنیت - سیستم دفاع سایبری
🏆 لیگ - سیستم رقابتی
📞 پشتیبانی - ارسال تیکت"""
    await message.answer(help_text, reply_markup=kb.main_menu())

@dp.message(Command("test"))
async def test_cmd(message: types.Message):
    """تست بات و Keep Alive"""
    current_time = datetime.now().strftime("%H:%M:%S")
    
    await message.answer(
        f"✅ **بات WarZone فعال است!**\n\n"
        f"🕒 زمان سرور: {current_time}\n"
        f"🔗 Keep Alive: فعال\n"
        f"✅ وضعیت: آنلاین"
    )

@dp.message(Command("ping"))
async def ping_cmd(message: types.Message):
    """بررسی سرعت پاسخگویی"""
    start_time = time.time()
    msg = await message.answer("🏓 در حال پینگ...")
    end_time = time.time()
    latency = (end_time - start_time) * 1000
    
    await msg.edit_text(f"🏓 پونگ!\n⏱ زمان پاسخ: {latency:.0f}ms")

# ==================== پروفایل ====================
@dp.message(F.text == "👤 پروفایل")
async def profile_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    profile = f"""👤 **پروفایل جنگجو**

⭐ سطح: {user['level']}
💰 ZP: {user['zp']:,}
💎 جم: {user['gem']}
💪 قدرت: {user['power']}

🎯 حملات: {user['total_attacks']:,}
💥 دمیج کل: {user['total_damage']:,}
🛩 جنگنده‌ها: {len(user['fighters'])}
🛸 پهپادها: {len(user['drones'])}
🦠 تیم خرابکاری: {len(user['sabotage_teams'])}
🏢 برج امنیت: لول {user['cyber_level']}"""
    
    await message.answer(profile, reply_markup=kb.main_menu())

# ==================== سیستم حمله ====================
@dp.message(F.text == "⚔️ حمله")
async def attack_cmd(message: types.Message):
    await message.answer("⚔️ **سیستم حمله**\n\n👇 نوع حمله را انتخاب کنید:", reply_markup=kb.attack_menu())

@dp.message(F.text == "🎯 حمله تکی")
async def single_attack(message: types.Message):
    user = db.get_user(message.from_user.id)
    reward = random.randint(50, 100)
    new_balance = db.update_user_zp(message.from_user.id, reward)
    user['total_attacks'] += 1
    user['total_damage'] += reward
    
    response = f"⚔️ **حمله تکی موفق!**\n\n💰 جایزه: {reward} ZP\n💎 موجودی جدید: {new_balance:,} ZP"
    await message.answer(response, reply_markup=kb.main_menu())

@dp.message(F.text == "💥 حمله ترکیبی")
async def combo_attack(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user['fighters']:
        await message.answer("❌ جنگنده ندارید! به فروشگاه مراجعه کنید.", reply_markup=kb.main_menu())
        return
    
    damage = random.randint(80, 150) + (len(user['fighters']) * 50)
    reward = damage
    new_balance = db.update_user_zp(message.from_user.id, reward)
    user['total_attacks'] += 1
    user['total_damage'] += damage
    
    response = f"💥 **حمله ترکیبی موفق!**\n\n💥 دمیج: {damage}\n💰 جایزه: {reward} ZP\n💎 موجودی جدید: {new_balance:,} ZP"
    await message.answer(response, reply_markup=kb.main_menu())

@dp.message(F.text == "🛸 حمله پهپادی")
async def drone_attack(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user['drones']:
        await message.answer("❌ پهپاد ندارید! به فروشگاه مراجعه کنید.", reply_markup=kb.main_menu())
        return
    
    damage = random.randint(60, 120) + (len(user['drones']) * 30)
    reward = damage
    new_balance = db.update_user_zp(message.from_user.id, reward)
    user['total_attacks'] += 1
    user['total_damage'] += damage
    
    response = f"🛸 **حمله پهپادی موفق!**\n\n💥 دمیج: {damage}\n💰 جایزه: {reward} ZP\n💎 موجودی جدید: {new_balance:,} ZP"
    await message.answer(response, reply_markup=kb.main_menu())

@dp.message(F.text == "🛡 حمله به مدافع")
async def defense_attack(message: types.Message):
    user = db.get_user(message.from_user.id)
    if user['defense_level'] <= 1 and user['cyber_level'] <= 1:
        await message.answer("❌ هیچ مدافعی برای حمله پیدا نشد!", reply_markup=kb.main_menu())
        return
    
    base_damage = random.randint(100, 200)
    defense_reduction = user['defense_level'] * 10
    cyber_bonus = CYBER_TOWER[user['cyber_level']]['defense_bonus']
    total_reduction = defense_reduction + cyber_bonus
    actual_damage = max(50, base_damage - total_reduction)
    reward = actual_damage
    new_balance = db.update_user_zp(message.from_user.id, reward)
    user['total_attacks'] += 1
    user['total_damage'] += actual_damage
    
    response = f"🛡 **حمله به مدافع موفق!**\n\n💥 دمیج: {actual_damage}\n💰 جایزه: {reward} ZP\n💎 موجودی جدید: {new_balance:,} ZP"
    await message.answer(response, reply_markup=kb.main_menu())

# ==================== فروشگاه ====================
@dp.message(F.text == "🛒 فروشگاه")
async def shop_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    shop_text = f"""🛒 **فروشگاه WarZone**

💰 موجودی شما: {user['zp']:,} ZP

👇 دسته مورد نظر را انتخاب کنید:"""
    await message.answer(shop_text, reply_markup=kb.shop_main_menu())

@dp.message(F.text == "🚀 موشک‌ها")
async def missiles_shop(message: types.Message):
    user = db.get_user(message.from_user.id)
    text = f"""🚀 **موشک‌های موجود**

💰 موجودی شما: {user['zp']:,} ZP

• تیرباران - 400 ZP
• رعدآسا - 700 ZP  
• تندباد - 1,000 ZP
• زلزله - 1,500 ZP
• آتشفشان - 8,000 ZP
• توفان‌نو - 15,000 ZP"""
    await message.answer(text, reply_markup=kb.missiles_menu())

@dp.message(F.text == "🛩 جنگنده‌ها")
async def fighters_shop(message: types.Message):
    user = db.get_user(message.from_user.id)
    text = f"""🛩 **جنگنده‌های موجود**

💰 موجودی شما: {user['zp']:,} ZP

• شب‌پرواز - 5,000 ZP
• توفان‌ساز - 8,000 ZP
• آذرخش - 12,000 ZP
• شبح‌ساحل - 18,000 ZP"""
    await message.answer(text, reply_markup=kb.fighters_menu())

@dp.message(F.text == "🛸 پهپادها")
async def drones_shop(message: types.Message):
    user = db.get_user(message.from_user.id)
    text = f"""🛸 **پهپادهای موجود**

💰 موجودی شما: {user['zp']:,} ZP

• زنبورک - 3,000 ZP
• سایفر - 5,000 ZP
• ریزپرنده V - 8,000 ZP"""
    await message.answer(text, reply_markup=kb.drones_menu())

@dp.message(F.text == "🛡 پدافند")
async def defense_shop(message: types.Message):
    user = db.get_user(message.from_user.id)
    text = f"""🛡 **سیستم پدافند**

💰 موجودی شما: {user['zp']:,} ZP

• سپر-۹۵ - 2,000 ZP
• سدیفاکتور - 5,000 ZP
• توربوشیلد - 10,000 ZP
• لایه نوری - 20,000 ZP
• پدافند افسانه‌ای - 50,000 ZP"""
    await message.answer(text, reply_markup=kb.defense_menu())

# خرید موشک
@dp.message(F.text.in_(["تیرباران", "رعدآسا", "تندباد", "زلزله", "آتشفشان", "توفان‌نو"]))
async def buy_missile(message: types.Message):
    item_name = message.text
    user_id = message.from_user.id
    
    if item_name in SHOP_ITEMS["موشک‌ها"]:
        price = SHOP_ITEMS["موشک‌ها"][item_name]['price']
        user = db.get_user(user_id)
        
        if user['zp'] >= price:
            db.update_user_zp(user_id, -price)
            db.add_missile(user_id, item_name, 1)
            response = f"✅ **خرید موفق!**\n\n🚀 {item_name} خریداری شد\n💰 هزینه: {price:,} ZP\n💎 موجودی جدید: {user['zp']-price:,} ZP"
        else:
            response = f"❌ موجودی ناکافی!\nقیمت: {price:,} ZP\nموجودی شما: {user['zp']:,} ZP"
        
        await message.answer(response, reply_markup=kb.shop_main_menu())

# خرید جنگنده
@dp.message(F.text.in_(["شب‌پرواز", "توفان‌ساز", "آذرخش", "شبح‌ساحل"]))
async def buy_fighter(message: types.Message):
    item_name = message.text
    user_id = message.from_user.id
    
    if item_name in SHOP_ITEMS["جنگنده‌ها"]:
        price = SHOP_ITEMS["جنگنده‌ها"][item_name]['price']
        user = db.get_user(user_id)
        
        if user['zp'] >= price:
            if item_name not in user['fighters']:
                db.update_user_zp(user_id, -price)
                db.add_fighter(user_id, item_name)
                response = f"✅ **خرید موفق!**\n\n🛩 {item_name} خریداری شد\n💰 هزینه: {price:,} ZP\n💎 موجودی جدید: {user['zp']-price:,} ZP"
            else:
                response = "❌ قبلاً این جنگنده را دارید!"
        else:
            response = f"❌ موجودی ناکافی!\nقیمت: {price:,} ZP\nموجودی شما: {user['zp']:,} ZP"
        
        await message.answer(response, reply_markup=kb.shop_main_menu())

# خرید پهپاد
@dp.message(F.text.in_(["زنبورک", "سایفر", "ریزپرنده V"]))
async def buy_drone(message: types.Message):
    item_name = message.text
    user_id = message.from_user.id
    
    if item_name in SHOP_ITEMS["پهپادها"]:
        price = SHOP_ITEMS["پهپادها"][item_name]['price']
        user = db.get_user(user_id)
        
        if user['zp'] >= price:
            if item_name not in user['drones']:
                db.update_user_zp(user_id, -price)
                db.add_drone(user_id, item_name)
                response = f"✅ **خرید موفق!**\n\n🛸 {item_name} خریداری شد\n💰 هزینه: {price:,} ZP\n💎 موجودی جدید: {user['zp']-price:,} ZP"
            else:
                response = "❌ قبلاً این پهپاد را دارید!"
        else:
            response = f"❌ موجودی ناکافی!\nقیمت: {price:,} ZP\nموجودی شما: {user['zp']:,} ZP"
        
        await message.answer(response, reply_markup=kb.shop_main_menu())

# خرید پدافند
@dp.message(F.text.in_(["سپر-۹۵", "سدیفاکتور", "توربوشیلد", "لایه نوری", "پدافند افسانه‌ای"]))
async def buy_defense(message: types.Message):
    item_name = message.text
    user_id = message.from_user.id
    
    if item_name in SHOP_ITEMS["پدافند"]:
        price = SHOP_ITEMS["پدافند"][item_name]['price']
        user = db.get_user(user_id)
        
        if user['zp'] >= price:
            db.update_user_zp(user_id, -price)
            user['defense_level'] += 1
            response = f"✅ **خرید موفق!**\n\n🛡 {item_name} خریداری شد\n💰 هزینه: {price:,} ZP\n🛡️ سطح دفاع جدید: {user['defense_level']}\n💎 موجودی جدید: {user['zp']-price:,} ZP"
        else:
            response = f"❌ موجودی ناکافی!\nقیمت: {price:,} ZP\nموجودی شما: {user['zp']:,} ZP"
        
        await message.answer(response, reply_markup=kb.shop_main_menu())

# ==================== سیستم باکس ====================
@dp.message(F.text == "📦 باکس")
async def boxes_cmd(message: types.Message):
    text = """📦 **جعبه‌های شانس**

📦 جعبه برنزی - رایگان
🥈 جعبه نقره‌ای - 5,000 ZP

👇 نوع جعبه را انتخاب کنید:"""
    await message.answer(text, reply_markup=kb.boxes_menu())

@dp.message(F.text == "📦 برنزی")
async def bronze_box(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    if db.can_open_bronze_box(message.from_user.id):
        if random.random() > 0.3:
            reward = random.randint(50, 200)
            new_balance = db.update_user_zp(message.from_user.id, reward)
            response = f"📦 **جعبه برنزی** 🎉\n\n💰 جایزه: {reward} ZP\n💎 موجودی جدید: {new_balance:,} ZP"
        else:
            missile = random.choice(["تیرباران", "رعدآسا"])
            db.add_missile(message.from_user.id, missile)
            response = f"📦 **جعبه برنزی** 🎉\n\n🚀 جایزه: ۱ عدد {missile}"
        
        db.set_bronze_box_time(message.from_user.id)
    else:
        response = "⏳ جعبه برنزی آماده نیست! 24 ساعت صبر کنید."
    
    await message.answer(response, reply_markup=kb.main_menu())

@dp.message(F.text == "🥈 نقره‌ای")
async def silver_box(message: types.Message):
    user = db.get_user(message.from_user.id)
    price = 5000
    
    if user['zp'] >= price:
        db.update_user_zp(message.from_user.id, -price)
        reward = random.randint(200, 500)
        new_balance = db.update_user_zp(message.from_user.id, reward)
        response = f"🥈 **جعبه نقره‌ای** 🎉\n\n💰 هزینه: {price:,} ZP\n💰 جایزه: {reward} ZP\n💎 موجودی جدید: {new_balance:,} ZP"
    else:
        response = f"❌ موجودی ناکافی!\nقیمت: {price:,} ZP\nموجودی شما: {user['zp']:,} ZP"
    
    await message.answer(response, reply_markup=kb.main_menu())

# ==================== سیستم ماینر ====================
@dp.message(F.text == "⛏ ماینر")
async def miner_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    current_time = time.time()
    time_since_last = current_time - user.get('miner_last_collect', 0)
    
    if time_since_last >= 3600:
        collectable = int((time_since_last / 3600) * (user['miner_level'] * 10))
        text = f"""⛏ **سیستم ماینر**

💰 موجودی ماینر: {user['miner_balance']:,} ZP
📊 سطح ماینر: {user['miner_level']}
✅ آماده جمع‌آوری: {collectable:,} ZP

🔄 /collect برای جمع‌آوری"""
    else:
        remaining = 3600 - time_since_last
        minutes = int(remaining // 60)
        text = f"""⛏ **سیستم ماینر**

💰 موجودی ماینر: {user['miner_balance']:,} ZP
📊 سطح ماینر: {user['miner_level']}
⏳ زمان باقی‌مانده: {minutes} دقیقه"""
    
    await message.answer(text, reply_markup=kb.main_menu())

@dp.message(Command("collect"))
async def collect_miner(message: types.Message):
    user = db.get_user(message.from_user.id)
    current_time = time.time()
    time_since_last = current_time - user.get('miner_last_collect', 0)
    
    if time_since_last >= 3600:
        collectable = int((time_since_last / 3600) * (user['miner_level'] * 10))
        db.update_user_zp(message.from_user.id, collectable)
        user['miner_last_collect'] = current_time
        response = f"✅ **جمع‌آوری موفق!**\n\n💰 {collectable:,} ZP دریافت کردید!"
    else:
        remaining = 3600 - time_since_last
        minutes = int(remaining // 60)
        response = f"⏳ {minutes} دقیقه تا جمع‌آوری بعدی"
    
    await message.answer(response, reply_markup=kb.main_menu())

# ==================== سیستم خرابکاری ====================
@dp.message(F.text == "🦠 خرابکاری")
async def sabotage_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    text = f"""🦠 **سیستم خرابکاری**

🔧 تعداد تیم‌ها: {len(user['sabotage_teams'])}
"""
    
    if user['sabotage_teams']:
        for i, team_level in enumerate(user['sabotage_teams']):
            team_data = SABOTAGE_TEAMS[team_level]
            text += f"\n{i+1}. {team_data['name']} (لول {team_level})"
    else:
        text += "\n❌ هیچ تیمی ندارید"
    
    text += "\n\n👇 اقدامات موجود:"
    
    if len(user['sabotage_teams']) > 0:
        text += "\n⚔️ حمله خرابکاری (/sabotage_attack)"
    if len(user['sabotage_teams']) < 5:
        text += "\n👥 استخدام تیم جدید (/hire_sabotage)"
    if user['sabotage_teams']:
        text += "\n⬆️ ارتقای تیم (/upgrade_sabotage)"
    
    await message.answer(text, reply_markup=kb.main_menu())

@dp.message(Command("hire_sabotage"))
async def hire_sabotage(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    if len(user['sabotage_teams']) >= 5:
        await message.answer("❌ حداکثر 5 تیم می‌توانید داشته باشید!", reply_markup=kb.main_menu())
        return
    
    cost = 2000
    if user['zp'] >= cost:
        db.update_user_zp(message.from_user.id, -cost)
        db.add_sabotage_team(message.from_user.id, 1)
        await message.answer("✅ **تیم خرابکاری لول 1 استخدام شد!**", reply_markup=kb.main_menu())
    else:
        await message.answer(f"❌ موجودی ناکافی! نیاز به {cost:,} ZP", reply_markup=kb.main_menu())

@dp.message(Command("upgrade_sabotage"))
async def upgrade_sabotage(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    if not user['sabotage_teams']:
        await message.answer("❌ هیچ تیم خرابکاری ندارید!", reply_markup=kb.main_menu())
        return
    
    for i, team_level in enumerate(user['sabotage_teams']):
        if team_level < 10:
            upgrade_cost = SABOTAGE_TEAMS[team_level]['upgrade_cost']
            if user['zp'] >= upgrade_cost:
                success, new_level = db.upgrade_sabotage_team(message.from_user.id, i)
                if success:
                    db.update_user_zp(message.from_user.id, -upgrade_cost)
                    await message.answer(f"✅ تیم {i+1} به لول {new_level} ارتقا یافت!", reply_markup=kb.main_menu())
                    return
    
    await message.answer("✅ همه تیم‌ها در حداکثر لول هستند!", reply_markup=kb.main_menu())

@dp.message(Command("sabotage_attack"))
async def sabotage_attack(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    if not user['sabotage_teams']:
        await message.answer("❌ هیچ تیم خرابکاری ندارید!", reply_markup=kb.main_menu())
        return
    
    total_success = sum(SABOTAGE_TEAMS[team]['success_rate'] for team in user['sabotage_teams'])
    avg_success = total_success / len(user['sabotage_teams'])
    
    if random.random() < avg_success:
        reward = 500 * len(user['sabotage_teams'])
        db.update_user_zp(message.from_user.id, reward)
        response = f"✅ **حمله موفق!**\n\n💰 جایزه: {reward:,} ZP"
    else:
        response = "❌ **حمله شکست خورد!**\n\n🔄 دوباره تلاش کنید"
    
    await message.answer(response, reply_markup=kb.main_menu())

# ==================== سیستم برج امنیت ====================
@dp.message(F.text == "🏢 برج امنیت")
async def cyber_tower_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    current_level = user['cyber_level']
    tower_data = CYBER_TOWER[current_level]
    
    text = f"""🏢 **برج امنیت سایبری**

🏷 نام: {tower_data['name']}
⭐ سطح: {current_level}/10
🛡 مزیت دفاعی: +{tower_data['defense_bonus']} قدرت
"""
    
    if current_level < 10:
        text += f"\n⬆️ ارتقا به سطح {current_level + 1}\n💰 هزینه: {tower_data['upgrade_cost']:,} ZP\n\n🔧 /upgrade_cyber برای ارتقا"
    else:
        text += "\n🎉 **حداکثر سطح رسیده‌اید!**"
    
    await message.answer(text, reply_markup=kb.main_men
