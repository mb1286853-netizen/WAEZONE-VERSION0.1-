# config.py - تنظیمات و آیتم‌های WarZone

# آیدی ادمین‌ها (آیدی عددی شما)
ADMINS = [7664487388, 987654321]  # جایگزین کن با آیدی واقعی خودت

SHOP_ITEMS = {
    "موشک‌ها": {
        "تیرباران": {"price": 400, "damage": 60, "level_required": 1},
        "رعدآسا": {"price": 700, "damage": 90, "level_required": 3},
        "تندباد": {"price": 1000, "damage": 120, "level_required": 5},
        "زلزله": {"price": 1500, "damage": 130, "level_required": 7},
        "آتشفشان": {"price": 8000, "damage": 2000, "level_required": 10},
        "توفان‌نو": {"price": 15000, "damage": 3000, "level_required": 15},
    },
    "جنگنده‌ها": {
        "شب‌پرواز": {"price": 5000, "damage": 200},
        "توفان‌ساز": {"price": 8000, "damage": 320},
        "آذرخش": {"price": 12000, "damage": 450},
        "شبح‌ساحل": {"price": 18000, "damage": 700},
    },
    "پهپادها": {
        "زنبورک": {"price": 3000, "damage": 90},
        "سایفر": {"price": 5000, "damage": 150},
        "ریزپرنده V": {"price": 8000, "damage": 250},
    },
    "پدافند": {
        "سپر-۹۵": {"price": 2000, "defense_bonus": 50, "level_required": 1},
        "سدیفاکتور": {"price": 5000, "defense_bonus": 100, "level_required": 3},
        "توربوشیلد": {"price": 10000, "defense_bonus": 200, "level_required": 5},
        "لایه نوری": {"price": 20000, "defense_bonus": 400, "level_required": 8},
        "پدافند افسانه‌ای": {"price": 50000, "defense_bonus": 1000, "level_required": 12},
    }
}

DEFENSE_SYSTEM = {
    "سپر-۹۵": {"level": 1, "block_chance": 0.1, "damage_reduction": 0.1},
    "سدیفاکتور": {"level": 2, "block_chance": 0.2, "damage_reduction": 0.2},
    "توربوشیلد": {"level": 3, "block_chance": 0.3, "damage_reduction": 0.3},
    "لایه نوری": {"level": 4, "block_chance": 0.4, "damage_reduction": 0.4},
    "پدافند افسانه‌ای": {"level": 5, "block_chance": 0.5, "damage_reduction": 0.5},
}

ATTACK_TYPES = {
    "تکی": {"base_damage": (40, 80), "xp_gain": (8, 15), "critical_chance": 0.15},
    "ترکیبی": {"base_damage": (80, 150), "xp_gain": (15, 25), "critical_chance": 0.15},
    "پهپادی": {"base_damage": (60, 120), "xp_gain": (12, 20), "critical_chance": 0.20},
}

MINER_CONFIG = {
    "base_income": 10,
    "upgrade_cost": 1000,
    "collection_cooldown": 3600,
}

BOXES = {
    "برنزی": {"price": 0, "cooldown": 86400},
    "نقره‌ای": {"price": 5000},
    "طلایی": {"price": 2, "currency": "gem"},
    "الماس": {"price": 5, "currency": "gem"},
}

SABOTAGE_TEAMS = {
    1: {"name": "تیم تازه‌کار", "success_rate": 0.3, "upgrade_cost": 1000},
    2: {"name": "تیم مبتدی", "success_rate": 0.4, "upgrade_cost": 2000},
    3: {"name": "تیم معمولی", "success_rate": 0.5, "upgrade_cost": 3500},
    4: {"name": "تیم حرفه‌ای", "success_rate": 0.6, "upgrade_cost": 5000},
    5: {"name": "تیم نخبه", "success_rate": 0.65, "upgrade_cost": 7000},
    6: {"name": "تیم ویژه", "success_rate": 0.7, "upgrade_cost": 10000},
    7: {"name": "تیم طلایی", "success_rate": 0.75, "upgrade_cost": 15000},
    8: {"name": "تیم الماسی", "success_rate": 0.8, "upgrade_cost": 20000},
    9: {"name": "تیم افسانه‌ای", "success_rate": 0.85, "upgrade_cost": 30000},
    10: {"name": "تیم فوق حرفه‌ای", "success_rate": 0.9, "upgrade_cost": 50000}
}

CYBER_TOWER = {
    1: {"name": "برج پایه", "defense_bonus": 10, "upgrade_cost": 2000},
    2: {"name": "برج پیشرفته", "defense_bonus": 20, "upgrade_cost": 4000},
    3: {"name": "برج حرفه‌ای", "defense_bonus": 35, "upgrade_cost": 7000},
    4: {"name": "برج طلایی", "defense_bonus": 55, "upgrade_cost": 11000},
    5: {"name": "برج الماسی", "defense_bonus": 80, "upgrade_cost": 16000},
    6: {"name": "برج امنیتی", "defense_bonus": 110, "upgrade_cost": 22000},
    7: {"name": "برج دفاعی", "defense_bonus": 145, "upgrade_cost": 29000},
    8: {"name": "برج نظامی", "defense_bonus": 185, "upgrade_cost": 37000},
    9: {"name": "برج استراتژیک", "defense_bonus": 230, "upgrade_cost": 46000},
    10: {"name": "برج ضد ضربه", "defense_bonus": 280, "upgrade_cost": 56000}
}
