import random
from aiogram import types
from database import db
from config import MISSILE_DATA, CHANCE_CONFIG, MESSAGES

async def attack_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🎯 حمله تکی"), types.KeyboardButton(text="💥 حمله ترکیبی")],
            [types.KeyboardButton(text="🔄 انتقام"), types.KeyboardButton(text="📋 تاریخچه حملات")],
            [types.KeyboardButton(text="🔙 منوی اصلی")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "⚔️ **سیستم حمله WarZone**\n\n"
        "🎯 **حمله تکی** - استفاده از یک موشک\n"
        "💥 **حمله ترکیبی** - ترکیب جنگنده و موشک\n"
        "🔄 **انتقام** - حمله متقابل\n"
        "📋 **تاریخچه** - مشاهده حملات گذشته\n\n"
        f"🔥 **شانس بحرانی**: {CHANCE_CONFIG['critical_attack']*100}%\n"
        f"🛡️ **شانس بلاک**: {CHANCE_CONFIG['block_missile']*100}%\n\n"
        "👇 نوع حمله را انتخاب کنید:",
        reply_markup=keyboard
    )

async def single_attack_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    
    # شانس حمله بحرانی
    is_critical = random.random() < CHANCE_CONFIG['critical_attack']
    base_reward = random.randint(40, 80)
    reward = base_reward * 2 if is_critical else base_reward
    xp_gain = random.randint(8, 15)
    
    # اعطای جایزه
    db.update_user_zp(message.from_user.id, reward)
    level_up = db.update_user_xp(message.from_user.id, xp_gain)
    
    # ثبت آمار
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET total_attacks = total_attacks + 1, total_damage = total_damage + ? WHERE user_id = ?',
        (reward, message.from_user.id)
    )
    
    # ثبت حمله
    cursor.execute(
        'INSERT INTO attacks (attacker_id, damage, reward, attack_type, is_critical) VALUES (?, ?, ?, ?, ?)',
        (message.from_user.id, reward, reward, "single", is_critical)
    )
    conn.commit()
    
    critical_text = " 🔥**بحرانی**" if is_critical else ""
    
    response = f"⚔️ **{MESSAGES['attack_success']}{critical_text}**\n\n"
    response += f"💰 **جایزه**: {reward} ZP\n"
    response += f"⭐ **XP**: +{xp_gain}\n"
    
    if level_up:
        new_level = db.get_user(message.from_user.id)[2]
        response += f"🎉 **{MESSAGES['level_up']}** (سطح {new_level})\n"
    
    response += f"\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)[4]:,} ZP"
    
    db.log_activity(message.from_user.id, "attack", f"حمله تکی - {reward} ZP")
    
    from main import main_menu
    await message.answer(response, reply_markup=main_menu())

async def combo_attack_handler(message: types.Message):
    user = db.get_user(message.from_user.id)
    user_fighters = db.get_user_fighters(message.from_user.id)
    
    if not user_fighters:
        await message.answer(
            "❌ **جنگنده ندارید!**\n\n"
            "برای حمله ترکیبی نیاز به حداقل یک جنگنده دارید.\n"
            "به فروشگاه مراجعه کنید و جنگنده بخرید.",
            reply_markup=main_menu()
        )
        return
    
    # محاسبه دمیج ترکیبی
    base_damage = random.randint(80, 150)
    fighter_bonus = len(user_fighters) * 50
    total_damage = base_damage + fighter_bonus
    
    # شانس بحرانی
    is_critical = random.random() < CHANCE_CONFIG['critical_attack']
    if is_critical:
        total_damage *= 2
    
    reward = total_damage
    xp_gain = random.randint(15, 25)
    
    # اعطای جایزه
    db.update_user_zp(message.from_user.id, reward)
    level_up = db.update_user_xp(message.from_user.id, xp_gain)
    
    # ثبت آمار
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET total_attacks = total_attacks + 1, total_damage = total_damage + ? WHERE user_id = ?',
        (total_damage, message.from_user.id)
    )
    
    # ثبت حمله
    cursor.execute(
        'INSERT INTO attacks (attacker_id, damage, reward, attack_type, is_critical) VALUES (?, ?, ?, ?, ?)',
        (message.from_user.id, total_damage, reward, "combo", is_critical)
    )
    conn.commit()
    
    critical_text = " 🔥**بحرانی**" if is_critical else ""
    fighter_text = f" ({len(user_fighters)} جنگنده)"
    
    response = f"💥 **حمله ترکیبی موفق{critical_text}**{fighter_text}\n\n"
    response += f"💥 **دمیج**: {total_damage}\n"
    response += f"💰 **جایزه**: {reward} ZP\n"
    response += f"⭐ **XP**: +{xp_gain}\n"
    
    if level_up:
        new_level = db.get_user(message.from_user.id)[2]
        response += f"🎉 **{MESSAGES['level_up']}** (سطح {new_level})\n"
    
    response += f"\n💎 **موجودی جدید**: {db.get_user(message.from_user.id)[4]:,} ZP"
    
    db.log_activity(message.from_user.id, "combo_attack", f"حمله ترکیبی - {reward} ZP")
    
    from main import main_menu
    await message.answer(response, reply_markup=main_menu())
