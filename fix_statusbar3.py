import subprocess, base64

BASE = "/storage/emulated/0/AndroidCSProjects/collbomber/app/src/main"
LAYOUT = f"{BASE}/res/layout"
DRAWABLE = f"{BASE}/res/drawable"
VALUES = f"{BASE}/res/values"
KOTLIN = f"{BASE}/kotlin/com/rolex/mybasic/collbomber"

def upload(path, content):
    b64 = base64.b64encode(content.encode()).decode()
    chunks = [b64[i:i+1500] for i in range(0, len(b64), 1500)]
    subprocess.run(['shizuku', 'sh', '-c', f"rm -f '{path}'"], capture_output=True, timeout=10)
    subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{chunks[0]}' > /sdcard/tmp/up.b64"], capture_output=True, timeout=30)
    for c in chunks[1:]:
        subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{c}' >> /sdcard/tmp/up.b64"], capture_output=True, timeout=15)
    subprocess.run(['shizuku', 'sh', '-c', f"base64 -d < /sdcard/tmp/up.b64 > '{path}' && rm /sdcard/tmp/up.b64"], capture_output=True, timeout=20)

# ===== FIX 1: Root FrameLayout — NO opaque background =====
# The root should NOT have a solid bg color — the image should extend behind status bar
r = subprocess.run(['shizuku', 'sh', '-c', f"cat '{LAYOUT}/activity_main.xml'"], capture_output=True, text=True, timeout=15)
xml = r.stderr if len(r.stderr or '') > 100 else r.stdout

# Remove opaque background from root FrameLayout
xml = xml.replace(
    'android:layout_height="match_parent"\n    android:background="@color/bg_primary"',
    'android:layout_height="match_parent"'
)
print("Fixed: removed opaque bg from root FrameLayout")
upload(f"{LAYOUT}/activity_main.xml", xml)

# ===== FIX 2: bg_gradient — very transparent, just subtle tint =====
gradient = '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient
        android:startColor="#10000000"
        android:centerColor="#18000000"
        android:endColor="#20000000"
        android:angle="270" />
</shape>'''

print("Fixed: bg_gradient.xml (10-20% opacity)")
upload(f"{DRAWABLE}/bg_gradient.xml", gradient)

# ===== FIX 3: themes.xml — transparent status bar + nav bar =====
r3 = subprocess.run(['shizuku', 'sh', '-c', f"cat '{VALUES}/themes.xml'"], capture_output=True, text=True, timeout=15)
themes = r3.stderr if len(r3.stderr or '') > 100 else r3.stdout

# Ensure transparent status bar in both themes
if 'android:statusBarColor' in themes:
    themes = themes.replace(
        '<item name="android:statusBarColor">@android:color/transparent</item>',
        '<item name="android:statusBarColor">@android:color/transparent</item>'
    )
else:
    # Add transparent status bar
    themes = themes.replace(
        '<item name="android:windowBackground">@color/bg_primary</item>',
        '<item name="android:windowBackground">@color/bg_primary</item>\n        <item name="android:statusBarColor">@android:color/transparent</item>'
    )

print("Fixed: themes.xml")
upload(f"{VALUES}/themes.xml", themes)

# ===== FIX 4: values-night/themes.xml =====
r4 = subprocess.run(['shizuku', 'sh', '-c', f"cat '{VALUES}/../values-night/themes.xml'"], capture_output=True, text=True, timeout=15)
night_themes = r4.stderr if len(r4.stderr or '') > 100 else r4.stdout
upload(f"{VALUES}/../values-night/themes.xml", night_themes)

# ===== VERIFY =====
v1 = subprocess.run(['shizuku', 'sh', '-c', f"wc -c '{LAYOUT}/activity_main.xml'"], capture_output=True, text=True, timeout=10)
v2 = subprocess.run(['shizuku', 'sh', '-c', f"wc -c '{DRAWABLE}/bg_gradient.xml'"], capture_output=True, text=True, timeout=10)
v3 = subprocess.run(['shizuku', 'sh', '-c', f"wc -c '{VALUES}/themes.xml'"], capture_output=True, text=True, timeout=10)
print(f"\nactivity_main.xml: {v1.stdout.strip() or v1.stderr.strip()}")
print(f"bg_gradient.xml: {v2.stdout.strip() or v2.stderr.strip()}")
print(f"themes.xml: {v3.stdout.strip() or v3.stderr.strip()}")

print("\n✅ All fixes applied!")
