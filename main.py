# در بخش imports اضافه کن:
from keyboards import sabotage_menu, defense_menu, league_menu

# هندلرهای جدید رو اضافه کن بعد از هندلرهای موجود:

@dp.message(lambda message: message.text == "🕵️ خرابکاری")
async def sabotage_handler(message: types.Message):
    await message.answer(
        "🕵️ **سیستم خرابکاری WarZone**\n\n"
        "**انواع تیم خرابکاری:**\n"
        "• **نفوذی** - کاهش پدافند دشمن\n"
        "• **الکترونیکی** - غیرفعال کردن امنیت\n"
        "• **اطلاعاتی** - افزایش غارت\n\n"
        "تیم مورد نظر را انتخاب کنید:",
        reply_markup=sabotage_menu()
    )

@dp.message(lambda message: message.text == "🕵️ نفوذی")
async def infiltrate_sabotage(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        
        # شانس موفقیت
        success_chance = 0.7
        is_success = random.random() < success_chance
        
        if is_success:
            reward = random.randint(100, 300)
            db.update_user_zp(message.from_user.id, reward)
            
            response = (
                f"🕵️ **خرابکاری نفوذی موفق!**\n\n"
                f"✅ **عملیات**: نفوذ به سیستم دفاعی\n"
                f"💰 **جایزه**: {reward} ZP\n"
                f"🎯 **اثر**: کاهش ۲۰٪ پدافند دشمن\n"
                f"💎 **موجودی جدید**: {db.get_user(message.from_user.id)[4]:,} ZP"
            )
        else:
            response = (
                f"🕵️ **خرابکاری ناموفق!**\n\n"
                f"❌ **عملیات**: نفوذ به سیستم دفاعی\n"
                f"⚠️ **هشدار**: تیم شما شناسایی شد\n"
                f"💡 **توصیه**: سطح تیم را ارتقا دهید"
            )
        
        db.log_activity(message.from_user.id, "sabotage", "خرابکاری نفوذی")
        await message.answer(response, reply_markup=sabotage_menu())
    except Exception as e:
        await message.answer("❌ خطا در خرابکاری", reply_markup=sabotage_menu())

@dp.message(lambda message: message.text == "🛡 دفاع")
async def defense_handler(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        
        defense_text = (
            f"🛡️ **سیستم دفاع WarZone**\n\n"
            f"**سطح فعلی**: {user[7]}\n"
            f"**شانس بلاک**: {user[7] * 10}%\n"
            f"**کاهش دمیج**: {user[7] * 5}%\n\n"
            f"🔼 **هزینه ارتقا**: {user[7] * 1000} ZP\n\n"
            "گزینه مورد نظر را انتخاب کنید:"
        )
        
        await message.answer(defense_text, reply_markup=defense_menu())
    except Exception as e:
        await message.answer("❌ خطا در نمایش دفاع", reply_markup=main_menu())

@dp.message(lambda message: message.text == "🛡️ ارتقا دفاع")
async def upgrade_defense(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        upgrade_cost = user[7] * 1000
        
        if user[4] >= upgrade_cost:
            db.update_user_zp(message.from_user.id, -upgrade_cost)
            
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET defense_level = defense_level + 1 WHERE user_id = ?', 
                          (message.from_user.id,))
            conn.commit()
            
            new_level = db.get_user(message.from_user.id)[7]
            new_balance = db.get_user(message.from_user.id)[4]
            
            response = (
                f"🛡️ **ارتقای دفاع موفق!**\n\n"
                f"📊 **سطح جدید**: {new_level}\n"
                f"🎯 **شانس بلاک**: {new_level * 10}%\n"
                f"🛡️ **کاهش دمیج**: {new_level * 5}%\n"
                f"💰 **هزینه**: {upgrade_cost:,} ZP\n"
                f"💎 **موجودی جدید**: {new_balance:,} ZP"
            )
        else:
            response = (
                f"❌ **موجودی ناکافی**\n\n"
                f"💰 **هزینه ارتقا**: {upgrade_cost:,} ZP\n"
                f"💎 **موجودی شما**: {user[4]:,} ZP"
            )
        
        await message.answer(response, reply_markup=defense_menu())
    except Exception as e:
        await message.answer("❌ خطا در ارتقای دفاع", reply_markup=defense_menu())

@dp.message(lambda message: message.text == "🏆 لیگ ها")
async def league_handler(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        
        # تعیین لیگ بر اساس سطح
        if user[2] >= 20:
            league = "افسانه‌ای"
            reward = 30000
        elif user[2] >= 15:
            league = "پلاتین" 
            reward = 15000
        elif user[2] >= 10:
            league = "طلا"
            reward = 7000
        elif user[2] >= 5:
            league = "نقره"
            reward = 3000
        else:
            league = "برنز"
            reward = 1000
        
        league_text = (
            f"🏆 **سیستم لیگ WarZone**\n\n"
            f"**لیگ فعلی**: {league}\n"
            f"**سطح شما**: {user[2]}\n"
            f"**پاداش هفتگی**: {reward:,} ZP\n\n"
            "گزینه مورد نظر را انتخاب کنید:"
        )
        
        await message.answer(league_text, reply_markup=league_menu())
    except Exception as e:
        await message.answer("❌ خطا در نمایش لیگ", reply_markup=main_menu())

@dp.message(lambda message: message.text == "💰 دریافت پاداش")
async def claim_league_reward(message: types.Message):
    try:
        user = db.get_user(message.from_user.id)
        
        # محاسبه پاداش بر اساس سطح
        if user[2] >= 20:
            reward = 30000
        elif user[2] >= 15:
            reward = 15000
        elif user[2] >= 10:
            reward = 7000
        elif user[2] >= 5:
            reward = 3000
        else:
            reward = 1000
        
        db.update_user_zp(message.from_user.id, reward)
        new_balance = db.get_user(message.from_user.id)[4]
        
        response = (
            f"🏆 **دریافت پاداش لیگ!**\n\n"
            f"💰 **مبلغ پاداش**: {reward:,} ZP\n"
            f"💎 **موجودی جدید**: {new_balance:,} ZP\n\n"
            f"⏰ **پاداش بعدی**: ۷ روز دیگر"
        )
        
        db.log_activity(message.from_user.id, "league_reward", f"{reward} ZP")
        await message.answer(response, reply_markup=league_menu())
    except Exception as e:
        await message.answer("❌ خطا در دریافت پاداش", reply_markup=league_menu())

# هندلرهای باقی مانده برای منوهای جدید
@dp.message(lambda message: message.text in ["📡 الکترونیکی", "🔒 اطلاعاتی", "📊 وضعیت تیم"])
async def sabotage_coming_soon(message: types.Message):
    await message.answer(
        "🛠 **این قابلیت به زودی فعال می‌شود**\n\n"
        "✅ در حال حاضر از خرابکاری نفوذی استفاده کنید",
        reply_markup=sabotage_menu()
    )

@dp.message(lambda message: message.text in ["📊 وضعیت دفاع", "📈 رتبه جهانی"])
async def defense_coming_soon(message: types.Message):
    await message.answer(
        "🛠 **این قابلیت به زودی فعال می‌شود**\n\n"
        "✅ در حال حاضر از ارتقای دفاع استفاده کنید",
        reply_markup=defense_menu()
            )
