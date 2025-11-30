from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    """منوی اصلی با چیدمان 3x3 دقیقاً مطابق درخواست"""
    keyboard = [
        [KeyboardButton(text="👤 پروفایل"), KeyboardButton(text="🛒 فروشگاه"), KeyboardButton(text="⚔️ حمله")],
        [KeyboardButton(text="🕵️ خرابکاری"), KeyboardButton(text="🏆 لیگ ها"), KeyboardButton(text="📦 باکس")],
        [KeyboardButton(text="⛏ ماینر"), KeyboardButton(text="🛡 دفاع"), KeyboardButton(text="⚙️ تنظیمات")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard, 
        resize_keyboard=True,
        input_field_placeholder="دستور خود را انتخاب کنید..."
    )

def attack_menu():
    """منوی حمله"""
    keyboard = [
        [KeyboardButton(text="🎯 حمله تکی"), KeyboardButton(text="💥 حمله ترکیبی")],
        [KeyboardButton(text="🔄 انتقام"), KeyboardButton(text="📋 تاریخچه حملات")],
        [KeyboardButton(text="🔙 بازگشت")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def shop_menu():
    """منوی فروشگاه"""
    keyboard = [
        [KeyboardButton(text="🚀 موشک‌ها"), KeyboardButton(text="🛩 جنگنده‌ها")],
        [KeyboardButton(text="🛸 پهپادها"), KeyboardButton(text="💎 ویژه‌ها")],
        [KeyboardButton(text="🔙 بازگشت")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def boxes_menu():
    """منوی باکس‌ها"""
    keyboard = [
        [KeyboardButton(text="📦 برنزی"), KeyboardButton(text="🥈 نقره‌ای")],
        [KeyboardButton(text="🥇 طلایی"), KeyboardButton(text="💎 الماس")],
        [KeyboardButton(text="🔙 بازگشت")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def miner_menu():
    """منوی ماینر"""
    keyboard = [
        [KeyboardButton(text="💰 برداشت"), KeyboardButton(text="🔼 ارتقا")],
        [KeyboardButton(text="📊 وضعیت"), KeyboardButton(text="🔙 بازگشت")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def back_only():
    """فقط دکمه بازگشت"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 بازگشت")]],
        resize_keyboard=True
    )
    def sabotage_menu():
    """منوی خرابکاری"""
    keyboard = [
        [KeyboardButton(text="🕵️ نفوذی"), KeyboardButton(text="📡 الکترونیکی")],
        [KeyboardButton(text="🔒 اطلاعاتی"), KeyboardButton(text="📊 وضعیت تیم")],
        [KeyboardButton(text="🔙 بازگشت")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
