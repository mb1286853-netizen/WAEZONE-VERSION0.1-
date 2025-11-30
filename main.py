# main.py - WarZone Bot
import os
import asyncio
import logging
import sys
import random
import time
import threading

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

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logger.error("❌ توکن یافت نشد!")
    sys.exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# سرور ساده HTTP برای پورت
async def health_check(request):
    return web.Response(text="🟢 WarZone Bot Active")

def run_http_server():
    try:
        app = web.Application()
        app.router.add_get('/', health_check)
        app.router.add_get('/health', health_check)
        web.run_app(app, host='0.0.0.0', port=8080)
    except Exception as e:
        logger.error(f"خطا در سرور HTTP: {e}")

# ==================== دیتابیس کامل ====================
class SimpleDB:
    def __init__(self):
        self.users = {}
        self.support_tickets = {}
        self.attack_requests = {}
    
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
                'league': 'برنز',
                'league_reward_claimed': False,
                'last_league_reward': 0
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
    
    def add_drone(self, user_id, drone_type):
        user = self.get_user(user_id)
        if drone_type not in user['drones']:
            user['drones'].append(drone_type)
    
    def add_sabotage_team(self, user_id, team_type):
        user = self.get_user(user_id)
        if team_type not in user['sabotage_teams']:
            user['sabotage_teams'].append(team_type)
    
    def get_user_fighters(self, user_id):
        user = self.get_user(user_id)
        return user.get('fighters', [])
    
    def get_user_drones(self, user_id):
        user = self.get_user(user_id)
        return user.get('drones', [])
    
    def get_user_sabotage_teams(self, user_id):
        user = self.get_user(user_id)
        return user.get('sabotage_teams', [])
    
    def can_open_bronze_box(self, user_id):
        user = self.get_user(user_id)
        current_time = time.time()
        return current_time - user.get('last_bronze_box', 0) >= 86400
    
    def set_bronze_box_time(self, user_id):
        user = self.get_user(user_id)
        user['last_bronze_box'] = time.time()
    
    def create_support_ticket(self, user_id, message):
        ticket_id = len(self.support_tickets) + 1
        self.support_tickets[ticket_id] = {
            'user_id': user_id,
            'message': message,
            'status': 'open',
            'created_at': time.time()
        }
        return ticket_id
    
    def get_user_tickets(self, user_id):
        user_tickets = []
        for ticket_id, ticket in self.support_tickets.items():
            if ticket['user_id'] == user_id:
                user_tickets.append((ticket_id, ticket))
        return user_tickets
    
    def upgrade_defense(self, user_id):
        user = self.get_user(user_id)
        user['defense_level'] += 1
        return user['defense_level']
    
    def upgrade_cyber(self, user_id):
        user = self.get_user(user_id)
        user['cyber_level'] += 1
        return user['cyber_level']
    
    def upgrade_miner(self, user_id):
        user = self.get_user(user_id)
        user['miner_level'] += 1
        return user['miner_level']
    
    def can_claim_league_reward(self, user_id):
        user = self.get_user(user_id)
        current_time = time.time()
        return current_time - user.get('last_league_reward', 0) >= 604800  # 7 روز

db = SimpleDB()

