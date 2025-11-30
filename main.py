# main.py - WarZone Bot for Railway
import os
import asyncio
import logging
import sys
import random
import time
import threading
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

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

# ==================== سرور HTTP برای Railway ====================
async def health_check(request):
    return web.Response(text=f"🟢 WarZone Bot Active - {datetime.now()}")

def run_http_server():
    try:
        app = web.Application()
        app.router.add_get('/', health_check)
        app.router.add_get('/health', health_check)
        app.router.add_get('/status', health_check)
        port = int(os.getenv("PORT", 8080))
        logger.info(f"🌐 سرور HTTP روی پورت {port} راه‌اندازی شد")
        web.run_app(app, host='0.0.0.0', port=port, access_log=None)
    except Exception as e:
        logger.error(f"❌ خطا در سرور HTTP: {e}")

# ==================== دیتابیس ساده ====================
class SimpleDB:
    def __init__(self):
        self.users = {}
        self.attack_combos = {}
        logger.info("🗄️ دیتابیس راه‌اندازی شد")
    
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
                'drones': [],
                'sabotage_teams': [],
                'attack_combos': [{}, {}, {}],
                'league': 'برنز',
                'league_reward_claimed': False,
                'last_league_reward': 0,
                'created_at': time.time()
            }
        return self.users[user_id]
    
    def update_user_zp(self, user_id, amount):
        user = self.get_user(user_id)
        user['zp'] += amount
        return user['zp']
    
    def update_user_xp(self, user_id, amount):
        user = self.get_user(user_id)
        user['xp'] += amount
        xp_needed = user['level'] * 100
        if user['xp'] >= xp_needed:
            user['level'] += 1
            user['xp'] -= xp_needed
            user['power'] += 20
            return True, user['level']
        return False, user['level']
    
    def add_missile(self, user_id, missile_type, count=1):
        user = self.get_user(user_id)
        if missile_type not in user['missiles']:
            user['missiles'][missile_type] = 0
        user['missiles'][missile_type] += count
    
    def add_fighter(self, user_id, fighter_type):
        user = self.get_user(user_id)
        if fighter_type not in user['fighters']:
            user['fighters'].append(fighter_type)
            return True
        return False
    
    def add_drone(self, user_id, drone_type):
        user = self.get_user(user_id)
        if drone_type not in user['drones']:
            user['drones'].append(drone_type)
            return True
        return False
    
    def get_user_fighters(self, user_id):
        user = self.get_user(user_id)
        return user.get('fighters', [])
    
    def get_user_drones(self, user_id):
        user = self.get_user(user_id)
        return user.get('drones', [])
    
    def can_open_bronze_box(self, user_id):
        user = self.get_user(user_id)
        current_time = time.time()
        return current_time - user.get('last_bronze_box', 0) >= 86400
    
    def set_bronze_box_time(self, user_id):
        user = self.get_user(user_id)
        user['last_bronze_box'] = time.time()
    
    def save_attack_combo(self, user_id, combo_index, combo_data):
        user = self.get_user(user_id)
        user['attack_combos'][combo_index] = combo_data
        return True
    
    def get_attack_combo(self, user_id, combo_index):
        user = self.get_user(user_id)
        return user['attack_combos'][combo_index]
    
    def get_all_stats(self):
        total_users = len(self.users)
        total_attacks = sum(user['total_attacks'] for user in self.users.values())
        total_damage = sum(user['total_damage'] for user in self.users.values())
        return {
            'total_users': total_users,
            'total_attacks': total_attacks,
            'total_damage': total_damage
        }

db = SimpleDB()

