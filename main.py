# main.py - WarZone Bot (Always Online)
import asyncio
import logging
import signal
import sys
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import aiohttp
import sqlite3
import random
import os

print("🚀 راه‌اندازی WarZone Bot...")

# تنظیمات پیشرفته لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('warzone.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# تنظیمات اصلی
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logger.error("❌ توکن یافت نشد! لطفا TOKEN را تنظیم کنید.")
    sys.exit(1)

# ساخت بات با تنظیمات پیشرفته
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# دیتابیس پیشرفته
class WarZoneDatabase:
    def __init__(self):
        self.db_path = 'warzone.db'
        self.conn = None
        self.init_db()
    
    def init_db(self):
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL")  # بهبود عملکرد
            self.create_tables()
            logger.info("✅ دیتابیس WarZone راه‌اندازی شد")
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی دیتابیس: {e}")
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # کاربران
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                zp INTEGER DEFAULT 1000,
                gem INTEGER DEFAULT 0,
                power INTEGER DEFAULT 100,
                defense_level INTEGER DEFAULT 1,
                cyber_level INTEGER DEFAULT 1,
                miner_level INTEGER DEFAULT 1,
                miner_balance INTEGER DEFAULT 0,
                last_miner_claim INTEGER DEFAULT 0,
                last_bronze_box INTEGER DEFAULT 0,
                total_attacks INTEGER DEFAULT 0,
                total_damage INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # موشک‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS missiles (
                user_id INTEGER,
                missile_type TEXT,
                quantity INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, missile_type),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # جنگنده‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fighters (
                user_id INTEGER,
                fighter_type TEXT,
                equipped BOOLEAN DEFAULT FALSE,
                PRIMARY KEY (user_id, fighter_type),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # حملات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attacker_id INTEGER,
                defender_id INTEGER,
                damage INTEGER,
                reward INTEGER,
                attack_type TEXT,
                is_critical BOOLEAN DEFAULT FALSE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (attacker_id) REFERENCES users (user_id),
                FOREIGN KEY (defender_id) REFERENCES users (user_id)
            )
        ''')
        
        # لاگ فعالیت‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_type TEXT,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        self.conn.commit()
    
    def get_connection(self):
        if self.conn is None:
            self.init_db()
        return self.conn

db = WarZoneDatabase()

# سیستم مدیریت خطا
async def error_handler(update: types.Update, exception: Exception):
    logger.error(f"خطا در پردازش آپدیت: {exception}")
    return True

# منوی اصلی
def main_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="👤 پروفایل"), types.KeyboardButton(text="⚔️ حمله")],
            [types.KeyboardButton(text="🛒 فروشگاه"), types.KeyboardButton(text="⛏ ماینر")],
            [types.KeyboardButton(text="📦 جعبه"), types.KeyboardButton(text="🛡 دفاع")],
            [types.KeyboardButton(text="🕵️ خرابکاری"), types.KeyboardButton(text="📊 آمار")]
        ],
        resize_keyboard=True,
        input_field_placeholder="انتخاب کنید..."
    )

# سیستم کاربر
def get_user(user_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
        conn.commit()
        logger.info(f"✅ کاربر جدید ایجاد شد: {user_id}")
        return get_user(user_id)
    return user

def update_user_zp(user_id, amount):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET zp = zp + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()

def update_user_xp(user_id, amount):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET xp = xp + ? WHERE user_id = ?', (amount, user_id))
    
    user = get_user(user_id)
    xp_needed = user[2] * 100
    if user[3] >= xp_needed:
        cursor.execute('UPDATE users SET level = level + 1, xp = xp - ? WHERE user_id = ?', 
                      (xp_needed, user_id))
        conn.commit()
        logger.info(f"🎉 کاربر {user_id} به سطح {user[2] + 1} ارتقا یافت")
        return True
    conn.commit()
    return False

def log_activity(user_id, activity_type, details=""):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO activity_log (user_id, activity_type, details) VALUES (?, ?, ?)',
        (user_id, activity_type, details)
    )
    conn.commit()

# هندلرهای اصلی
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    username = f"@{message.from_user.username}" if message.from_user.username else "ناشناس"
    
    welcome_text = (
        f"🎯 **به WarZone خوش آمدید {username}!** ⚔️\n\n"
        "🛡️ **یک بازی استراتژیک جنگی پیشرفته**\n\n"
        "✅ **قابلیت‌های فعال:**\n"
        "• ⚔️ سیستم حمله پیشرفته\n" 
        "• 🛒 فروشگاه جنگ‌افزار\n"
        "• ⛏️ ماینر تولید ZP\n"
        "• 📦 جعبه‌های شانس\n"
        "• 👤 پروفایل و سطح‌بندی\n"
        "• 📊 آمار کامل\n\n"
        f"💰 **موجودی اولیه**: {user[4]:,} ZP\n"
        "👇 از منوی زیر انتخاب کنید:"
    )
    
    log_activity(message.from_user.id, "start", "ورود به ربات")
    await message.answer(welcome_text, reply_markup=main_menu())

@dp.message(Command("status"))
async def status_cmd(message: types.Message):
    bot_info = await bot.get_me()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM attacks')
    total_attacks = cursor.fetchone()[0]
    
    status_text = (
        "🤖 **وضعیت WarZone Bot**\n\n"
        f"🆔 **بات**: @{bot_info.username}\n"
        f"👥 **کاربران**: {total_users:,}\n"
        f"⚔️ **حملات**: {total_attacks:,}\n"
        f"🕒 **آپ‌تایم**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"📊 **وضعیت**: 🟢 آنلاین\n\n"
        "✅ تمام سیستم‌ها فعال هستند"
    )
    
    await message.answer(status_text)

@dp.message(lambda message: message.text == "👤 پروفایل")
async def profile_handler(message: types.Message):
    user = get_user(message.from_user.id)
    xp_needed = user[2] * 100
    xp_percent = (user[3] / xp_needed) * 100 if xp_needed > 0 else 0
    
    profile_text = (
        f"👤 **پروفایل جنگجو**\n\n"
        f"🆔 **شناسه**: {user[0]}\n"
        f"⭐ **سطح**: {user[2]}\n"
        f"📊 **XP**: {user[3]}/{xp_needed} ({xp_percent:.1f}%)\n"
        f"💰 **ZP**: {user[4]:,}\n"
        f"💎 **جم**: {user[5]}\n"
        f"💪 **قدرت**: {user[6]}\n"
        f"🛡️ **پدافند**: سطح {user[7]}\n"
        f"🔒 **امنیت**: سطح {user[8]}\n"
        f"⛏️ **ماینر**: سطح {user[9]}\n"
        f"🎯 **حملات**: {user[13]:,}\n"
        f"💥 **دمیج کل**: {user[14]:,}"
    )
    
    log_activity(message.from_user.id, "profile_view")
    await message.answer(profile_text, reply_markup=main_menu())

@dp.message(lambda message: message.text == "⚔️ حمله")
async def attack_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🎯 حمله تکی"), types.KeyboardButton(text="💥 حمله ترکیبی")],
            [types.KeyboardButton(text="🔙 منوی اصلی")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "⚔️ **سیستم حمله WarZone**\n\n"
        "🎯 **حمله تکی** - استفاده از یک موشک\n"
        "💥 **حمله ترکیبی** - ترکیب جنگنده و موشک\n"
        "💰 **جایزه**: XP + ZP\n"
        "🔥 **شانس بحرانی**: ۱۵٪\n\n"
        "👇 نوع حمله را انتخاب کنید:",
        reply_markup=keyboard
    )

@dp.message(lambda message: message.text == "🎯 حمله تکی")
async def single_attack_handler(message: types.Message):
    user = get_user(message.from_user.id)
    
    # شانس حمله بحرانی
    is_critical = random.random() < 0.15
    base_reward = random.randint(40, 80)
    reward = base_reward * 2 if is_critical else base_reward
    xp_gain = random.randint(8, 15)
    
    # اعطای جایزه
    update_user_zp(message.from_user.id, reward)
    level_up = update_user_xp(message.from_user.id, xp_gain)
    
    # ثبت آمار
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET total_attacks = total_attacks + 1, total_damage = total_damage + ? WHERE user_id = ?',
        (reward, message.from_user.id)
    )
    
    # ثبت حمله
    cursor.execute(
        'INSERT INTO attacks (attacker_id, damage, reward, attack_type, is_critical) VALUES (?, ?, ?, ?, ?)',
        (message.from_user.id, reward, reward, "single", is_critical)
    )
    conn.commit()
    
    critical_text = " 🔥**بحرانی**" if is_critical else ""
    
    response = f"⚔️ **حمله موفق{critical_text}!**\n\n"
    response += f"💰 **جایزه**: {reward} ZP\n"
    response += f"⭐ **XP**: +{xp_gain}\n"
    
    if level_up:
        new_level = get_user(message.from_user.id)[2]
        response += f"🎉 **سطح شما ارتقا یافت!** (سطح {new_level})\n"
    
    response += f"\n💎 **موجودی جدید**: {get_user(message.from_user.id)[4]:,} ZP"
    
    log_activity(message.from_user.id, "attack", f"حمله تکی - {reward} ZP")
    await message.answer(response, reply_markup=main_menu())

@dp.message(lambda message: message.text == "📊 آمار")
async def stats_handler(message: types.Message):
    user = get_user(message.from_user.id)
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM attacks WHERE attacker_id = ?', (message.from_user.id,))
    user_attacks = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(damage) FROM attacks WHERE attacker_id = ?', (message.from_user.id,))
    total_damage = cursor.fetchone()[0] or 0
    
    stats_text = (
        "📊 **آمار جهانی WarZone**\n\n"
        f"👥 **کل کاربران**: {total_users:,}\n"
        f"🎯 **حملات شما**: {user_attacks:,}\n"
        f"💥 **دمیج کل شما**: {total_damage:,}\n"
        f"⭐ **سطح شما**: {user[2]}\n"
        f"💰 **ZP شما**: {user[4]:,}\n\n"
        f"🕒 **تاریخ**: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    
    log_activity(message.from_user.id, "stats_view")
    await message.answer(stats_text, reply_markup=main_menu())

# هندلرهای باقی مانده (مشابه قبل)
@dp.message(lambda message: message.text in ["🛒 فروشگاه", "⛏ ماینر", "📦 جعبه", "🛡 دفاع", "🕵️ خرابکاری"])
async def coming_soon_handler(message: types.Message):
    feature_name = {
        "🛒 فروشگاه": "فروشگاه جنگ‌افزار",
        "⛏ ماینر": "سیستم ماینر", 
        "📦 جعبه": "جعبه‌های شانس",
        "🛡 دفاع": "سیستم دفاع",
        "🕵️ خرابکاری": "سیستم خرابکاری"
    }[message.text]
    
    await message.answer(
        f"🛠 **{feature_name}**\n\n"
        f"🔜 به زودی فعال می‌شود\n\n"
        f"✅ در حال حاضر از این قابلیت‌ها استفاده کنید:\n"
        f"• ⚔️ سیستم حمله پیشرفته\n"
        f"• 👤 پروفایل و آمار\n"
        f"• 📊 آمار جهانی\n\n"
        f"🔄 به روزرسانی‌های بعدی را دنبال کنید!",
        reply_markup=main_menu()
    )

@dp.message(lambda message: message.text == "🔙 منوی اصلی")
async def back_handler(message: types.Message):
    await message.answer("🔙 بازگشت به منوی اصلی", reply_markup=main_menu())

# هندلر پیام‌های متنی
@dp.message()
async def all_messages(message: types.Message):
    if message.text and not message.text.startswith('/'):
        await message.answer("🎯 از منوی زیر انتخاب کنید:", reply_markup=main_menu())

# مدیریت خاموشی
async def shutdown(signal, loop):
    logger.info("🔄 دریافت سیگنال خاموشی...")
    await bot.session.close()
    if db.conn:
        db.conn.close()
    logger.info("✅ بات WarZone خاموش شد")
    loop.stop()

# شروع بات
async def main():
    logger.info("🚀 شروع WarZone Bot...")
    
    try:
        # حذف وب‌هوک برای پولینگ
        async with aiohttp.ClientSession() as session:
            await session.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
            logger.info("✅ وب‌هوک حذف شد")
        
        # اطلاعات بات
        bot_info = await bot.get_me()
        logger.info(f"✅ بات: @{bot_info.username}")
        logger.info(f"✅ شناسه بات: {bot_info.id}")
        
        # تنظیم هندلر خطا
        dp.errors.register(error_handler)
        
        # تنظیم سیگنال‌های خاموشی
        loop = asyncio.get_running_loop()
        for sig in [signal.SIGTERM, signal.SIGINT]:
            loop.add_signal_handler(
                sig, 
                lambda: asyncio.create_task(shutdown(sig, loop))
            )
        
        logger.info("🟢 بات WarZone آنلاین شد و آماده دریافت پیام‌ها است...")
        logger.info("⏰ پولینگ فعال - بات همیشه آنلاین خواهد بود")
        
        # شروع پولینگ
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"❌ خطای بحرانی: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹ توقف دستی بات")
    except Exception as e:
        logger.error(f"❌ خطای اصلی: {e}")
