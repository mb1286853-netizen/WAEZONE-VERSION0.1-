# keyboards.py - نسخه کامل
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 پروفایل"), KeyboardButton(text="🛒 فروشگاه")],
            [KeyboardButton(text="⚔️ حمله"), KeyboardButton(text="📦 باکس")],
            [KeyboardButton(text="⛏ ماینر"), KeyboardButton(text="📞 پشتیبانی")],
            [KeyboardButton(text="🦠 خرابکاری"), KeyboardButton(text="🏢 برج امنیت")],
            [KeyboardButton(text="🏆 لیگ"), KeyboardButton(text="🆘 راهنما")]
        ],
        resize_keyboard=True
    )

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 آمار بات"), KeyboardButton(text="👥 مدیریت کاربران")],
            [KeyboardButton(text="📢 ارسال همگانی"), KeyboardButton(text="🎁 هدیه همگانی")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def admin_users_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ افزودن ZP"), KeyboardButton(text="💎 افزودن جم")],
            [KeyboardButton(text="⭐ افزودن لول"), KeyboardButton(text="📊 اطلاعات کاربر")],
            [KeyboardButton(text="🔙 بازگشت به پنل ادمین")]
        ],
        resize_keyboard=True
    )

def shop_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 موشک‌ها"), KeyboardButton(text="🛩 جنگنده‌ها")],
            [KeyboardButton(text="🛸 پهپادها"), KeyboardButton(text="🛡 پدافند")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def attack_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 حمله تکی"), KeyboardButton(text="💥 حمله ترکیبی")],
            [KeyboardButton(text="🛸 حمله پهپادی"), KeyboardButton(text="🛡 حمله به مدافع")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def boxes_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 برنزی"), KeyboardButton(text="🥈 نقره‌ای")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def support_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📩 ارسال تیکت"), KeyboardButton(text="📋 تیکت‌های من")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def missiles_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="تیرباران"), KeyboardButton(text="رعدآسا")],
            [KeyboardButton(text="تندباد"), KeyboardButton(text="زلزله")],
            [KeyboardButton(text="آتشفشان"), KeyboardButton(text="توفان‌نو")],
            [KeyboardButton(text="🔙 بازگشت به فروشگاه")]
        ],
        resize_keyboard=True
    )

def fighters_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="شب‌پرواز"), KeyboardButton(text="توفان‌ساز")],
            [KeyboardButton(text="آذرخش"), KeyboardButton(text="شبح‌ساحل")],
            [KeyboardButton(text="🔙 بازگشت به فروشگاه")]
        ],
        resize_keyboard=True
    )

def drones_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="زنبورک"), KeyboardButton(text="سایفر")],
            [KeyboardButton(text="ریزپرنده V"), KeyboardButton(text="🔙 بازگشت به فروشگاه")]
        ],
        resize_keyboard=True
    )

def defense_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="سپر-۹۵"), KeyboardButton(text="سدیفاکتور")],
            [KeyboardButton(text="توربوشیلد"), KeyboardButton(text="لایه نوری")],
            [KeyboardButton(text="پدافند افسانه‌ای"), KeyboardButton(text="🔙 بازگشت به فروشگاه")]
        ],
        resize_keyboard=True
    )
