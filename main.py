# main.py - WarZone Bot Complete با Healthcheck Railway
import os
import asyncio
import logging
import sys
import random
import time
from datetime import datetime
from aiohttp import web

print("🚀 شروع WarZone Bot...")

# بارگذاری متغیرهای محیطی
from dotenv import load_dotenv
load_dotenv()

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('warzone_bot.log')
    ]
)
logger = logging.getLogger(__name__)

# بررسی توکن
TOKEN = os.getenv("TELEGRAM_TOKEN")
print(f"🔍 بررسی توکن: {TOKEN[:10]}..." if TOKEN else "❌ توکن پیدا نشد")

# ایمپورت ماژول‌ها
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import keyboards as kb
from config import SHOP_ITEMS, ATTACK_TYPES, ADMINS, DEFENSE_SYSTEM, BOXES, MINER_CONFIG
from database import db

# ==================== HEALTHCHECK برای Railway ====================
async def health_check(request):
    """سرور سلامت برای Railway"""
    return web.Response(text="OK")

async def start_health_server():
    """شروع سرور سلامت"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"✅ سرور سلامت روی پورت {port} راه‌اندازی شد")
    return runner

# ==================== متغیرهای گلوبال ====================
bot = None
dp = None
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
⛏ ماینر - استخراج منابع
📦 باکس - جعبه‌های شانس
🏆 لیگ - سیستم رقابتی
🔧 خرابکاری - عملیات ویژه
🛡 مدافعان - مبارزه با دیگران
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
💾 ایجاد بکاپ
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
❤️ **سلامت**: {user.get('health', 500)}

🎯 **حملات**: {user['total_attacks']:,}
💥 **دمیج کل**: {user['total_damage']:,}
🛩 **جنگنده‌ها**: {len(user['fighters'])}
🛸 **پهپادها**: {len(user['drones'])}

🔧 **خرابکاری**: سطح {user.get('sabotage_level', 0)}
⛏ **ماینر**: سطح {user.get('miner_level', 1)}
🛡 **دفاع**: {user.get('active_defense', 'ندارد')}
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
    
    user['zp'] += reward
    user['total_attacks'] += 1
    user['total_damage'] += reward
    db.save_data()
    
    response = f"""
⚔️ **حمله تکی موفق!**

💰 **جایزه**: {reward} ZP
⭐ **XP**: +{xp_gain}
💎 **موجودی جدید**: {user['zp']:,} ZP
"""
    
    await message.answer(response, reply_markup=kb.main_menu())

@dp.message(F.text == "💥 حمله ترکیبی")
async def combo_attack_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    user_fighters = user.get('fighters', {})
    
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
    
    user['zp'] += reward
    user['total_attacks'] += 1
    user['total_damage'] += total_damage
    db.save_data()
    
    fighter_text = f" ({len(user_fighters)} جنگنده)"
    response = f"""
💥 **حمله ترکیبی موفق**{fighter_text}

💥 **دمیج**: {total_damage}
💰 **جایزه**: {reward} ZP
⭐ **XP**: +{xp_gain}
💎 **موجودی جدید**: {user['zp']:,} ZP
"""
    
    await message.answer(response, reply_markup=kb.main_menu())

@dp.message(F.text == "🛸 حمله پهپادی")
async def drone_attack_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    user_drones = user.get('drones', {})
    
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
    
    user['zp'] += reward
    user['total_attacks'] += 1
    user['total_damage'] += total_damage
    db.save_data()
    
    drone_text = f" ({len(user_drones)} پهپاد)"
    response = f"""
🛸 **حمله پهپادی موفق**{drone_text}

💥 **دمیج**: {total_damage}
💰 **جایزه**: {reward} ZP
⭐ **XP**: +{xp_gain}
💎 **موجودی جدید**: {user['zp']:,} ZP
"""
    
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

# ==================== سیستم ماینر ====================
@dp.message(F.text == "⛏ ماینر")
async def miner_cmd(message: types.Message):
    miner_info = db.get_miner_info(message.from_user.id)
    
    miner_text = f"""
⛏ **ماینر منابع**

