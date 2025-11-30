# keyboards.py - منوهای کیبوردی WarZone
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# منوی اصلی
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 پروفایل"), KeyboardButton(text="🛒 فروشگاه"), KeyboardButton(text="⚔️ حمله")],
            [KeyboardButton(text="📦 باکس"), KeyboardButton(text="⛏ ماینر"), KeyboardButton(text="🛡 پدافند")],
            [KeyboardButton(text="🏆 لیگ"), KeyboardButton(text="🕵️ خرابکاری"), KeyboardButton(text="📞 پشتیبانی")]
        ],
        resize_keyboard=True
    )

# منوی حمله
def attack_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 حمله تکی"), KeyboardButton(text="💥 حمله ترکیبی")],
            [KeyboardButton(text="🛸 حمله پهپادی"), KeyboardButton(text="🛠 ترکیب‌های من")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

# منوی اصلی فروشگاه
def shop_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 موشک‌ها"), KeyboardButton(text="🛩 جنگنده‌ها")],
            [KeyboardButton(text="🛸 پهپادها"), KeyboardButton(text="🛡 پدافند")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

# منوی موشک‌ها
def missiles_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="تیرباران"), KeyboardButton(text="رعدآسا"), KeyboardButton(text="تندباد")],
            [KeyboardButton(text="زلزله"), KeyboardButton(text="آتشفشان"), KeyboardButton(text="توفان‌نو")],
            [KeyboardButton(text="🔙 بازگشت به فروشگاه")]
        ],
        resize_keyboard=True
    )

# منوی جنگنده‌ها
def fighters_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="شب‌پرواز"), KeyboardButton(text="توفان‌ساز")],
            [KeyboardButton(text="آذرخش"), KeyboardButton(text="شبح‌ساحل")],
            [KeyboardButton(text="🔙 بازگشت به فروشگاه")]
        ],
        resize_keyboard=True
    )

# منوی پهپادها
def drones_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="زنبورک"), KeyboardButton(text="سایفر"), KeyboardButton(text="ریزپرنده V")],
            [KeyboardButton(text="🔙 بازگشت به فروشگاه")]
        ],
        resize_keyboard=True
    )

# منوی پدافند
def defense_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="سپر-۹۵"), KeyboardButton(text="سدیفاکتور"), KeyboardButton(text="توربوشیلد")],
            [KeyboardButton(text="لایه نوری"), KeyboardButton(text="پدافند افسانه‌ای")],
            [KeyboardButton(text="🔙 بازگشت به فروشگاه")]
        ],
        resize_keyboard=True
    )

# منوی باکس
def boxes_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 برنزی"), KeyboardButton(text="🥈 نقره‌ای")],
            [KeyboardButton(text="🥇 طلایی"), KeyboardButton(text="💎 الماس")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

# منوی ماینر
def miner_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⛏ برداشت"), KeyboardButton(text="🔼 ارتقا ماینر")],
            [KeyboardButton(text="📊 اطلاعات ماینر"), KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

# منوی پشتیبانی
def support_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📩 ارسال تیکت"), KeyboardButton(text="📋 تیکت‌های من")],
            [KeyboardButton(text="🆘 راهنمای سریع"), KeyboardButton(text="📞 تماس با ادمین")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

# منوی ادمین
def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 مدیریت کاربران"), KeyboardButton(text="💎 انتقال منابع")],
            [KeyboardButton(text="📊 آمار بات"), KeyboardButton(text="📢 ارسال همگانی")],
            [KeyboardButton(text="🔙 بازگشت به منوی اصلی")]
        ],
        resize_keyboard=True
    )

# منوی مدیریت کاربران
def admin_users_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ افزودن ZP"), KeyboardButton(text="💎 افزودن جم"), KeyboardButton(text="⭐ افزودن لول")],
            [KeyboardButton(text="📊 اطلاعات کاربر"), KeyboardButton(text="🔍 جستجوی کاربر")],
            [KeyboardButton(text="🔙 بازگشت به پنل ادمین")]
        ],
        resize_keyboard=True
    )
