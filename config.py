import os
from typing import Dict, List

# تنظیمات اصلی
TOKEN = os.getenv("TOKEN")
ADMIN_IDS = [123456789]  # جایگزین کن با ادمین واقعی

# قیمت‌ها و مشخصات موشک‌ها
MISSILE_DATA: Dict[str, Dict] = {
    "تیرباران": {"damage": 60, "price": 400, "min_level": 1},
    "رعدآسا": {"damage": 90, "price": 700, "min_level": 3},
    "تندباد": {"damage": 120, "price": 1000, "min_level": 5},
    "زلزله": {"damage": 130, "price": 1500, "min_level": 7},
    "آتشفشان": {"damage": 2000, "price": 8000, "min_level": 0},
    "توفان‌نو": {"damage": 3000, "price": 15000, "min_level": 0},
    "خاموش‌کن": {"damage": 0, "price": 20000, "min_level": 0, "special": "قطع سیستم"}
}

# جنگنده‌ها
FIGHTER_DATA: Dict[str, Dict] = {
    "شب‌پرواز": {"damage": 200, "price": 5000},
    "توفان‌ساز": {"damage": 320, "price": 8000},
    "آذرخش": {"damage": 450, "price": 12000},
    "شبح‌ساحل": {"damage": 700, "price": 18000}
}

# پهپادها
DRONE_DATA: Dict[str, Dict] = {
    "زنبورک": {"damage": 90, "price": 3000},
    "سایفر": {"damage": 150, "price": 5000},
    "ریزپرنده V": {"damage": 250, "price": 8000}
}

# موشک‌های آخرالزمانی
APOCALYPSE_MISSILES: Dict[str, Dict] = {
    "عقاب‌توفان": {"damage": 8000, "price": 30000, "gems": 3},
    "اژدهای‌آتش": {"damage": 12500, "price": 45000, "gems": 5},
    "فینیکس": {"damage": 18000, "price": 60000, "gems": 8}
}

# سیستم دفاع
DEFENSE_SYSTEMS: Dict[str, Dict] = {
    "سپر-۹۵": {"level": 1, "block_chance": 0.1, "upgrade_cost": 500},
    "سدیفاکتور": {"level": 2, "block_chance": 0.2, "upgrade_cost": 1000},
    "توربوشیلد": {"level": 3, "block_chance": 0.3, "upgrade_cost": 2000},
    "لایه نوری": {"level": 4, "block_chance": 0.4, "upgrade_cost": 4000},
    "پدافند افسانه‌ای": {"level": 5, "block_chance": 0.5, "upgrade_cost": 8000}
}

# سیستم امنیت سایبری
CYBER_SECURITY: Dict[str, Dict] = {
    "دیوار آتش": {"level": 1, "detection_chance": 0.2, "reduce_loot": 0.15, "upgrade_cost": 600},
    "نظارت پیشرفته": {"level": 2, "detection_chance": 0.35, "reduce_loot": 0.3, "upgrade_cost": 1200},
    "رمزنگاری کوانتومی": {"level": 3, "detection_chance": 0.5, "reduce_loot": 0.5, "upgrade_cost": 2400},
    "هوش مصنوعی دفاعی": {"level": 4, "detection_chance": 0.75, "reduce_loot": 0.7, "upgrade_cost": 4800},
    "هوش مصنوعی امنیتی": {"level": 5, "detection_chance": 0.95, "reduce_loot": 0.9, "upgrade_cost": 9600}
}

# جعبه‌های شانس
LOOTBOXES: Dict[str, Dict] = {
    "برنزی": {"price": 0, "cooldown": 86400, "rewards": {"min_zp": 50, "max_zp": 200, "missile_chance": 0.3}},
    "نقره‌ای": {"price": 5000, "cooldown": 0, "rewards": {"min_zp": 200, "max_zp": 500, "missile_chance": 0.5}},
    "طلایی": {"price_gem": 2, "cooldown": 0, "rewards": {"min_zp": 500, "max_zp": 1500, "missile_chance": 0.7}},
    "الماس": {"price_gem": 5, "cooldown": 0, "rewards": {"min_zp": 1000, "max_zp": 3000, "missile_chance": 0.9}},
    "افسانه‌ای": {"price_gem": 15, "cooldown": 0, "rewards": {"min_zp": 5000, "max_zp": 10000, "missile_chance": 1.0}}
}

# سیستم ماینر
MINER_CONFIG = {
    "base_income": 100,
    "upgrade_cost_multiplier": 500,
    "max_balance_time": 10800,  # 3 ساعت
    "levels": {
        1: {"income": 100, "upgrade_cost": 500},
        2: {"income": 200, "upgrade_cost": 1000},
        3: {"income": 300, "upgrade_cost": 1500},
        4: {"income": 400, "upgrade_cost": 2000},
        5: {"income": 500, "upgrade_cost": 2500},
        6: {"income": 600, "upgrade_cost": 3000},
        7: {"income": 700, "upgrade_cost": 3500},
        8: {"income": 800, "upgrade_cost": 4000},
        9: {"income": 900, "upgrade_cost": 4500},
        10: {"income": 1000, "upgrade_cost": 5000},
        11: {"income": 1200, "upgrade_cost": 6000},
        12: {"income": 1400, "upgrade_cost": 7000},
        13: {"income": 1600, "upgrade_cost": 8000},
        14: {"income": 1800, "upgrade_cost": 9000},
        15: {"income": 2000, "upgrade_cost": 10000}
    }
}

# سیستم لیگ
LEAGUES = {
    "برنز": {"min_level": 1, "reward": 1000},
    "نقره": {"min_level": 5, "reward": 3000},
    "طلا": {"min_level": 10, "reward": 7000},
    "پلاتین": {"min_level": 15, "reward": 15000},
    "افسانه‌ای": {"min_level": 20, "reward": 30000}
}

# شانس‌ها
CHANCE_CONFIG = {
    "critical_attack": 0.15,  # 15%
    "block_missile": 0.25,    # 25%
    "loot_success": 0.6,      # 60%
    "sabotage_success": 0.7,  # 70%
    "counter_attack": 0.3     # 30%
}

# پیام‌ها
MESSAGES = {
    "welcome": "🎯 به WarZone خوش آمدید! ⚔️",
    "attack_success": "⚔️ حمله موفق!",
    "attack_critical": "🔥 حمله بحرانی!",
    "not_enough_zp": "❌ موجودی ZP ناکافی!",
    "level_up": "🎉 سطح شما ارتقا یافت!",
    "miner_claimed": "⛏️ برداشت از ماینر انجام شد!",
    "lootbox_opened": "📦 جعبه شانس باز شد!"
}
