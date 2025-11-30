from aiogram import types
from aiogram.filters import Command
from database import db
from config import MESSAGES

async def start_command(message: types.Message):
    user = db.get_user(message.from_user.id)
    username = f"@{message.from_user.username}" if message.from_user.username else "ناشناس"
    
    welcome_text = (
        f"{MESSAGES['welcome']}\n\n"
        f"🛡️ **یک بازی استراتژیک جنگی پیشرفته**\n\n"
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
    
    db.log_activity(message.from_user.id, "start", "ورود به ربات")
    
    from main import main_menu
    await message.answer(welcome_text, reply_markup=main_menu())

async def profile_command(message: types.Message):
    user = db.get_user(message.from_user.id)
    stats = db.get_user_stats(message.from_user.id)
    
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
        f"🎯 **حملات**: {stats['total_attacks']:,}\n"
        f"💥 **دمیج کل**: {stats['total_damage']:,}\n\n"
        f"📅 **عضویت**: {user[15].split()[0]}"
    )
    
    db.log_activity(message.from_user.id, "profile_view")
    
    from main import main_menu
    await message.answer(profile_text, reply_markup=main_menu())

async def stats_command(message: types.Message):
    user = db.get_user(message.from_user.id)
    stats = db.get_user_stats(message.from_user.id)
    total_users = db.get_total_users()
    total_attacks = db.get_total_attacks()
    
    stats_text = (
        "📊 **آمار جهانی WarZone**\n\n"
        f"👥 **کل کاربران**: {total_users:,}\n"
        f"🎯 **حملات شما**: {stats['total_attacks']:,}\n"
        f"💥 **دمیج کل شما**: {stats['total_damage']:,}\n"
        f"⭐ **سطح شما**: {user[2]}\n"
        f"💰 **ZP شما**: {user[4]:,}\n"
        f"💎 **جم شما**: {user[5]}\n\n"
        f"🏆 **رتبه تخمینی**: Top {max(1, int((user[2] / total_users) * 100))}%\n\n"
        f"🕒 **آخرین به‌روزرسانی**: هم‌اکنون"
    )
    
    db.log_activity(message.from_user.id, "stats_view")
    
    from main import main_menu
    await message.answer(stats_text, reply_markup=main_menu())
