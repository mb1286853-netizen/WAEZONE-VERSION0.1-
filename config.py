import os
from typing import Dict

# دریافت توکن از متغیر محیطی رندر
TOKEN = os.getenv("TOKEN")

# اگر توکن وجود نداشت، از فایل env بخون (برای توسعه)
if not TOKEN:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        TOKEN = os.getenv("TOKEN")
    except ImportError:
        pass

# ادمین‌ها (جایگزین کن با ایدی‌های واقعی)
ADMIN_IDS = [123456789]

# تنظیمات پایه
MISSILE_DATA: Dict[str, Dict] = {
    "تیرباران": {"damage": 60, "price": 400, "min_level": 1},
    "رعدآسا": {"damage": 90, "price": 700, "min_level": 3},
}

FIGHTER_DATA: Dict[str, Dict] = {
    "شب‌پرواز": {"damage": 200, "price": 5000},
}

DRONE_DATA: Dict[str, Dict] = {
    "زنبورک": {"damage": 90, "price": 3000},
}

# شانس‌ها
CHANCE_CONFIG = {
    "critical_attack": 0.15,
    "block_missile": 0.25,
}

# پیام‌ها
MESSAGES = {
    "welcome": "🎯 به WarZone خوش آمدید! ⚔️",
    "attack_success": "⚔️ حمله موفق!",
}
