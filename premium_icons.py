import subprocess, base64, time

BASE = "/storage/emulated/0/AndroidCSProjects/collbomber/app/src/main/res"
DRAWABLE = f"{BASE}/drawable"
VALUES = f"{BASE}/values"

def upload(path, content):
    b64 = base64.b64encode(content.encode()).decode()
    chunks = [b64[i:i+1500] for i in range(0, len(b64), 1500)]
    subprocess.run(['shizuku', 'sh', '-c', f"rm -f '{path}'"], capture_output=True, timeout=10)
    subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{chunks[0]}' > /sdcard/tmp/up.b64"], capture_output=True, timeout=30)
    for c in chunks[1:]:
        subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{c}' >> /sdcard/tmp/up.b64"], capture_output=True, timeout=15)
    subprocess.run(['shizuku', 'sh', '-c', f"base64 -d < /sdcard/tmp/up.b64 > '{path}' && rm /sdcard/tmp/up.b64"], capture_output=True, timeout=20)

# ===== PREMIUM ICONS =====

# Crown icon (for premium badge)
crown = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFD740"
        android:pathData="M12,2L9.19,8.63L2,9.24L7.46,13.97L5.82,21L12,17.27L18.18,21L16.54,13.97L22,9.24L14.81,8.63L12,2Z" />
</vector>'''

# Atom/Sparkle icon (for MIX MODE)
atom = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="32dp"
    android:height="32dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#B24BF3"
        android:pathData="M12,2C6.48,2 2,6.48 2,12s4.48,10 10,10 10,-4.48 10,-10S17.52,2 12,2zM13,17h-2v-6h2v6zM13,9h-2V7h2v2z"/>
    <path
        android:fillColor="#B24BF3"
        android:pathData="M12,7c-1.1,0-2,0.9-2,2v2h4V9c0,-1.1-0.9,-2-2,-2z"/>
    <path
        android:fillColor="#D4A5FF"
        android:pathData="M12,3C7.03,3 3,7.03 3,12s4.03,9 9,9 9,-4.03 9,-9S16.97,3 12,3z" android:strokeColor="#D4A5FF" android:strokeWidth="0.5" android:fillAlpha="0"/>
    <path
        android:fillColor="#E8D4FF"
        android:pathData="M12,1l-2.5,5.5L4,7.5l4,4-1,5.5L12,15l5,2-1-5.5 4-4-5.5-1L12,1z"/>
</vector>'''

# Shield icon (for Activity Log)
shield = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="20dp"
    android:height="20dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#00D1FF"
        android:pathData="M12,1L3,5v6c0,5.55 3.84,10.74 9,12 5.16,-1.26 9,-6.45 9,-12V5L12,1z" android:fillAlpha="0.3"/>
    <path
        android:fillColor="#00D1FF"
        android:pathData="M12,1L3,5v6c0,5.55 3.84,10.74 9,12 5.16,-1.26 9,-6.45 9,-12V5L12,1z" android:strokeColor="#00D1FF" android:strokeWidth="1.5" android:fillAlpha="0"/>
    <path
        android:fillColor="#00D1FF"
        android:pathData="M10,17l-4,-4 1.41,-1.41L10,14.17l6.59,-6.59L18,9l-8,8z"/>
</vector>'''

# Phone icon (for CALL)
phone = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp"
    android:height="22dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FF9F0A"
        android:pathData="M6.62,10.79c1.44,2.83 3.76,5.14 6.59,6.59l2.2,-2.2c0.27,-0.27 0.67,-0.36 1.02,-0.24 1.12,0.37 2.33,0.57 3.57,0.57 0.55,0 1,0.45 1,1V20c0,0.55 -0.45,1 -1,1 -9.39,0 -17,-7.61 -17,-17 0,-0.55 0.45,-1 1,-1h3.5c0.55,0 1,0.45 1,1 0,1.25 0.2,2.45 0.57,3.57 0.11,0.35 0.03,0.74 -0.25,1.02l-2.2,2.2z"/>
</vector>'''

# SMS icon
sms = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp"
    android:height="22dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#007AFF"
        android:pathData="M20,2H4C2.9,2 2.01,2.9 2.01,4L2,22l4,-4h14c1.1,0 2,-0.9 2,-2V4c0,-1.1 -0.9,-2 -2,-2zM18,14H6v-2h12v2zM18,11H6V9h12v2zM18,8H6V6h12v2z"/>
