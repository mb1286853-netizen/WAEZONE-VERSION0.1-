import time
from aiogram import types
from database import db
from config import MINER_CONFIG, MESSAGES

async def miner_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    miner_level = user[9]
    miner_income = MINER_CONFIG['levels'][miner_level]['income']
    upgrade_cost = MINER_CONFIG['levels'][miner_level]['upgrade_cost']
    
    # محاسبه موجودی قابل برداشت
    current_time = int(time.time())
    last_claim = user[11] or current_time
    time_passed = current_time - last_claim
    max_balance_time = MINER_CONFIG['max_balance_time']
    
    if time_passed > max_balance_time:
        time_passed = max_balance_time
    
    potential_income = (time_passed // 3600) * miner_income
    current_balance = user[10] + potential_income
    
    miner_text = (
        f"⛏️ **سیستم ماینر WarZone**\n\n"
        f"💰 **تولید ساعتی**: {miner_income} ZP/ساعت\n"
        f"📊 **سطح ماینر**: {miner_level}\n"
        f"💎 **موجودی قابل برداشت**: {current_balance:,} ZP\n"
        f"🔼 **هزینه ارتقا**: {upgrade_cost:,} ZP\n\n"
    )
    
    if time_passed < 3600:
        remaining = 3600 - time_passed
        minutes = remaining // 60
        miner_text += f"⏳ **زمان تا برداشت بعدی**: {minutes} دقیقه\n\n"
    
    miner_text += (
        "**دستورات:**\n"
        "• <code>برداشت ماینر</code> - دریافت ZP\n"
        "• <code>ارتقا ماینر</code> - ارتقای سطح\n"
        "• <code>وضعیت ماینر</code> - اطلاعات دقیق"
    )
    
    from main import main_menu
    await message.answer(miner_text, reply_markup=main_menu())

async def claim_miner_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    current_time = int(time.time())
    last_claim = user[11] or current_time
    time_passed = current_time - last_claim
    
    if time_passed < 3600:
        remaining = 3600 - time_passed
        minutes = remaining // 60
        await message.answer(
            f"⏳ **هنوز آماده نیست!**\n\n"
            f"⏰ **زمان باقی‌مانده**: {minutes} دقیقه\n"
            f"💰 **موجودی فعلی**: {user[10]:,} ZP\n\n"
            f"لطفاً بعداً تلاش کنید.",
            reply_markup=main_menu()
        )
        return
    
    # محاسبه درآمد
    hours_passed = time_passed // 3600
    max_hours = MINER_CONFIG['max_balance_time'] // 3600
    if hours_passed > max_hours:
        hours_passed = max_hours
    
    miner_income = MINER_CONFIG['levels'][user[9]]['income']
    income = hours_passed * miner_income
    total_balance = user[10] + income
    
    # برداشت
    db.update_user_zp(message.from_user.id, total_balance)
    
    # ریست کردن ماینر
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET miner_balance = 0, last_miner_claim = ? WHERE user_id = ?',
        (current_time, message.from_user.id)
    )
    conn.commit()
    
    new_balance = db.get_user(message.from_user.id)[4]
    
    response = (
        f"⛏️ **{MESSAGES['miner_claimed']}**\n\n"
        f"💰 **مبلغ برداشت**: {total_balance:,} ZP\n"
        f"⏰ **ساعات کاری**: {hours_passed} ساعت\n"
        f"📊 **نرخ ساعتی**: {miner_income} ZP\n"
        f"💎 **موجودی جدید**: {new_balance:,} ZP\n\n"
        f"✅ برداشت بعدی: ۱ ساعت دیگر"
    )
    
    db.log_activity(message.from_user.id, "miner_claim", f"{total_balance} ZP")
    
    from main import main_menu
    await message.answer(response, reply_markup=main_menu())
