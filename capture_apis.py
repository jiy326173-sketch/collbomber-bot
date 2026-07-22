#!/usr/bin/env python3
"""
MitmProxy capture script — saves ALL API requests/responses
Target app ke saare API calls capture karta hai
"""
import mitmproxy.http
import json
import os
import time
from datetime import datetime

CAPTURE_FILE = "/root/workspace/captured_apis.json"
captured = []

def request(flow: mitmproxy.http.HTTPFlow):
    """Capture every request"""
    url = flow.request.pretty_url
    method = flow.request.method
    host = flow.request.host
    
    # Skip common CDN/static/analytics
    skip_domains = ["google-analytics", "googletagmanager", "doubleclick", 
                     "facebook.com/tr", "cdn.", ".js", ".css", ".png", ".jpg", 
                     ".gif", ".svg", ".woff", ".ico", "analytics"]
    if any(s in url for s in skip_domains):
        return
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "name": host.split(".")[-2] if len(host.split(".")) > 2 else host,
        "url": url,
        "method": method,
        "headers": dict(flow.request.headers),
        "body": flow.request.text if flow.request.text else "",
    }
    
    # Check if it has phone/OTP keywords  
    body_lower = flow.request.text.lower() if flow.request.text else ""
    is_otp_api = any(w in url.lower() or w in body_lower for w in 
                     ["otp", "phone", "mobile", "voice", "call", "verify", 
                      "register", "signup", "login", "auth", "send"])
    
    if is_otp_api:
        entry["type"] = "🔴 OTP/REGISTRATION API"
    else:
        entry["type"] = "API"
    
    captured.append(entry)
    
    # Save to file
    with open(CAPTURE_FILE, "w") as f:
        json.dump(captured, f, indent=2)
    
    # Print immediately
    print(f"\n{'='*60}", flush=True)
    print(f"[{entry['type']}] {method} {url}", flush=True)
    print(f"  Headers: {dict(flow.request.headers)}", flush=True)
    print(f"  Body: {flow.request.text}", flush=True)
    print(f"{'='*60}", flush=True)


def response(flow: mitmproxy.http.HTTPFlow):
    """Capture responses for OTP APIs"""
    url = flow.request.pretty_url
    body_lower = flow.request.text.lower() if flow.request.text else ""
    
    if any(w in url.lower() or w in body_lower for w in 
           ["otp", "phone", "mobile", "voice", "call", "verify", "send", "auth"]):
        print(f"  🔵 Response {flow.response.status_code}: {flow.response.text[:300]}", flush=True)
