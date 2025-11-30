# main.py - WarZone Bot Complete with Admin Panel
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

# ==================== سیستم ادمین ====================
@dp.message(F.text == "👥 مدیریت کاربران")
async def admin_users_handler(message: types.Message):
    if not db.is_admin(message.from_user.id):
        await message.answer("❌ دسترسی denied!", reply_markup=kb.main_menu())
        return
    
    users_text = """
👥 **مدیریت کاربران**

➕ **افزودن ZP** - افزایش ZP کاربر
💎 **افزودن جم** - افزایش جم کاربر  
⭐ **افزودن لول** - افزایش لول کاربر
📊 **اطلاعات کاربر** - مشاهده اطلاعات کاربر
🔍 **جستجوی کاربر** - جستجو با آیدی

👇 عملیات مورد نظر را انتخاب کنید:
"""
    await message.answer(users_text, reply_markup=kb.admin_users_menu())

@dp.message(F.text == "➕ افزودن ZP")
async def admin_add_zp_handler(message: types.Message):
    if not db.is_admin(message.from_user.id):
        return
    
    user_admin_state[message.from_user.id] = {'action': 'add_zp'}
    await message.answer(
        "💰 **افزودن ZP به کاربر**\n\n"
        "لطفاً آیدی کاربر و مقدار ZP را به این فرمت ارسال کنید:\n"
        "`آیدی_کاربر مقدار_ZP`\n\n"
        "مثال:\n"
        "`123456789 5000`\n\n"
        "این مقدار ZP به کاربر اضافه خواهد شد.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 بازگشت به پنل ادمین")]],
            resize_keyboard=True
        )
    )

@dp.message(F.text == "💎 افزودن جم")
async def admin_add_gem_handler(message: types.Message):
    if not db.is_admin(message.from_user.id):
        return
    
    user_admin_state[message.from_user.id] = {'action': 'add_gem'}
    await message.answer(
        "💎 **افزودن جم به کاربر**\n\n"
        "لطفاً آیدی کاربر و مقدار جم را به این فرمت ارسال کنید:\n"
        "`آیدی_کاربر مقدار_جم`\n\n"
        "مثال:\n"
        "`123456789 10`\n\n"
        "این مقدار جم به کاربر اضافه خواهد شد.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 بازگشت به پنل ادمین")]],
            resize_keyboard=True
        )
    )

@dp.message(F.text == "⭐ افزودن لول")
async def admin_add_level_handler(message: types.Message):
    if not db.is_admin(message.from_user.id):
        return
    
    user_admin_state[message.from_user.id] = {'action': 'add_level'}
    await message.answer(
        "⭐ **افزودن لول به کاربر**\n\n"
        "لطفاً آیدی کاربر و مقدار لول را به این فرمت ارسال کنید:\n"
        "`آیدی_کاربر مقدار_لول`\n\n"
        "مثال:\n"
        "`123456789 5`\n\n"
        "این مقدار لول به کاربر اضافه خواهد شد.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 بازگشت به پنل ادمین")]],
            resize_keyboard=True
        )
    )

@dp.message(F.text == "📊 اطلاعات کاربر")
async def admin_user_info_handler(message: types.Message):
    if not db.is_admin(message.from_user.id):
        return
    
    user_admin_state[message.from_user.id] = {'action': 'user_info'}
    await message.answer(
        "📊 **اطلاعات کاربر**\n\n"
        "لطفاً آیدی کاربر را ارسال کنید:\n"
        "`آیدی_کاربر`\n\n"
        "مثال:\n"
        "`123456789`",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 بازگشت به پنل ادمین")]],
            resize_keyboard=True
        )
    )