</vector>'''

# WhatsApp icon
wa = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp"
    android:height="22dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#25D366"
        android:pathData="M17.472,14.382c-0.297,-0.149 -1.758,-0.867 -2.03,-0.967 -0.273,-0.099 -0.471,-0.148 -0.668,0.15 -0.197,0.297 -0.767,0.966 -0.94,1.164 -0.173,0.199 -0.347,0.223 -0.644,0.075 -0.297,-0.15 -1.255,-0.463 -2.39,-1.475 -0.883,-0.788 -1.48,-1.761 -1.653,-2.059 -0.173,-0.297 -0.018,-0.458 0.13,-0.606 0.134,-0.133 0.298,-0.347 0.446,-0.52 0.149,-0.174 0.198,-0.298 0.298,-0.497 0.099,-0.198 0.05,-0.371 -0.025,-0.52 -0.075,-0.149 -0.668,-1.612 -0.916,-2.207 -0.242,-0.579 -0.487,-0.5 -0.668,-0.51 -0.173,-0.008 -0.371,-0.01 -0.568,-0.01 -0.198,0 -0.52,0.074 -0.792,0.372 -0.272,0.297 -1.04,1.016 -1.04,2.479 0,1.462 1.065,2.875 1.213,3.074 0.149,0.198 2.096,3.2 5.077,4.487 0.709,0.306 1.262,0.489 1.694,0.625 0.712,0.227 1.36,0.195 1.871,0.118 0.571,-0.085 1.758,-0.719 2.006,-1.413 0.248,-0.694 0.248,-1.29 0.173,-1.414 -0.074,-0.124 -0.272,-0.198 -0.57,-0.347z"/>
    <path
        android:fillColor="#25D366"
        android:pathData="M12,2C6.48,2 2,6.48 2,12c0,1.82 0.49,3.53 1.34,5L2,22l5.11,-1.34C8.58,21.52 10.25,22 12,22c5.52,0 10,-4.48 10,-10S17.52,2 12,2zM12,20c-1.55,0 -2.99,-0.37 -4.23,-1.02l-0.3,-0.18 -3.1,0.81 0.82,-3.03 -0.2,-0.31C4.25,14.34 3.75,12.73 3.75,12 3.75,7.45 7.45,3.75 12,3.75S20.25,7.45 20.25,12 16.55,20.25 12,20.25z"/>
</vector>'''

# Info icon
info = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp"
    android:height="22dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FF9F0A"
        android:pathData="M12,2C6.48,2 2,6.48 2,12s4.48,10 10,10 10,-4.48 10,-10S17.52,2 12,2zM13,17h-2v-6h2v6zM13,9h-2V7h2v2z"/>
</vector>'''

# ===== PREMIUM DRAWABLES =====

# Purple glow card border
glow_card = '''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:bottom="3dp">
        <shape android:shape="rectangle">
            <solid android:color="#40B24BF3" />
            <corners android:radius="24dp" />
        </shape>
    </item>
    <item>
        <shape android:shape="rectangle">
            <gradient android:startColor="#18FFFFFF" android:endColor="#08FFFFFF" android:angle="135" />
            <corners android:radius="24dp" />
        </shape>
    </item>
    <item>
        <shape android:shape="rectangle">
            <stroke android:width="1dp" android:color="#30B24BF3" />
            <corners android:radius="24dp" />
        </shape>
    </item>
</layer-list>'''

# Premium badge
badge = '''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape android:shape="rectangle">
            <gradient android:startColor="#FF5E5CE6" android:endColor="#FF3B39B0" android:angle="0" />
            <corners android:radius="12dp" />
        </shape>
    </item>
    <item>
        <shape android:shape="rectangle">
            <stroke android:width="0.5dp" android:color="#60FFFFFF" />
            <corners android:radius="12dp" />
        </shape>
    </item>
</layer-list>'''

# Quick access button - dark glass
quick_btn = '''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:bottom="2dp">
        <shape android:shape="rectangle">
            <solid android:color="#2AB24BF3" />
            <corners android:radius="16dp" />
        </shape>
    </item>
    <item>
        <shape android:shape="rectangle">
            <gradient android:startColor="#20FFFFFF" android:endColor="#08FFFFFF" android:angle="135" />
            <corners android:radius="16dp" />
        </shape>
    </item>
    <item>
        <shape android:shape="rectangle">
            <stroke android:width="0.5dp" android:color="#20B24BF3" />
            <corners android:radius="16dp" />
        </shape>
    </item>
</layer-list>'''

# Purple glow ring (for Quick Access center)
glow_ring = '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <stroke android:width="2dp" android:color="#B24BF3" />
    <solid android:color="#08B24BF3" />
</shape>'''

# START button - purple gradient
btn_start = '''<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#33B24BF3">
    <item>
        <layer-list>
            <item android:bottom="3dp">
                <shape android:shape="rectangle">
                    <solid android:color="#2AB24BF3" />
                    <corners android:radius="28dp" />
                </shape>
            </item>
            <item>
                <shape android:shape="rectangle">
                    <gradient android:startColor="#FFB24BF3" android:endColor="#FF5E5CE6" android:angle="0" />
                    <corners android:radius="28dp" />
                </shape>
            </item>
            <item>
                <shape android:shape="rectangle">
                    <gradient android:startColor="#40FFFFFF" android:endColor="#00FFFFFF" android:angle="135" />
                    <corners android:radius="28dp" />
                </shape>
            </item>
        </layer-list>
    </item>
</ripple>'''

# ===== UPLOAD ALL =====
files = {
    f"{DRAWABLE}/ic_crown.xml": crown,
    f"{DRAWABLE}/ic_atom.xml": atom,
    f"{DRAWABLE}/ic_shield.xml": shield,
    f"{DRAWABLE}/ic_phone.xml": phone,
    f"{DRAWABLE}/ic_sms2.xml": sms,
    f"{DRAWABLE}/ic_wa2.xml": wa,
    f"{DRAWABLE}/ic_info.xml": info,
    f"{DRAWABLE}/glow_card.xml": glow_card,
    f"{DRAWABLE}/badge_premium.xml": badge,
    f"{DRAWABLE}/quick_access_btn.xml": quick_btn,
    f"{DRAWABLE}/glow_ring.xml": glow_ring,
    f"{DRAWABLE}/btn_start_all.xml": btn_start,
}

for path, content in files.items():
    upload(path, content)
    print(f"✅ {path.split('/')[-1]}")

print(f"\n{len(files)} premium drawables uploaded!")