# ==================== منوها ====================
def main_menu():
    keyboard = [
        [types.KeyboardButton(text="👤 پروفایل"), types.KeyboardButton(text="🛒 فروشگاه"), types.KeyboardButton(text="⚔️ حمله")],
        [types.KeyboardButton(text="🕵️ خرابکاری"), types.KeyboardButton(text="🏆 لیگ ها"), types.KeyboardButton(text="📦 باکس")],
        [types.KeyboardButton(text="⛏ ماینر"), types.KeyboardButton(text="🛡 دفاع"), types.KeyboardButton(text="📞 پشتیبانی")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def attack_menu():
    keyboard = [
        [types.KeyboardButton(text="🎯 حمله تکی"), types.KeyboardButton(text="💥 حمله ترکیبی")],
        [types.KeyboardButton(text="🛸 حمله پهپادی"), types.KeyboardButton(text="🎯 حمله به کاربر")],
        [types.KeyboardButton(text="🔙 بازگشت")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def combo_menu():
    keyboard = [
        [types.KeyboardButton(text="🛠 ساخت ترکیب ۱"), types.KeyboardButton(text="🛠 ساخت ترکیب ２")],
        [types.KeyboardButton(text="🛠 ساخت ترکیب ３"), types.KeyboardButton(text="📋 ترکیب‌های من")],
        [types.KeyboardButton(text="🎯 حمله با ترکیب"), types.KeyboardButton(text="🔙 بازگشت")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ==================== دستورات اصلی ====================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    
    welcome_text = f"""
🎯 **به WarZone خوش آمدید {username}!** ⚔️

💰 **موجودی اولیه**: {user['zp']:,} ZP
⭐ **سطح**: {user['level']}
💪 **قدرت**: {user['power']}

👇 از منوی زیر انتخاب کنید:
"""
    await message.answer(welcome_text, reply_markup=main_menu())

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    help_text = """
🆘 **راهنمای WarZone**

🎮 **دستورات اصلی:**
/start - شروع بازی
/help - راهنما  
/status - وضعیت بات

⚔️ **سیستم حمله:**
• حمله تکی - کسب ZP و XP
• حمله ترکیبی - با جنگنده‌ها
• حمله پهپادی - دمیج بیشتر
• سیستم ترکیب‌های شخصی

🛒 **فروشگاه:**
• موشک‌ها - قدرت حمله
• جنگنده‌ها - حمله ترکیبی  
• پهپادها - حمله هوایی
• ویژه‌ها - آیتم‌های خاص

📦 **سایر قابلیت‌ها:**
• ماینر - تولید خودکار ZP
• سیستم دفاع - محافظت
• لیگ‌ها - رقابت
• پشتیبانی
"""
    await message.answer(help_text, reply_markup=main_menu())

@dp.message(Command("status"))
async def status_cmd(message: types.Message):
    stats = db.get_all_stats()
    status_text = f"""
🤖 **وضعیت WarZone**

👥 **کاربران**: {stats['total_users']}
⚔️ **حملات**: {stats['total_attacks']}
💥 **دمیج کل**: {stats['total_damage']:,}
🟢 **پلتفرم**: Railway
⏰ **زمان**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    await message.answer(status_text, reply_markup=main_menu())

# ==================== پروفایل ====================
@dp.message(lambda message: message.text == "👤 پروفایل")
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
📦 **جعبه برنزی**: {box_status}
"""
    await message.answer(profile_text, reply_markup=main_menu())

# ==================== سیستم حمله ====================
@dp.message(lambda message: message.text == "⚔️ حمله")
async def attack_handler(message: types.Message):
    await message.answer(
        "⚔️ **سیستم حمله WarZone**\n\n"
        "🎯 **حمله تکی** - حمله ساده با موشک\n"
        "💥 **حمله ترکیبی** - با جنگنده (قدرت بیشتر)\n"
        "🛸 **حمله پهپادی** - حمله هوایی\n"
        "🎯 **حمله به کاربر** - حمله به کاربران دیگر\n\n"
        "👇 نوع حمله را انتخاب کنید:",
        reply_markup=attack_menu()
    )

@dp.message(lambda message: message.text == "🎯 حمله تکی")
async def single_attack_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # محاسبات حمله
    is_critical = random.random() < 0.15
    base_reward = random.randint(40, 80)
    reward = base_reward * 2 if is_critical else base_reward
    xp_gain = random.randint(8, 15)
    
    # آپدیت کاربر
    new_balance = db.update_user_zp(message.from_user.id, reward)
    level_up, new_level = db.update_user_xp(message.from_user.id, xp_gain)
    
    user['total_attacks'] += 1
    user['total_damage'] += reward
    
    # ساخت پاسخ
    critical_text = " 🔥**بحرانی**" if is_critical else ""
    
    response = f"⚔️ **حمله موفق{critical_text}!**\n\n💰 **جایزه**: {reward} ZP\n⭐ **XP**: +{xp_gain}\n"
    
    if level_up:
        response += f"🎉 **سطح شما ارتقا یافت!** (سطح {new_level})\n"
    
    response += f"\n💎 **موجودی جدید**: {new_balance:,} ZP"
    
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
    
    # محاسبات حمله ترکیبی
    base_damage = random.randint(80, 150)
    fighter_bonus = len(user_fighters) * 50
    total_damage = base_damage + fighter_bonus
    
    is_critical = random.random() < 0.15
    if is_critical:
        total_damage *= 2
    
    reward = total_damage
    xp_gain = random.randint(15, 25)
    
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
    
    await message.answer(response, reply_markup=main_menu())

@dp.message(lambda message: message.text == "🛸 حمله پهپادی")
async def drone_attack_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    user_drones = db.get_user_drones(message.from_user.id)
    
    if not user_drones:
        await message.answer(
            "❌ **پهپاد ندارید!**\n\n"
            "برای حمله پهپادی نیاز به حداقل یک پهپاد دارید.\n"
            "به فروشگاه مراجعه کنید و پهپاد بخرید.",
            reply_markup=main_menu()
        )
        return
    
    # محاسبات حمله پهپادی
    base_damage = random.randint(60, 120)
    drone_bonus = len(user_drones) * 30
    total_damage = base_damage + drone_bonus
    
    is_critical = random.random() < 0.20
    if is_critical:
        total_damage *= 2
    
    reward = total_damage
    xp_gain = random.randint(12, 20)
    
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
    
    await message.answer(response, reply_markup=main_menu())

@dp.message(lambda message: message.text == "🎯 حمله به کاربر")
async def attack_user_handler(message: types.Message):
    await message.answer(
        "🎯 **حمله به کاربران**\n\n"
        "🔜 این قابلیت به زودی فعال می‌شود\n\n"
        "✅ در حال حاضر از حملات زیر استفاده کنید:\n"
        "• 🎯 حمله تکی\n"
        "• 💥 حمله ترکیبی\n"
        "• 🛸 حمله پهپادی",
        reply_markup=main_menu()
    )

# ==================== سیستم ترکیب‌ها ====================
@dp.message(lambda message: message.text == "📋 ترکیب‌های من")
async def my_combos_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    combos = user['attack_combos']
    
    combo_text = "📋 **ترکیب‌های حمله شما**\n\n"
    
    for i, combo in enumerate(combos, 1):
        if combo:
            combo_text += f"{i}️⃣ **ترکیب {i}** - فعال\n"
            if 'fighters' in combo:
                combo_text += f"   🛩 {combo['fighters']}\n"
            if 'drones' in combo:
                combo_text += f"   🛸 {combo['drones']}\n"
            if 'missiles' in combo:
                combo_text += f"   🚀 {len(combo['missiles'])} موشک\n"
        else:
            combo_text += f"{i}️⃣ **ترکیب {i}** - خالی\n"
        
        combo_text += "\n"
    
    combo_text += "برای ساخت ترکیب جدید از منوی حمله ترکیبی استفاده کنید."
    
    await message.answer(combo_text, reply_markup=main_menu())

# ==================== فروشگاه ====================
@dp.message(lambda message: message.text == "🛒 فروشگاه")
async def shop_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    shop_text = f"""
🛒 **فروشگاه WarZone**

💰 **موجودی شما**: {user['zp']:,} ZP

🚀 **موشک‌ها:**
• تیرباران - 400 ZP
• رعدآسا - 700 ZP  
• تندباد - 1,000 ZP

🛩 **جنگنده‌ها:**
• شب‌پرواز - 5,000 ZP
• توفان‌ساز - 8,000 ZP

🛸 **پهپادها:**
• زنبورک - 3,000 ZP
• سایفر - 5,000 ZP

💎 **ویژه‌ها:**
• آتشفشان - 8,000 ZP
• توفان‌نو - 15,000 ZP

🔜 به زودی آیتم‌های بیشتر...
"""
    await message.answer(shop_text, reply_markup=main_menu())

# ==================== سیستم باکس ====================
@dp.message(lambda message: message.text == "📦 باکس")
async def boxes_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    boxes_text = f"""
📦 **جعبه‌های شانس WarZone**

💰 **موجودی شما**: {user['zp']:,} ZP

📦 **جعبه برنزی** - رایگان (هر ۲۴ ساعت)
• جایزه: 50-200 ZP یا موشک

🥈 **جعبه نقره‌ای** - 5,000 ZP  
• جایزه: 200-500 ZP

🥇 **جعبه طلایی** - ۲ جم
• جایزه: آیتم‌های ویژه

💎 **جعبه الماس** - ۵ جم
• جایزه: موشک‌های افسانه‌ای

👇 برای باز کردن جعبه، از دکمه‌های زیر استفاده کنید:
"""
    
    keyboard = [
        [types.KeyboardButton(text="📦 برنزی"), types.KeyboardButton(text="🥈 نقره‌ای")],
        [types.KeyboardButton(text="🥇 طلایی"), types.KeyboardButton(text="💎 الماس")],
        [types.KeyboardButton(text="🔙 بازگشت")]
    ]
    boxes_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    await message.answer(boxes_text, reply_markup=boxes_markup)

@dp.message(lambda message: message.text == "📦 برنزی")
async def bronze_box_handler(message: types.Message):
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
            new_balance = db.update_user_zp(message.from_user.id, reward)
            response = f"📦 **جعبه برنزی** 🎉\n\n💰 **جایزه**: {reward} ZP\n💎 **موجودی جدید**: {new_balance:,} ZP"
        else:
            missiles = ["تیرباران", "رعدآسا"]
            missile = random.choice(missiles)
            db.add_missile(message.from_user.id, missile)
            response = f"📦 **جعبه برنزی** 🎉\n\n🚀 **جایزه**: ۱ عدد {missile}"
        
        db.set_bronze_box_time(message.from_user.id)
    
    await message.answer(response, reply_markup=main_menu())

# ==================== سایر قابلیت‌ها ====================
@dp.message(lambda message: message.text in ["🕵️ خرابکاری", "🏆 لیگ ها", "⛏ ماینر", "🛡 دفاع", "📞 پشتیبانی"])
async def coming_soon_handler(message: types.Message):
    feature_name = message.text
    await message.answer(
        f"{feature_name}\n\n"
        "🔜 این قابلیت به زودی فعال می‌شود\n\n"
        "✅ در حال حاضر از سیستم‌های زیر استفاده کنید:\n"
        "• ⚔️ حمله\n• 🛒 فروشگاه\n• 📦 باکس\n• 👤 پروفایل",
        reply_markup=main_menu()
    )

@dp.message(lambda message: message.text == "🔙 بازگشت")
async def back_handler(message: types.Message):
    await message.answer("🔙 به منوی اصلی بازگشتید", reply_markup=main_menu())

# ==================== هندلر پیش‌فرض ====================
@dp.message()
async def echo_handler(message: types.Message):
    await message.answer("از منوی زیر انتخاب کنید:", reply_markup=main_menu())

# ==================== تابع اصلی ====================
async def main():
    logger.info("🤖 بات WarZone در حال راه‌اندازی...")
    
    # اجرای سرور HTTP در background
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    logger.info("🚀 شروع polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