@dp.message(F.text == "📊 آمار بات")
async def admin_stats_handler(message: types.Message):
    if not db.is_admin(message.from_user.id):
        return
    
    stats = db.get_all_stats()
    stats_text = f"""
📈 **آمار کلی WarZone**

👥 **تعداد کاربران**: {stats['total_users']}
⚔️ **تعداد حملات**: {stats['total_attacks']}
💥 **دمیج کل**: {stats['total_damage']:,}
📞 **تیکت‌ها**: {stats['total_tickets']}
🟢 **تیکت‌های باز**: {stats['open_tickets']}

🕒 **زمان سرور**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    await message.answer(stats_text, reply_markup=kb.admin_menu())

# پردازش دستورات ادمین
@dp.message(F.text.regexp(r'^\d+ \d+$'))
async def process_admin_action(message: types.Message):
    if not db.is_admin(message.from_user.id):
        return
    
    user_id = message.from_user.id
    if user_id not in user_admin_state:
        return
    
    action = user_admin_state[user_id]['action']
    parts = message.text.split()
    target_user_id = int(parts[0])
    amount = int(parts[1])
    
    target_user = db.find_user_by_id(target_user_id)
    if not target_user:
        await message.answer("❌ کاربر یافت نشد!", reply_markup=kb.admin_menu())
        del user_admin_state[user_id]
        return
    
    if action == 'add_zp':
        new_balance = db.add_zp_to_user(target_user_id, amount)
        response = f"✅ **ZP اضافه شد!**\n\n👤 کاربر: {target_user_id}\n💰 مقدار: {amount:,} ZP\n💎 موجودی جدید: {new_balance:,} ZP"
    
    elif action == 'add_gem':
        new_balance = db.add_gem_to_user(target_user_id, amount)
        response = f"✅ **جم اضافه شد!**\n\n👤 کاربر: {target_user_id}\n💎 مقدار: {amount} جم\n💎 موجودی جدید: {new_balance} جم"
    
    elif action == 'add_level':
        new_level = db.add_level_to_user(target_user_id, amount)
        response = f"✅ **لول اضافه شد!**\n\n👤 کاربر: {target_user_id}\n⭐ مقدار: {amount} لول\n⭐ لول جدید: {new_level}"
    
    await message.answer(response, reply_markup=kb.admin_menu())
    del user_admin_state[user_id]

@dp.message(F.text.regexp(r'^\d+$'))
async def process_user_info(message: types.Message):
    if not db.is_admin(message.from_user.id):
        return
    
    user_id = message.from_user.id
    if user_id not in user_admin_state or user_admin_state[user_id]['action'] != 'user_info':
        return
    
    target_user_id = int(message.text)
    target_user = db.find_user_by_id(target_user_id)
    
    if not target_user:
        await message.answer("❌ کاربر یافت نشد!", reply_markup=kb.admin_menu())
        del user_admin_state[user_id]
        return
    
    user_info = f"""
📊 **اطلاعات کاربر**

👤 **آیدی**: {target_user['user_id']}
⭐ **لول**: {target_user['level']}
💰 **ZP**: {target_user['zp']:,}
💎 **جم**: {target_user['gem']}
💪 **قدرت**: {target_user['power']}

🛡️ **دفاع**: سطح {target_user['defense_level']}
🔒 **امنیت**: سطح {target_user['cyber_level']}
⛏ **ماینر**: سطح {target_user['miner_level']}

🎯 **حملات**: {target_user['total_attacks']:,}
💥 **دمیج کل**: {target_user['total_damage']:,}
🛩 **جنگنده‌ها**: {len(target_user['fighters'])}
🛸 **پهپادها**: {len(target_user['drones'])}

📅 **تاریخ عضویت**: {datetime.fromtimestamp(target_user['created_at']).strftime('%Y-%m-%d')}
"""
    await message.answer(user_info, reply_markup=kb.admin_menu())
    del user_admin_state[user_id]

# ==================== سیستم پشتیبانی ====================
@dp.message(F.text == "📞 پشتیبانی")
async def support_handler(message: types.Message):
    support_text = """
📞 **پشتیبانی WarZone**

📩 **ارسال تیکت** - ایجاد درخواست پشتیبانی
📋 **تیکت‌های من** - مشاهده تیکت‌های قبلی  
🆘 **راهنمای سریع** - سوالات متداول
📞 **تماس با ادمین** - اطلاعات تماس

