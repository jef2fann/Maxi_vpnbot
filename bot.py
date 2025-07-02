from telebot import TeleBot, types
import json
import os
import datetime
import time

API_TOKEN = 'YOUR_TOKEN_HERE'
CHANNEL_USERNAME = 'YourChannelUsername'
ADMIN_ID = 123456789

bot = TeleBot(API_TOKEN)
user_states = {}
admin_waiting_config_for = None
config_data_file = "configs.json"

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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if not is_user_subscribed(chat_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("عضو شدم ✅", callback_data="joined"))
        bot.send_message(chat_id, f"❌ برای استفاده از ربات باید عضو کانال زیر باشید:
"
                                  f"https://t.me/{CHANNEL_USERNAME}", reply_markup=markup)
        return
    bot.send_message(chat_id, "سلام به ربات خوش اومدی 🌸")
    show_main_menu(chat_id)

def check_expiring_configs():
    now = datetime.datetime.now()
    for uid, data in config_users.items():
        try:
            start = datetime.datetime.fromisoformat(data["date"])
            days = (now - start).days
            if days == 29:
                bot.send_message(int(uid), "⏰ یک روز تا پایان کانفیگ باقی مانده است.")
        except Exception as e:
            print(f"[!] Error checking expiry for {uid}: {e}")

print("🤖 Bot is running...")

while True:
    try:
        check_expiring_configs()
        bot.infinity_polling(timeout=30, long_polling_timeout=5)
    except Exception as e:
        print(f"[!] Error: {e}")
        time.sleep(5)
