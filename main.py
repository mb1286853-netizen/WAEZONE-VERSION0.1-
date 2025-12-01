# main.py - WarZone Bot Complete
import os
import asyncio
import logging
import sys
import random
import time
from datetime import datetime

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
    # برای Railway تست
    print("⚠️ توکن یافت نشد، حالت تست فعال شد")
    TOKEN = "dummy_token_for_healthcheck"
else:
    print(f"✅ توکن دریافت شد")

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import keyboards as kb
from config import SHOP_ITEMS, ATTACK_TYPES, ADMINS
from database import db

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
    
    user['zp'] += reward
    user['total_attacks'] += 1
    user['total_damage'] += reward
    
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
    
    user['zp'] += reward
    user['total_attacks'] += 1
    user['total_damage'] += total_damage
    
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
    
    user['zp'] += reward
    user['total_attacks'] += 1
    user['total_damage'] += total_damage
    
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

# ==================== سیستم ماینر ====================
@dp.message(F.text == "⛏ ماینر")
async def miner_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    miner_text = f"""
⛏ **ماینر منابع**

📊 **سطح**: {user.get('miner_level', 1)}
💰 **موجودی ماینر**: {user.get('miner_balance', 0):,} ZP
💎 **درآمد/ساعت**: {user.get('miner_income', 10):,} ZP

👇 عملیات مورد نظر را انتخاب کنید:
"""
    await message.answer(miner_text, reply_markup=kb.miner_menu())

@dp.message(F.text == "⛏ جمع‌آوری")
async def collect_miner_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    current_time = time.time()
    last_collect = user.get('miner_last_collect', 0)
    
    if current_time - last_collect >= 3600:  # 1 ساعت
        income = user.get('miner_income', 10) * user.get('miner_level', 1)
        user['miner_balance'] = user.get('miner_balance', 0) + income
        user['miner_last_collect'] = current_time
        user['zp'] += income
        
        response = f"""
✅ **جمع‌آوری موفق!**

💰 **دریافتی**: {income:,} ZP
⛏ موجودی ماینر: 0 ZP
💎 به کیف پول اضافه شد
💎 موجودی جدید: {user['zp']:,} ZP
"""
    else:
        remaining = 3600 - (current_time - last_collect)
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        response = f"⏳ زمان جمع‌آوری بعدی: {hours:02d}:{minutes:02d}"
    
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

@dp.message(F.text == "🎁 باکس برنزی")
async def bronze_box_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    current_time = time.time()
    
    if current_time - user.get('last_bronze_box', 0) >= 86400:
        reward = random.randint(100, 500)
        user['zp'] += reward
        user['last_bronze_box'] = current_time
        
        response = f"""
🎁 **باکس برنزی باز شد!**

💰 **جایزه**: {reward:,} ZP
🎉 مبارک! دوباره فردا
"""
    else:
        remaining = 86400 - (current_time - user['last_bronze_box'])
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        response = f"⏳ باکس برنزی بعدی: {hours:02d}:{minutes:02d}"
    
    await message.answer(response, reply_markup=kb.boxes_menu())

# ==================== سیستم لیگ ====================
@dp.message(F.text == "🏆 لیگ")
async def league_cmd(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    league_text = f"""
🏆 **سیستم لیگ**

📊 **لیگ فعلی**: {user.get('league', 'برنز')}
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
    your_power = user['power'] + (len(user.get('fighters', [])) * 20)
    
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

# ==================== هندلر پیام متنی برای تیکت ====================
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
    
    # خرید موشک
    if message.text in ["تیرباران", "رعدآسا", "تندباد"]:
        missile_name = message.text
        user_id = message.from_user.id
        
        if missile_name in SHOP_ITEMS["موشک‌ها"]:
            item_data = SHOP_ITEMS["موشک‌ها"][missile_name]
            user = db.get_user(user_id)
            
            if user['zp'] < item_data['price']:
                await message.answer(
                    f"❌ **موجودی ناکافی!**\n\n"
                    f"قیمت {missile_name}: {item_data['price']:,} ZP\n"
                    f"موجودی شما: {user['zp']:,} ZP",
                    reply_markup=kb.missiles_menu()
                )
                return
            
            if user['zp'] >= item_data['price']:
                user['zp'] -= item_data['price']
                user['missiles'][missile_name] = user['missiles'].get(missile_name, 0) + 1
                new_count = user['missiles'][missile_name]
                
                response = f"✅ **خرید موفق!**\n\n🚀 {missile_name} خریداری شد\n💰 هزینه: {item_data['price']:,} ZP\n📦 تعداد: {new_count} عدد\n💎 موجودی جدید: {user['zp']:,} ZP"
                await message.answer(response, reply_markup=kb.shop_main_menu())

# ==================== تابع اصلی ====================
async def main():
    print("🤖 بات در حال اجرا است...")
    
    try:
        # تست اتصال به تلگرام
        if TOKEN != "dummy_token_for_healthcheck":
            me = await bot.get_me()
            print(f"✅ ربات آماده: @{me.username}")
        else:
            print("⚠️ حالت تست: بات آماده است اما به تلگرام متصل نیست")
        
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.error(f"❌ خطا در اجرای بات: {e}")
        print(f"خطا: {e}")

if __name__ == "__main__":
    # ایجاد فولدرهای لازم
    for folder in ["backups", "logs"]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    asyncio.run(main())
