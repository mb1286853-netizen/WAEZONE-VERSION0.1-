# keyboards.py - کیبوردهای کامل WarZone
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# منوی اصلی
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="👤 پروفایل"),
        KeyboardButton(text="⚔️ حمله"),
        KeyboardButton(text="🛒 فروشگاه")
    )
    builder.row(
        KeyboardButton(text="⛏ ماینر"),
        KeyboardButton(text="📦 باکس‌ها"),
        KeyboardButton(text="🏆 لیگ")
    )
    builder.row(
        KeyboardButton(text="🔧 خرابکاری"),
        KeyboardButton(text="🛡 مدافعان"),
        KeyboardButton(text="📞 پشتیبانی")
    )
    return builder.as_markup(resize_keyboard=True)

# منوی حمله
def attack_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🎯 حمله تکی"),
        KeyboardButton(text="💥 حمله ترکیبی"),
        KeyboardButton(text="🛸 حمله پهپادی")
    )
    builder.row(
        KeyboardButton(text="⚡ حمله سریع"),
        KeyboardButton(text="🎪 حمله به کمپ"),
        KeyboardButton(text="🏰 محاصره قلعه")
    )
    builder.row(KeyboardButton(text="🔙 بازگشت"))
    return builder.as_markup(resize_keyboard=True)

# منوی فروشگاه
def shop_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🚀 موشک‌ها"),
        KeyboardButton(text="🛩 جنگنده‌ها"),
        KeyboardButton(text="🛸 پهپادها")
    )
    builder.row(
        KeyboardButton(text="🛡 پدافند"),
        KeyboardButton(text="⚡ ارتقا قدرت"),
        KeyboardButton(text="💎 خرید جم")
    )
    builder.row(KeyboardButton(text="🔙 بازگشت"))
    return builder.as_markup(resize_keyboard=True)

# منوی ماینر
def miner_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="⛏ جمع‌آوری"),
        KeyboardButton(text="⬆️ ارتقا ماینر")
    )
    builder.row(
        KeyboardButton(text="📊 اطلاعات ماینر"),
        KeyboardButton(text="⚡ افزایش درآمد")
    )
    builder.row(KeyboardButton(text="🔙 بازگشت"))
    return builder.as_markup(resize_keyboard=True)

# منوی باکس‌ها
def boxes_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🎁 باکس برنزی"),
        KeyboardButton(text="🥈 باکس نقره‌ای")
    )
    builder.row(
        KeyboardButton(text="🥇 باکس طلایی"),
        KeyboardButton(text="💎 باکس الماس")
    )
    builder.row(KeyboardButton(text="🔙 بازگشت"))
    return builder.as_markup(resize_keyboard=True)

# منوی لیگ
def league_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🏆 رده‌بندی"),
        KeyboardButton(text="⚔️ مبارزه لیگ"),
        KeyboardButton(text="🎁 دریافت جایزه")
    )
    builder.row(
        KeyboardButton(text="📊 امتیازات"),
        KeyboardButton(text="📈 رتبه من")
    )
    builder.row(KeyboardButton(text="🔙 بازگشت"))
    return builder.as_markup(resize_keyboard=True)

# منوی خرابکاری
def sabotage_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🎯 حمله خرابکارانه"),
        KeyboardButton(text="👥 استخدام تیم"),
        KeyboardButton(text="⬆️ ارتقا خرابکاری")
    )
    builder.row(
        KeyboardButton(text="🔍 جاسوسی"),
        KeyboardButton(text="💰 سرقت منابع"),
        KeyboardButton(text="⚡ قطع ارتباط")
    )
    builder.row(KeyboardButton(text="🔙 بازگشت"))
    return builder.as_markup(resize_keyboard=True)

# منوی مدافعان
def defenders_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🛡 دفاع از پایگاه"),
        KeyboardButton(text="🎯 انتخاب هدف"),
        KeyboardButton(text="⚔️ حمله به مدافع")
    )
    builder.row(
        KeyboardButton(text="🏹 مستقر کردن نیرو"),
        KeyboardButton(text="🔧 تعمیر استحکامات"),
        KeyboardButton(text="📊 وضعیت دفاع")
    )
    builder.row(KeyboardButton(text="🔙 بازگشت"))
    return builder.as_markup(resize_keyboard=True)

# منوی پشتیبانی
def support_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📩 ایجاد تیکت"),
        KeyboardButton(text="📋 تیکت‌های من"),
        KeyboardButton(text="ℹ️ راهنمایی")
    )
    builder.row(KeyboardButton(text="🔙 بازگشت"))
    return builder.as_markup(resize_keyboard=True)

# منوی ادمین
def admin_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📊 آمار کلی"),
        KeyboardButton(text="👥 مدیریت کاربران"),
        KeyboardButton(text="📢 ارسال همگانی")
    )
    builder.row(
        KeyboardButton(text="💾 ایجاد بکاپ"),
        KeyboardButton(text="🔧 تنظیمات بات"),
        KeyboardButton(text="⚠️ مدیریت تیکت‌ها")
    )
    builder.row(
        KeyboardButton(text="💰 مدیریت ارز"),
        KeyboardButton(text="🎯 تنظیم رویداد"),
        KeyboardButton(text="📈 گزارش‌گیری")
    )
    builder.row(KeyboardButton(text="🔙 بازگشت"))
    return builder.as_markup(resize_keyboard=True)

# اینلاین کیبورد برای موشک‌ها
def missiles_inline_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="تیرباران - 400 ZP", callback_data="buy_missile_تیرباران"),
        InlineKeyboardButton(text="رعدآسا - 700 ZP", callback_data="buy_missile_رعدآسا")
    )
    builder.row(
        InlineKeyboardButton(text="تندباد - 1,000 ZP", callback_data="buy_missile_تندباد"),
        InlineKeyboardButton(text="زلزله - 1,500 ZP", callback_data="buy_missile_زلزله")
    )
    builder.row(
        InlineKeyboardButton(text="آتشفشان - 8,000 ZP", callback_data="buy_missile_آتشفشان"),
        InlineKeyboardButton(text="توفان‌نو - 15,000 ZP", callback_data="buy_missile_توفان‌نو")
    )
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_shop"))
    return builder.as_markup()

# منوی ارتقا امنیت سایبری
def cyber_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🔐 سطح ۱: فایروال پایه"),
        KeyboardButton(text="🛡 سطح ۲: کدگذاری"),
        KeyboardButton(text="⚡ سطح ۳: آنتی‌ویروس")
    )
    builder.row(
        KeyboardButton(text="🔒 سطح ۴: سیستم تشخیص"),
        KeyboardButton(text="🚫 سطح ۵: محافظت پیشرفته"),
        KeyboardButton(text="🛡 سطح ۶: دیوار آتش")
    )
    builder.row(
        KeyboardButton(text="⚡ سطح ۷: مانیتورینگ"),
        KeyboardButton(text="🔐 سطح ۸: رمزنگاری"),
        KeyboardButton(text="🚨 سطح ۹: هشدار هوشمند")
    )
    builder.row(
        KeyboardButton(text="🛡 سطح ۱۰: ضد ضربه"),
        KeyboardButton(text="🔙 بازگشت")
    )
    return builder.as_markup(resize_keyboard=True)