👇 عملیات مورد نظر را انتخاب کنید:
"""
    await message.answer(support_text, reply_markup=kb.support_menu())

@dp.message(F.text == "📩 ارسال تیکت")
async def create_ticket_handler(message: types.Message):
    user_admin_state[message.from_user.id] = {'action': 'create_ticket'}
    await message.answer(
        "📩 **ارسال تیکت پشتیبانی**\n\n"
        "لطفاً پیام خود را ارسال کنید:\n\n"
        "✅ موضوع مشکل یا سوال خود را به طور کامل شرح دهید\n"
        "✅ در صورت امکان تصویر یا اسکرین‌شات ارسال کنید\n"
        "✅ پیام شما به ادمین‌ها ارسال خواهد شد\n\n"
        "برای انصراف از منوی بازگشت استفاده کنید.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 بازگشت")]],
            resize_keyboard=True
        )
    )

@dp.message(F.text == "📋 تیکت‌های من")
async def my_tickets_handler(message: types.Message):
    user_tickets = db.get_user_tickets(message.from_user.id)
    
    if not user_tickets:
        await message.answer("📭 **هیچ تیکتی ندارید!**", reply_markup=kb.support_menu())
        return
    
    tickets_text = "📋 **تیکت‌های شما**\n\n"
    
    for ticket_id, ticket in user_tickets[:5]:  # فقط ۵ تیکت آخر
        status_icon = "🟢" if ticket['status'] == 'open' else "🔴" if ticket['status'] == 'closed' else "🟡"
        created_date = datetime.fromtimestamp(ticket['created_at']).strftime('%Y-%m-%d')
        
        tickets_text += f"{status_icon} **تیکت #{ticket_id}** - {ticket['status']}\n"
        tickets_text += f"📅 {created_date}\n"
        tickets_text += f"📝 {ticket['message'][:50]}...\n\n"
    
    if len(user_tickets) > 5:
        tickets_text += f"📎 و {len(user_tickets) - 5} تیکت دیگر..."
    
    await message.answer(tickets_text, reply_markup=kb.support_menu())

@dp.message(F.text == "🆘 راهنمای سریع")
async def quick_help_handler(message: types.Message):
    help_text = """
🆘 **راهنمای سریع**

❓ **چگونه ZP کسب کنم؟**
• حمله تکی، ترکیبی و پهپادی
• باز کردن جعبه‌های شانس
• استفاده از ماینر

❓ **چگونه جنگنده بخرم؟**
• به فروشگاه بروید
• بخش جنگنده‌ها را انتخاب کنید
• جنگنده مورد نظر را انتخاب کنید

❓ **جعبه برنزی چیست؟**
• هر ۲۴ ساعت یکبار رایگان
• جایزه: ZP یا موشک

❓ **مشکلی دارم؟**
• از بخش "ارسال تیکت" استفاده کنید
• مشکل را به طور کامل شرح دهید
"""
    await message.answer(help_text, reply_markup=kb.support_menu())

@dp.message(F.text == "📞 تماس با ادمین")
async def contact_admin_handler(message: types.Message):
    contact_text = """
📞 **تماس با ادمین**

👤 **پشتیبانی فنی**: @WarZone_Support
🔧 **درگاه ارتباطی**: تیکت پشتیبانی

💡 **راهنمایی**:
• برای مشکلات فنی از تیکت استفاده کنید
• پاسخگویی در سریع‌ترین زمان ممکن
• لطفاً شکیبا باشید
"""
    await message.answer(contact_text, reply_markup=kb.support_menu())

# پردازش تیکت پشتیبانی
@dp.message(F.text & ~F.text.startswith('/') & ~F.text.startswith('🔙'))
async def process_ticket_message(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in user_admin_state and user_admin_state[user_id]['action'] == 'create_ticket':
        ticket_id = db.create_ticket(user_id, message.text)
        
        # اطلاع به ادمین‌ها
        for admin_id in ADMINS:
            try:
                await bot.send_message(
                    admin_id,
                    f"📩 **تیکت جدید #{ticket_id}**\n\n"
                    f"👤 کاربر: {user_id}\n"
                    f"📝 پیام: {message.text}\n\n"
                    f"🕒 زمان: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
            except:
                pass
        
        await message.answer(
            f"✅ **تیکت شما ثبت شد!**\n\n"
            f"📋 شماره تیکت: #{ticket_id}\n"
            f"📝 پیام شما: {message.text}\n\n"
            f"🕒 پاسخگویی در سریع‌ترین زمان ممکن\n"
            f"📞 برای پیگیری از بخش 'تیکت‌های من' استفاده کنید",
            reply_markup=kb.support_menu()
        )
        del user_admin_state[user_id]

# ==================== پروفایل ====================
@dp.message(F.text == "👤 پروفایل")
async def profile_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # محاسبه زمان باقی‌مانده جعبه برنزی
    can_open_bronze = db.can_open_bronze_box(message.from_user.id)
    if can_open_bronze:
        box_status = "🟢 آماده"
    else:
        remaining = 86400 - (time.time() - user.get('last_bronze_box', 0))
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        box_status = f"⏳ {hours} ساعت و {minutes} دقیقه"
    
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
🛩 **جنگنده‌ها**: {len(user['fighters'])}
🛸 **پهپادها**: {len(user['drones'])}
📦 **جعبه برنزی**: {box_status}
"""
    await message.answer(profile_text, reply_markup=kb.main_menu())

