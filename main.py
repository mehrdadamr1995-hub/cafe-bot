import os
import threading
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run, daemon=True).start()

import requests
import time
import json
import os

TOKEN = "553696568:294qJP8FjXCqNcjMUMHZDVZHtjwfhNIaF3U"
ADMIN_CHAT_ID = 1644251611
URL = f"https://tapi.bale.ai/bot{TOKEN}/"

DB_FILE = "database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_db()

PLANS = {
    "اسپرسو تک": {
        "۱۰ شات (۱ ماهه) - ۱,۱۳۰,۰۰۰ تومان": {"title": "اسپرسو تک", "shots": 10},
        "۲۰ شات (۱ ماهه) - ۲,۱۴۰,۰۰۰ تومان": {"title": "اسپرسو تک", "shots": 20}
    },
    "اسپرسو دوبل": {
        "۱۰ شات (۱ ماهه) - ۱,۳۳۰,۰۰۰ تومان": {"title": "اسپرسو دوبل", "shots": 10},
        "۲۰ شات (۱ ماهه) - ۲,۵۳۰,۰۰۰ تومان": {"title": "اسپرسو دوبل", "shots": 20}
    },
    "آمریکانو": {
        "۱۰ شات (۱ ماهه) - ۱,۳۳۰,۰۰۰ تومان": {"title": "آمریکانو", "shots": 10},
        "۲۰ شات (۱ ماهه) - ۲,۵۳۰,۰۰۰ تومان": {"title": "آمریکانو", "shots": 20}
    },
    "لاته کلاسیک": {
        "۱۰ شات (۱ ماهه) - ۲,۰۰۰,۰۰۰ تومان": {"title": "لاته کلاسیک", "shots": 10},
        "۲۰ شات (۱ ماهه) - ۳,۷۷۰,۰۰۰ تومان": {"title": "لاته کلاسیک", "shots": 20}
    }
}

user_steps = {}
user_data = {}

def send_message(chat_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "text": text}
    if keyboard:
        payload["reply_markup"] = {"keyboard": keyboard, "resize_keyboard": True}
    try:
        requests.post(URL + "sendMessage", json=payload, timeout=5)
    except:
        pass

def send_photo(chat_id, photo_id, caption):
    payload = {"chat_id": chat_id, "photo": photo_id, "caption": caption}
    try:
        requests.post(URL + "sendPhoto", json=payload, timeout=5)
    except:
        pass

def main_keyboard():
    return [
        [{"text": "ثبت‌نام در طرح اشتراک ماهانه‌ی قهوه"}],
        [{"text": "📊 گزارش اشتراک من"}]
    ]

# پاک‌سازی صف پیام‌های قدیمی موقع استارت
try:
    res = requests.get(URL + "getUpdates", params={"offset": -1}, timeout=5).json()
    if res.get("ok") and res.get("result"):
        offset = res["result"][-1]["update_id"] + 1
    else:
        offset = 0
except:
    offset = 0

print("ربات روشن شد و صف پیام‌ها بازنشانی گردید.")