📊 **سطح**: {miner_info['level']}
💰 **موجودی**: {miner_info['balance']:,} ZP
💎 **درآمد/ساعت**: {miner_info['income']:,} ZP
⏰ **جمع‌آوری بعدی**: {miner_info['next_collect']}
🔧 **ارتقا بعدی**: {miner_info['next_upgrade_cost']:,} ZP

👇 عملیات مورد نظر را انتخاب کنید:
"""
    await message.answer(miner_text, reply_markup=kb.miner_menu())

@dp.message(F.text == "⛏ جمع‌آوری")
async def collect_miner_cmd(message: types.Message):
    income = db.collect_miner(message.from_user.id)
    
    if income > 0:
        response = f"""
✅ **جمع‌آوری موفق!**

💰 **دریافتی**: {income:,} ZP
⛏ موجودی ماینر: 0 ZP
💎 به کیف پول اضافه شد
"""
    else:
        response = "⏳ هنوز زمان جمع‌آوری نرسیده است!"
    
    await message.answer(response, reply_markup=kb.miner_menu())

@dp.message(F.text == "⬆️ ارتقا ماینر")
async def upgrade_miner_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    cost = 1000 * user['miner_level']
    
    if user['zp'] >= cost:
        success, new_level = db.upgrade_miner(message.from_user.id)
        if success:
            response = f"""
✅ **ارتقا موفق!**

⛏ **سطح جدید**: {new_level}
💰 **هزینه**: {cost:,} ZP
💎 **درآمد جدید**: {user['miner_income']:,} ZP/ساعت
"""
        else:
            response = "❌ خطا در ارتقا!"
    else:
        response = f"""
❌ **موجودی ناکافی!**

💰 **مورد نیاز**: {cost:,} ZP
💎 **موجودی شما**: {user['zp']:,} ZP
"""
    
    await message.answer(response, reply_markup=kb.miner_menu())

# ==================== سیستم باکس‌ها ====================
@dp.message(F.text == "📦 باکس‌ها")
async def boxes_cmd(message: types.Message):
    boxes_text = """
📦 **باکس‌های شانس**

🎁 **باکس برنزی** - رایگان (هر ۲۴ ساعت)
🥈 **باکس نقره‌ای** - 5,000 ZP
🥇 **باکس طلایی** - 2 جم
💎 **باکس الماس** - 5 جم

👇 باکس مورد نظر را انتخاب کنید:
"""
    await message.answer(boxes_text, reply_markup=kb.boxes_menu())

# ==================== سیستم لیگ ====================
@dp.message(F.text == "🏆 لیگ")
async def league_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    league_text = f"""
🏆 **سیستم لیگ**

📊 **لیگ فعلی**: {user['league']}
⭐ **امتیازات**: {user.get('league_points', 0):,}
🏅 **جایزه روزانه**: {100 * user['level']:,} ZP

👇 عملیات مورد نظر را انتخاب کنید:
"""
    await message.answer(league_text, reply_markup=kb.league_menu())

# ==================== سیستم خرابکاری ====================
@dp.message(F.text == "🔧 خرابکاری")
async def sabotage_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    sabotage_text = f"""
🔧 **تیم خرابکاری**

📊 **سطح**: {user.get('sabotage_level', 0)}/10
👥 **تیم‌ها**: {user.get('sabotage_teams', 0)}
🎯 **نرخ موفقیت**: {int(user.get('sabotage_success_rate', 0.1) * 100)}%

👇 عملیات خرابکارانه:
"""
    await message.answer(sabotage_text, reply_markup=kb.sabotage_menu())

@dp.message(F.text == "⬆️ ارتقا خرابکاری")
async def upgrade_sabotage_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    sabotage_level = user.get('sabotage_level', 0)
    
    if sabotage_level >= 10:
        await message.answer("🎉 شما به سطح فوق‌حرفه‌ای (۱۰) رسیده‌اید!", reply_markup=kb.sabotage_menu())
        return
    
    cost = 5000 * (sabotage_level + 1)
    
    if user['zp'] >= cost:
        user['sabotage_level'] = sabotage_level + 1
        user['sabotage_success_rate'] = user.get('sabotage_success_rate', 0.1) + 0.1
        user['zp'] -= cost
        
        if user['sabotage_level'] % 2 == 0:
            user['sabotage_teams'] = user.get('sabotage_teams', 0) + 1
        
        db.save_data()
        
        level_names = {
            1: "مبتدی", 2: "مقدماتی", 3: "متوسط", 4: "پیشرفته",
            5: "حرفه‌ای", 6: "کارشناس", 7: "استاد", 
            8: "نخبه", 9: "اسطوره", 10: "فوق‌حرفه‌ای"
        }
        
        response = f"""