# ==================== سیستم حمله ====================
@dp.message(F.text == "⚔️ حمله")
async def attack_handler(message: types.Message):
    await message.answer(
        "⚔️ **سیستم حمله WarZone**\n\n"
        "🎯 **حمله تکی** - حمله ساده با موشک\n"
        "💥 **حمله ترکیبی** - با جنگنده (قدرت بیشتر)\n"
        "🛸 **حمله پهپادی** - حمله هوایی\n"
        "🛠 **ترکیب‌های من** - مدیریت ترکیب‌های شخصی\n\n"
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

@dp.message(F.text == "💥 حمله ترکیبی")
async def combo_attack_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    user_fighters = user['fighters']
    
    if not user_fighters:
        await message.answer(
            "❌ **جنگنده ندارید!**\n\n"
            "برای حمله ترکیبی نیاز به حداقل یک جنگنده دارید.\n"
            "به فروشگاه مراجعه کنید و جنگنده بخرید.",
            reply_markup=kb.main_menu()
        )
        return
    
    # محاسبات حمله ترکیبی
    attack_config = ATTACK_TYPES["ترکیبی"]
    base_damage = random.randint(attack_config["base_damage"][0], attack_config["base_damage"][1])
    fighter_bonus = len(user_fighters) * 50
    total_damage = base_damage + fighter_bonus
    
    is_critical = random.random() < attack_config["critical_chance"]
    if is_critical:
        total_damage *= 2
    
    reward = total_damage
    xp_gain = random.randint(attack_config["xp_gain"][0], attack_config["xp_gain"][1])
    
    # آپدیت کاربر
    new_balance = db.update_user_zp(message.from_user.id, reward)
    level_up, new_level = db.update_user_xp(message.from_user.id, xp_gain)
    
    user['total_attacks'] += 1
    user['total_damage'] += total_damage
    
    # ساخت پاسخ
    critical_text = " 🔥**بحرانی**" if is_critical else ""
    fighter_text = f" ({len(user_fighters)} جنگنده)"
    
    response = f"💥 **حمله ترکیبی موفق{critical_text}**{fighter_text}\n\n💥 **دمیج**: {total_damage}\n💰 **جایزه**: {reward} ZP\n⭐ **XP**: +{xp_gain}\n"
    
    if level_up:
        response += f"🎉 **سطح شما ارتقا یافت!** (سطح {new_level})\n"
    
    response += f"\n💎 **موجودی جدید**: {new_balance:,} ZP"
    
    await message.answer(response, reply_markup=kb.main_menu())

@dp.message(F.text == "🛸 حمله پهپادی")
async def drone_attack_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    user_drones = user['drones']
    
    if not user_drones:
        await message.answer(
            "❌ **پهپاد ندارید!**\n\n"
            "برای حمله پهپادی نیاز به حداقل یک پهپاد دارید.\n"
            "به فروشگاه مراجعه کنید و پهپاد بخرید.",
            reply_markup=kb.main_menu()
        )
        return
    
    # محاسبات حمله پهپادی
    attack_config = ATTACK_TYPES["پهپادی"]
    base_damage = random.randint(attack_config["base_damage"][0], attack_config["base_damage"][1])
    drone_bonus = len(user_drones) * 30
    total_damage = base_damage + drone_bonus
    
    is_critical = random.random() < attack_config["critical_chance"]
    if is_critical:
        total_damage *= 2
    
    reward = total_damage
    xp_gain = random.randint(attack_config["xp_gain"][0], attack_config["xp_gain"][1])
    
    # آپدیت کاربر
    new_balance = db.update_user_zp(message.from_user.id, reward)
    level_up, new_level = db.update_user_xp(message.from_user.id, xp_gain)
    
    user['total_attacks'] += 1
    user['total_damage'] += total_damage
    
    # ساخت پاسخ
    critical_text = " 🔥**بحرانی**" if is_critical else ""
    drone_text = f" ({len(user_drones)} پهپاد)"
    
    response = f"🛸 **حمله پهپادی موفق{critical_text}**{drone_text}\n\n💥 **دمیج**: {total_damage}\n💰 **جایزه**: {reward} ZP\n⭐ **XP**: +{xp_gain}\n"
    
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
💎 **جم**: {user['gem']}

👇 دسته مورد نظر را انتخاب کنید:

🚀 **موشک‌ها** - قدرت حمله اصلی
🛩 **جنگنده‌ها** - حمله ترکیبی  
🛸 **پهپادها** - حمله هوایی
🛡 **پدافند** - سیستم دفاع
"""
    await message.answer(shop_text, reply_markup=kb.shop_main_menu())

# دسته‌های فروشگاه
@dp.message(F.text == "🚀 موشک‌ها")
async def missiles_shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)

    