while True:
    try:
        response = requests.get(URL + "getUpdates", params={"offset": offset, "timeout": 10})
        result = response.json()
        
        if result.get("ok") and result.get("result"):
            for update in result["result"]:
                # آپدیت آنی offset برای جلوگیری از تکرار پردازش یک پیام
                offset = update["update_id"] + 1

                if "message" in update:
                    msg = update["message"]
                    chat_id = str(msg["chat"]["id"])
                    user_text = msg.get("text", "")

                    # --- دستورات مدیر (بدون تکرار) ---
                    if int(chat_id) == ADMIN_CHAT_ID:
                        # ۱. پاک کردن دیتابیس
                        if user_text == "/reset":
                            db = {}
                            save_db(db)
                            send_message(ADMIN_CHAT_ID, "🗑 دیتابیس کاملاً پاک شد.")
                            continue

                        # ۲. شارژ اشتراک
                        elif user_text.startswith("/add"):
                            parts = user_text.split()
                            if len(parts) == 3:
                                target_id = str(parts[1]).strip()
                                shots = int(parts[2])
                                
                                # اگر کاربر نبود، پروفایل جدید بساز
                                if target_id not in db:
                                    db[target_id] = {"name": "کاربر", "drink": "اشتراک", "total_shots": 0, "rem_shots": 0}
                                
                                db[target_id]["total_shots"] = shots
                                db[target_id]["rem_shots"] = shots
                                save_db(db)
                                
                                send_message(ADMIN_CHAT_ID, f"✅ شارژ انجام شد!\nکاربر: {target_id}\nموجودی فعلی: {shots} شات")
                                send_message(target_id, f"🎉 اشتراک شما فعال شد!\nتعداد {shots} شات به حساب شما اضافه گردید.")
                                continue

                        # ۳. کسر شات
                        elif user_text.startswith("/use"):
                            parts = user_text.split()
                            if len(parts) >= 2:
                                target_id = str(parts[1]).strip()
                                count_to_use = int(parts[2]) if len(parts) == 3 else 1
                                
                                if target_id not in db:
                                    send_message(ADMIN_CHAT_ID, f"❌ کاربر {target_id} در دیتابیس نیست.")
                                    continue
                                
                                if db[target_id]["rem_shots"] < count_to_use:
                                    send_message(ADMIN_CHAT_ID, f"❌ موجودی کافی نیست. مانده: {db[target_id]['rem_shots']}")
                                    continue
                                
                                old_shots = db[target_id]["rem_shots"]
                                db[target_id]["rem_shots"] -= count_to_use
                                save_db(db)
                                rem = db[target_id]["rem_shots"]
                                
                                send_message(ADMIN_CHAT_ID, f"☕️ {count_to_use} شات کم شد.\nمانده جدید: {rem} شات")
                                send_message(target_id, f"☕️ نوش جان! {count_to_use} شات استفاده شد.\n🔋 مانده اشتراک: {rem} شات")
                                continue

                    # --- منو و جریان کاربر ---
                    if user_text in ["/start", "سلام"]:
                        user_steps[chat_id] = "START"
                        send_message(chat_id, "به ربات ثبت‌نام و مدیریت اشتراک خوش آمدید! ☕️", main_keyboard())

                    elif user_text == "📊 گزارش اشتراک من":
                        if chat_id in db and db[chat_id]["rem_shots"] > 0:
                            info = db[chat_id]
                            used = info["total_shots"] - info["rem_shots"]
                            report = (
                                f"📋 **گزارش آنلاین اشتراک شما**\n\n"
                                f"👤 نام: {info['name']}\n"
                                f"☕️ نوع نوشیدنی: {info['drink']}\n"
                                f"🔢 کل شات خریده‌شده: {info['total_shots']}\n"
                                f"✅ استفاده‌شده: {used}\n"
                                f"🔋 **باقیمانده: {info['rem_shots']} شات**"
                            )
                            send_message(chat_id, report, main_keyboard())
                        else:
                            send_message(chat_id, "شما در حال حاضر اشتراک فعال ندارید.", main_keyboard())

                    elif user_text == "ثبت‌نام در طرح اشتراک ماهانه‌ی قهوه":
                        user_steps[chat_id] = "AWAITING_NAME"
                        send_message(chat_id, "لطفاً نام و نام خانوادگی خودت رو وارد کن:")

                    elif user_steps.get(chat_id) == "AWAITING_NAME":
                        user_data[chat_id] = {"name": user_text}
                        user_steps[chat_id] = "AWAITING_PHONE"
                        send_message(chat_id, f"ممنون {user_text} عزیز! 📝\nحالا شماره تماس خودت رو بفرست:")

                    elif user_steps.get(chat_id) == "AWAITING_PHONE":
                        user_data[chat_id]["phone"] = user_text
                        user_steps[chat_id] = "AWAITING_DRINK"
                        drink_btn = [
                            [{"text": "اسپرسو تک"}, {"text": "اسپرسو دوبل"}],
                            [{"text": "آمریکانو"}, {"text": "لاته کلاسیک"}]
                        ]
                        send_message(chat_id, "لطفاً نوع نوشیدنی مورد نظرت رو انتخاب کن:", drink_btn)

                    elif user_steps.get(chat_id) == "AWAITING_DRINK" and user_text in PLANS:
                        user_data[chat_id]["drink"] = user_text
                        user_steps[chat_id] = "AWAITING_SHOTS"
                        shots_btn = [[{"text": opt}] for opt in PLANS[user_text].keys()]
                        send_message(chat_id, f"طرح‌های موجود برای {user_text}:\nلطفاً تعداد شات مدنظرت رو انتخاب کن:", shots_btn)

                    elif user_steps.get(chat_id) == "AWAITING_SHOTS":
                        selected_drink = user_data[chat_id]["drink"]
                        if user_text in PLANS[selected_drink]:
                            plan_info = PLANS[selected_drink][user_text]
                            user_data[chat_id]["plan_title"] = user_text
                            user_data[chat_id]["shots"] = plan_info["shots"]
                            user_steps[chat_id] = "AWAITING_RECEIPT"
                            
                            card_info = (
                                f"☕️ طرح انتخابی شما: {user_text}\n\n"
                                "💳 لطفاً مبلغ مربوطه رو به شماره کارت زیر واریز کن و عکس رسیدش رو همینجا بفرست:\n\n"
                                "۶۱۰۴-۳۳۱۱-۴۴۲۸-۵۶۹۰\nبه نام: مهرداد امیری"
                            )
                            send_message(chat_id, card_info)

                    elif user_steps.get(chat_id) == "AWAITING_RECEIPT" and "photo" in msg:
                        photo_file_id = msg["photo"][-1]["file_id"]
                        name = user_data[chat_id]["name"]
                        phone = user_data[chat_id]["phone"]
                        drink = user_data[chat_id]["drink"]
                        shots = user_data[chat_id]["shots"]

                        send_message(chat_id, "رسیدت دریافت شد! 🎉\nپس از بررسی و تأیید، اشتراکت فعال میشه.", main_keyboard())

                        admin_caption = (
                            f"🔔 ثبت‌نام و رسید جدید!\n\n"
                            f"👤 نام: {name}\n"
                            f"📞 شماره: {phone}\n"
                            f"☕️ نوشیدنی: {drink} ({shots} شات)\n"
                            f"🆔 شناسه کاربر: {chat_id}\n\n"
                            f"👉 جهت فعال‌سازی دستور زیر را ارسال کنید:\n`/add {chat_id} {shots}`"
                        )
                        send_photo(ADMIN_CHAT_ID, photo_file_id, admin_caption)
                        
                        db[chat_id] = {"name": name, "phone": phone, "drink": drink, "total_shots": 0, "rem_shots": 0}
                        save_db(db)
                        user_steps[chat_id] = "COMPLETED"

    except Exception as e:
        time.sleep(2)
    
    time.sleep(1)