✅ **ارتقا موفق!**

🔧 **سطح جدید**: {user['sabotage_level']} ({level_names[user['sabotage_level']]})
💰 **هزینه**: {cost:,} ZP
🎯 **نرخ موفقیت**: {int(user['sabotage_success_rate'] * 100)}%
"""
        
        if user['sabotage_level'] == 10:
            response += "\n🎉 **تبریک! شما به سطح فوق‌حرفه‌ای رسیدید!**"
        
        await message.answer(response, reply_markup=kb.sabotage_menu())
    else:
        await message.answer(f"❌ موجودی ناکافی! نیاز: {cost:,} ZP", reply_markup=kb.sabotage_menu())

# ==================== سیستم مدافعان ====================
@dp.message(F.text == "🛡 مدافعان")
async def defenders_cmd(message: types.Message):
    defenders_text = """
🛡 **سیستم مدافعان**

⚔️ با دیگر بازیکنان مبارزه کنید
🏆 امتیاز کسب کنید
💰 جایزه دریافت کنید

👇 عملیات مورد نظر را انتخاب کنید:
"""
    await message.answer(defenders_text, reply_markup=kb.defenders_menu())

@dp.message(F.text == "⚔️ حمله به مدافع")
async def attack_defender_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # شبیه‌سازی مبارزه
    enemy_power = random.randint(50, 500)
    your_power = user['power'] + (len(user.get('fighters', {})) * 20)
    
    if your_power > enemy_power:
        reward = random.randint(100, 500)
        xp_gain = random.randint(10, 30)
        
        user['zp'] += reward
        user['xp'] = user.get('xp', 0) + xp_gain
        user['total_attacks'] += 1
        user['total_damage'] += reward
        
        # بررسی ارتقا سطح
        xp_needed = user['level'] * 100
        if user['xp'] >= xp_needed:
            user['level'] += 1
            user['xp'] -= xp_needed
            user['power'] += 20
            level_up = f"\n🎉 **سطح شما افزایش یافت! سطح جدید: {user['level']}**"
        else:
            level_up = ""
        
        db.save_data()
        
        response = f"""
✅ **پیروزی در نبرد!**

⚔️ **قدرت شما**: {your_power}
🎯 **قدرت حریف**: {enemy_power}
💰 **جایزه**: {reward:,} ZP
⭐ **XP**: +{xp_gain}
💪 **موجودی جدید**: {user['zp']:,} ZP
{level_up}
"""
    else:
        response = f"""
❌ **شکست در نبرد!**

⚔️ **قدرت شما**: {your_power}
🎯 **قدرت حریف**: {enemy_power}
💡 **نکته**: قدرت خود را افزایش دهید
"""
    
    await message.answer(response, reply_markup=kb.defenders_menu())

# ==================== سیستم پشتیبانی ====================
@dp.message(F.text == "📞 پشتیبانی")
async def support_cmd(message: types.Message):
    support_text = """
📞 **پشتیبانی WarZone**

📩 برای ایجاد تیکت جدید روی "ایجاد تیکت" کلیک کنید
📋 برای مشاهده تیکت‌های قبلی روی "تیکت‌های من" کلیک کنید

👇 عملیات مورد نظر را انتخاب کنید:
"""
    await message.answer(support_text, reply_markup=kb.support_menu())

@dp.message(F.text == "📩 ایجاد تیکت")
async def create_ticket_cmd(message: types.Message):
    user_purchase_state[message.from_user.id] = {'action': 'create_ticket'}
    await message.answer("📝 لطفا متن تیکت خود را ارسال کنید:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(F.text == "📋 تیکت‌های من")
async def my_tickets_cmd(message: types.Message):
    user_tickets = db.get_user_tickets(message.from_user.id)
    
    if not user_tickets:
        await message.answer("📭 شما هیچ تیکتی ندارید.", reply_markup=kb.support_menu())
        return
    
    tickets_text = "📋 **تیکت‌های شما:**\n\n"
    for ticket_id, ticket in user_tickets:
        status = "✅ باز" if ticket['status'] == 'open' else "❌ بسته"
        tickets_text += f"🎫 **تیکت #{ticket_id}** - {status}\n"
        tickets_text += f"📝 {ticket['message'][:50]}...\n"
        tickets_text += f"🕐 {datetime.fromtimestamp(ticket['created_at']).strftime('%Y-%m-%d %H:%M')}\n\n"
    
    await message.answer(tickets_text, reply_markup=kb.support_menu())

# ==================== سیستم امنیت سایبری ====================
@dp.message(F.text == "🔐 امنیت سایبری")
async def cyber_security_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    cyber_text = f"""
🔐 **امنیت سایبری**

