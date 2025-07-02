from telebot import TeleBot, types
import json
import os
import datetime
import time

# تنظیمات
API_TOKEN = 'YOUR_BOT_TOKEN_HERE'
CHANNEL_USERNAME = 'Maxi_Vpn'
ADMIN_ID = 627417733

bot = TeleBot(API_TOKEN)
user_states = {}
admin_waiting_config_for = None
config_data_file = "configs.json"

# بارگذاری کانفیگ‌ها
if os.path.exists(config_data_file):
    with open(config_data_file, "r") as f:
        config_users = json.load(f)
else:
    config_users = {}

def save_configs():
    with open(config_data_file, "w") as f:
        json.dump(config_users, f)

def is_user_subscribed(chat_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", chat_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🛒 خرید کانفیگ جدید")
    markup.row("ℹ️ اطلاعات کانفیگ‌ها", "📚 آموزش اتصال")
    markup.row("💬 پشتیبانی")
    bot.send_message(chat_id, "منوی اصلی 👇", reply_markup=markup)

# منوی ادمین
def show_admin_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("👥 لیست کاربران", "📊 آمار فروش")
    markup.row("🧾 لیست کانفیگ‌ها", "❌ انصراف")
    bot.send_message(chat_id, "پنل مدیریت ادمین 👇", reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if not is_user_subscribed(chat_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("عضو شدم ✅", callback_data="joined"))
        bot.send_message(chat_id, f"""❌ برای استفاده از ربات باید عضو کانال زیر باشید:
https://t.me/{CHANNEL_USERNAME}""", reply_markup=markup)
        return
    bot.send_message(chat_id, "سلام به ربات Maxi_VPN خوش اومدی 🌸")
    show_main_menu(chat_id)

@bot.message_handler(commands=['admin'])
def admin_panel(msg):
    if msg.from_user.id == ADMIN_ID:
        show_admin_menu(msg.chat.id)
    else:
        bot.send_message(msg.chat.id, "⛔ شما ادمین نیستید.")

@bot.message_handler(func=lambda msg: msg.text == "👥 لیست کاربران")
def list_users(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    users = list(config_users.keys())
    text = "👥 کاربران ثبت‌شده:\n" + "\n".join(users) if users else "هیچ کاربری ثبت نشده."
    bot.send_message(msg.chat.id, text)

@bot.message_handler(func=lambda msg: msg.text == "📊 آمار فروش")
def stats(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    total = len(config_users)
    bot.send_message(msg.chat.id, f"📊 تعداد کل فروش‌ها: {total}")

@bot.message_handler(func=lambda msg: msg.text == "🧾 لیست کانفیگ‌ها")
def all_configs(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    if not config_users:
        bot.send_message(msg.chat.id, "❌ کانفیگی ثبت نشده.")
        return
    text = ""
    for uid, data in config_users.items():
        text += f"👤 {uid}\n📄 {data['config']}\n📅 {data['date']}\n\n"
    bot.send_message(msg.chat.id, text[:4096])

@bot.message_handler(func=lambda msg: msg.text == "💬 پشتیبانی")
def support(msg):
    bot.send_message(msg.chat.id, "برای پشتیبانی پیام دهید:\n@jef2fan")

@bot.message_handler(func=lambda msg: msg.text == "🛒 خرید کانفیگ جدید")
def buy(msg):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🪙 25 گیگ - 120 تومان", "💎 50 گیگ - 170 تومان")
    markup.add("🚀 100 گیگ - 250 تومان", "🔥 200 گیگ - 350 تومان")
    markup.add("❌ انصراف")
    bot.send_message(msg.chat.id, "یک پلن را انتخاب کن:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text.startswith(("🪙", "💎", "🚀", "🔥")))
def select_plan(m):
    plan = m.text
    user_states[m.chat.id] = plan
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💳 کارت به کارت", "❌ انصراف")
    bot.send_message(m.chat.id, f"🧾 پیش‌فاکتور:\n{plan}\n\nلطفا نوع پرداخت را انتخاب کن.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💳 کارت به کارت")
def payment_method(m):
    user_states[m.chat.id] = "waiting_receipt"
    bot.send_message(m.chat.id, "💳 لطفا تصویر رسید واریز را ارسال کن.\n\nکارت: 6104337954942122 - به نام قاسم زاده")

@bot.message_handler(content_types=["photo"])
def handle_receipt(msg):
    uid = msg.chat.id
    if user_states.get(uid) == "waiting_receipt":
        plan = user_states.get(uid, "نامشخص")
        caption = f"🧾 رسید از کاربر {uid}:\nپلن: {plan}"

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ تایید", callback_data=f"confirm_{uid}"),
            types.InlineKeyboardButton("📤 ارسال کانفیگ", callback_data=f"send_{uid}")
        )

        bot.send_photo(ADMIN_ID, msg.photo[-1].file_id, caption=caption, reply_markup=markup)
        bot.send_message(uid, "✅ رسید ثبت شد. منتظر تایید ادمین باشید.")
        user_states[uid] = "pending_admin"

@bot.callback_query_handler(func=lambda c: c.data.startswith("confirm_"))
def confirm_payment(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "⛔ فقط ادمین می‌تونه تایید کنه", show_alert=True)
        return
    uid = int(c.data.split("_")[1])
    bot.send_message(uid, "✅ پرداخت تایید شد. لطفا منتظر دریافت کانفیگ باشید.")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📤 ارسال کانفیگ", callback_data=f"send_{uid}"))
    bot.send_message(ADMIN_ID, f"کاربر {uid} تایید شد. لطفا کانفیگ را بفرستید.", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("send_"))
def ask_config(c):
    global admin_waiting_config_for
    if c.from_user.id != ADMIN_ID:
        return
    admin_waiting_config_for = int(c.data.split("_")[1])
    bot.send_message(ADMIN_ID, f"لطفاً کانفیگ کاربر {admin_waiting_config_for} را ارسال کن:")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and admin_waiting_config_for is not None)
def receive_config(m):
    global admin_waiting_config_for
    uid = admin_waiting_config_for
    config = m.text

    bot.send_message(uid, f"✅ کانفیگ شما آماده است:\n\n{config}\n\n⏳ مدت: 30 روز")
    bot.send_message(ADMIN_ID, f"کانفیگ به کاربر {uid} ارسال شد.")
    config_users[str(uid)] = {
        "config": config,
        "date": datetime.datetime.now().isoformat()
    }
    save_configs()
    admin_waiting_config_for = None

@bot.message_handler(func=lambda m: m.text == "ℹ️ اطلاعات کانفیگ‌ها")
def info(m):
    uid = str(m.chat.id)
    if uid in config_users:
        data = config_users[uid]
        start = datetime.datetime.fromisoformat(data["date"])
        now = datetime.datetime.now()
        days_left = 30 - (now - start).days
        msg = (f"📄 کانفیگ شما:\n{data['config']}\n\n⏳ زمان باقی‌مانده: {max(0, days_left)} روز")
    else:
        msg = "❌ شما هنوز کانفیگی خریداری نکرده‌اید."
    bot.send_message(m.chat.id, msg)

@bot.message_handler(func=lambda m: m.text == "📚 آموزش اتصال")
def tutorial(m):
    bot.send_message(m.chat.id, "📲 اپ NapsternetV یا v2rayNG را نصب کن و کانفیگ را وارد کن.\n✅ سپس روی اتصال بزن.")

@bot.message_handler(func=lambda m: m.text == "❌ انصراف")
def cancel(m):
    if m.from_user.id == ADMIN_ID:
        show_admin_menu(m.chat.id)
    else:
        show_main_menu(m.chat.id)

def check_expiring_configs():
    now = datetime.datetime.now()
    for uid, data in config_users.items():
        try:
            start = datetime.datetime.fromisoformat(data["date"])
            days = (now - start).days
            if days == 29:
                bot.send_message(int(uid), "⏰ یک روز تا پایان کانفیگ باقی مانده است. لطفاً برای تمدید مجدد، از طریق ربات خرید انجام دهید.")
        except Exception as e:
            print(f"[!] Error checking expiry for {uid}: {e}")

print("🤖 Maxi_VPN Bot is running...")

while True:
    try:
        check_expiring_configs()
        bot.infinity_polling(timeout=30, long_polling_timeout=5)
    except Exception as e:
        print(f"[!] Error: {e}")
        time.sleep(5)