def main_menu():
    keyboard = [
        [types.KeyboardButton(text="👤 پروفایل"), types.KeyboardButton(text="🛒 فروشگاه"), types.KeyboardButton(text="⚔️ حمله")],
        [types.KeyboardButton(text="🕵️ خرابکاری"), types.KeyboardButton(text="🏆 لیگ ها"), types.KeyboardButton(text="📦 باکس")],
        [types.KeyboardButton(text="⛏ ماینر"), types.KeyboardButton(text="🛡 دفاع"), types.KeyboardButton(text="📞 پشتیبانی")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ==================== تمام هندلرهای اصلی ====================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    username = f"@{message.from_user.username}" if message.from_user.username else "ناشناس"
    
    welcome_text = f"🎯 **به WarZone خوش آمدید {username}!** ⚔️\n\n💰 **موجودی اولیه**: {user['zp']:,} ZP\n👇 از منوی زیر انتخاب کنید:"
    
    await message.answer(welcome_text, reply_markup=main_menu())

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    help_text = """
🆘 **راهنمای WarZone**

🎮 **دستورات اصلی:**
/start - شروع بازی
/help - راهنما  
/support - پشتیبانی
/status - وضعیت بات

⚔️ **سیستم حمله:**
• حمله تکی - کسب ZP و XP
• حمله ترکیبی - با جنگنده‌ها
• حمله پهپادی - دمیج بیشتر

🛒 **فروشگاه:**
• موشک‌ها - قدرت حمله
• جنگنده‌ها - حمله ترکیبی
• پهپادها - حمله هوایی
• ویژه‌ها - آیتم‌های خاص

📦 **جعبه‌های شانس:**
• برنزی - رایگان (۲۴ ساعته)
• نقره‌ای - ۵,۰۰۰ ZP
• طلایی - ۲ جم
• الماس - ۵ جم

⛏ **ماینر:**
• تولید خودکار ZP
• قابل ارتقا تا سطح ۱۵
• برداشت هر ۱ ساعت

🛡 **سایر قابلیت‌ها:**
• سیستم دفاع
• خرابکاری
• لیگ‌ها
• پشتیبانی
"""
    await message.answer(help_text, reply_markup=main_menu())

@dp.message(Command("status"))
async def status_cmd(message: types.Message):
    total_users = len(db.users)
    total_attacks = sum(user['total_attacks'] for user in db.users.values())
    
    status_text = f"🤖 **وضعیت WarZone**\n\n👥 **کاربران**: {total_users}\n⚔️ **حملات**: {total_attacks}\n🟢 **وضعیت**: آنلاین"
    await message.answer(status_text, reply_markup=main_menu())

# ==================== پروفایل ====================
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
    
    profile_text = f"👤 **پروفایل جنگجو**\n\n⭐ **سطح**: {user['level']}\n📊 **XP**: {user['xp']}/{user['level'] * 100}\n💰 **ZP**: {user['zp']:,}\n💎 **جم**: {user['gem']}\n💪 **قدرت**: {user['power']}\n🛡️ **دفاع**: سطح {user['defense_level']}\n🔒 **امنیت**: سطح {user['cyber_level']}\n🎯 **حملات**: {user['total_attacks']:,}\n💥 **دمیج کل**: {user['total_damage']:,}\n📦 **جعبه برنزی**: {box_status}"
    
    await message.answer(profile_text, reply_markup=main_menu())

# ==================== سیستم حمله ====================
@dp.message(lambda message: message.text == "⚔️ حمله")
async def attack_handler(message: types.Message):
    keyboard = [
        [types.KeyboardButton(text="🎯 حمله تکی"), types.KeyboardButton(text="💥 حمله ترکیبی")],
        [types.KeyboardButton(text="🛸 حمله پهپادی"), types.KeyboardButton(text="🎯 حمله به کاربر")],
        [types.KeyboardButton(text="🔙 بازگشت")]
    ]
    attack_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    await message.answer(
        "⚔️ **سیستم حمله WarZone**\n\n"
        "🎯 **حمله تکی** - حمله ساده با موشک\n"
        "💥 **حمله ترکیبی** - با جنگنده (قدرت بیشتر)\n"
        "🛸 **حمله پهپادی** - حمله هوایی\n"
        "🎯 **حمله به کاربر** - حمله به کاربران دیگر\n\n"
        "👇 نوع حمله را انتخاب کنید:",
        reply_markup=attack_markup
    )

@dp.message(lambda message: message.text == "🎯 حمله تکی")
async def single_attack_handler(message: types.Message):
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
    
    base_damage = random.randint(80, 150)
    fighter_bonus = len(user_fighters) * 50
    total_damage = base_damage + fighter_bonus
    
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
    
    response = f"💥 **حمله ترکیبی موفق{critical_text}**{fighter_text}\n\n💥 **دمیج**: {total_damage}\n💰 **جایزه**: {reward} ZP\n⭐ **XP**: +{xp_gain}\n"
    
    if level_up:
        new_level = db.get_user(message.from_user.id)['level']
        response += f"🎉 **سطح شما ارتقا یافت!** (سطح {new_level})\n"
    
    response += f"\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)['zp']:,} ZP"
    
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
    
    base_damage = random.randint(60, 120)
    drone_bonus = len(user_drones) * 30
    total_damage = base_damage + drone_bonus
    
    is_critical = random.random() < 0.20
    if is_critical:
        total_damage *= 2
    
    reward = total_damage
    xp_gain = random.randint(12, 20)
    
    db.update_user_zp(message.from_user.id, reward)
    level_up = db.update_user_xp(message.from_user.id, xp_gain)
    
    user['total_attacks'] += 1
    user['total_damage'] += total_damage
    
    critical_text = " 🔥**بحرانی**" if is_critical else ""
    drone_text = f" ({len(user_drones)} پهپاد)"
    
    response = f"🛸 **حمله پهپادی موفق{critical_text}**{drone_text}\n\n💥 **دمیج**: {total_damage}\n💰 **جایزه**: {reward} ZP\n⭐ **XP**: +{xp_gain}\n"
    
    if level_up:
        new_level = db.get_user(message.from_user.id)['level']
        response += f"🎉 **سطح شما ارتقا یافت!** (سطح {new_level})\n"
    
    response += f"\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)['zp']:,} ZP"
    
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

# ==================== سیستم فروشگاه ====================
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
        "برای خرید ریپلای کنید: خرید موشک نامموشک"
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
        "برای خرید ریپلای کنید: خرید جنگنده نامجنگنده"
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
        "برای خرید ریپلای کنید: خرید پهپاد نامپهپاد"
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
        "برای خرید ریپلای کنید: خرید ویژه نامآیتم"
    )
    
    await message.answer(special_text, reply_markup=main_menu())

# ==================== سیستم باکس ====================
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

@dp.message(lambda message: message.text == "🥈 نقره‌ای")
async def silver_box_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    price = 5000
    
    if user['zp'] >= price:
        db.update_user_zp(message.from_user.id, -price)
        reward = random.randint(200, 500)
        db.update_user_zp(message.from_user.id, reward)
        
        response = f"🥈 **جعبه نقره‌ای** 🎉\n\n💰 **هزینه**: {price:,} ZP\n💰 **جایزه**: {reward} ZP\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)['zp']:,} ZP"
    else:
        response = f"❌ **موجودی ناکافی**\n\n💰 **قیمت جعبه**: {price:,} ZP\n💎 **موجودی شما**: {user['zp']:,} ZP"
    
    await message.answer(response, reply_markup=main_menu())

@dp.message(lambda message: message.text == "🥇 طلایی")
async def gold_bo