🛡 **سطح فعلی**: {user.get('cyber_level', 1)}/10
🚨 **دفاع فعال**: {'✅' if user.get('cyber_defense', False) else '❌'}
💪 **محافظت**: {user.get('cyber_level', 1) * 10}%

👇 برای ارتقا سطح مورد نظر را انتخاب کنید:
"""
    await message.answer(cyber_text, reply_markup=kb.cyber_menu())

# ==================== پنل ادمین ====================
@dp.message(F.text == "📊 آمار کلی")
async def admin_stats_cmd(message: types.Message):
    if not db.is_admin(message.from_user.id):
        return
    
    stats = db.get_all_stats()
    
    stats_text = f"""
📊 **آمار کلی بات**

👥 **کاربران کل**: {stats['total_users']:,}
⚔️ **حملات کل**: {stats['total_attacks']:,}
💥 **دمیج کل**: {stats['total_damage']:,}
📞 **تیکت‌ها**: {stats['total_tickets']}
🟢 **تیکت‌های باز**: {stats['open_tickets']}

💾 **دیتابیس**: {os.path.getsize('warzone_data.json') / 1024:.1f} KB
"""
    await message.answer(stats_text, reply_markup=kb.admin_menu())

@dp.message(F.text == "👥 مدیریت کاربران")
async def admin_users_cmd(message: types.Message):
    if not db.is_admin(message.from_user.id):
        return
    
    user_admin_state[message.from_user.id] = {'action': 'manage_users'}
    
    users_text = """
👥 **مدیریت کاربران**

📝 آیدی کاربر را برای مدیریت ارسال کنید

عملیات‌های ممکن:
👁 مشاهده اطلاعات کاربر
💰 دادن ZP به کاربر
💎 دادن جم به کاربر
⬆️ تغییر سطح کاربر
"""
    await message.answer(users_text)

@dp.message(F.text == "💾 ایجاد بکاپ")
async def admin_backup_cmd(message: types.Message):
    if not db.is_admin(message.from_user.id):
        return
    
    if db.create_backup():
        await message.answer("✅ بکاپ با موفقیت ایجاد شد!", reply_markup=kb.admin_menu())
    else:
        await message.answer("❌ خطا در ایجاد بکاپ!", reply_markup=kb.admin_menu())

# ==================== هندلر پیام متنی ====================
@dp.message(F.text)
async def handle_text_messages(message: types.Message):
    user_id = message.from_user.id
    
    # هندلر ایجاد تیکت
    if user_id in user_purchase_state and user_purchase_state[user_id].get('action') == 'create_ticket':
        ticket_id = db.create_ticket(user_id, message.text)
        del user_purchase_state[user_id]
        
        await message.answer(
            f"✅ **تیکت ایجاد شد!**\n\n🎫 **شماره تیکت**: #{ticket_id}\n📝 پیام شما ثبت شد\n⏳ به زودی پاسخ داده خواهد شد",
            reply_markup=kb.support_menu()
        )
        return
    
    # هندلر مدیریت کاربران توسط ادمین
    if user_id in user_admin_state and user_admin_state[user_id].get('action') == 'manage_users':
        try:
            target_user_id = int(message.text)
            user = db.find_user_by_id(target_user_id)
            
            if user:
                admin_text = f"""
👤 **اطلاعات کاربر**

🆔 **آیدی**: {user['user_id']}
⭐ **سطح**: {user['level']}
💰 **ZP**: {user['zp']:,}
💎 **جم**: {user['gem']}
⚔️ **حملات**: {user['total_att
