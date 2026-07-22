import subprocess, base64

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

# 1. bg_gradient — purple tint
gradient = '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient
        android:startColor="#300A0520"
        android:centerColor="#200A0A18"
        android:endColor="#18050515"
        android:angle="270" />
</shape>'''
upload(f"{DRAWABLE}/bg_gradient.xml", gradient)
print("✅ bg_gradient (purple tint)")

# 2. Updated colors.xml with purple accent
colors = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Background -->
    <color name="bg_primary">#FF0A0A0B</color>
    <color name="bg_secondary">#FF121212</color>
    <color name="bg_tertiary">#FF1C1C1E</color>

    <!-- Glass -->
    <color name="glass_fill">#15FFFFFF</color>
    <color name="glass_stroke">#1AFFFFFF</color>
    <color name="glass_sheen">#0AFFFFFF</color>
    <color name="glass_shadow">#40000000</color>
    <color name="glass_dark">#1A000000</color>

    <!-- Purple Accent System -->
    <color name="accent_purple">#FFB24BF3</color>
    <color name="accent_purple_light">#FFD4A5FF</color>
    <color name="accent_purple_dark">#FF7C3AED</color>
    <color name="accent_blue">#FF007AFF</color>
    <color name="accent_cyan">#FF00D1FF</color>

    <!-- Category Colors -->
    <color name="call_accent">#FFFF9F0A</color>
    <color name="sms_accent">#FF007AFF</color>
    <color name="whatsapp_accent">#FF25D366</color>
    <color name="mix_accent">#FFB24BF3</color>

    <!-- Text -->
    <color name="text_primary">#FFFFFFFF</color>
    <color name="text_secondary">#FFEBEBF0</color>
    <color name="text_tertiary">#FFA0A0AC</color>
    <color name="text_quaternary">#FF70707A</color>
    <color name="text_disabled">#FF404046</color>

    <!-- Status -->
    <color name="status_success">#FF30D158</color>
    <color name="status_error">#FFFF453A</color>
    <color name="status_warning">#FFFFD60A</color>

    <!-- Pure -->
    <color name="white">#FFFFFFFF</color>
    <color name="black">#FF000000</color>
    <color name="transparent">#00000000</color>
</resources>'''
upload(f"{VALUES}/colors.xml", colors)
print("✅ colors.xml (purple system)")

# 3. Update avatar_ring with purple glow
avatar_ring = '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <stroke android:width="2.5dp" android:color="#B24BF3" />
    <solid android:color="#00000000" />
    <size android:width="96dp" android:height="96dp" />
</shape>'''
upload(f"{DRAWABLE}/avatar_ring.xml", avatar_ring)
print("✅ avatar_ring (purple glow)")

# 4. themes.xml — transparent bars
themes = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="SplashTheme" parent="Theme.AppCompat.DayNight.NoActionBar">
        <item name="android:windowBackground">@color/bg_primary</item>
        <item name="android:statusBarColor">@android:color/transparent</item>
        <item name="android:navigationBarColor">@android:color/transparent</item>
        <item name="android:windowLightStatusBar">false</item>
    </style>
    <style name="AppTheme" parent="Theme.AppCompat.DayNight.NoActionBar">
        <item name="android:windowBackground">@color/bg_primary</item>
        <item name="android:statusBarColor">@android:color/transparent</item>
        <item name="android:navigationBarColor">@android:color/transparent</item>
        <item name="android:windowLightStatusBar">false</item>
        <item name="android:windowAnimationStyle">@style/GlassTransition</item>
    </style>
    <style name="GlassTransition" parent="@android:style/Animation.Activity">
        <item name="android:activityOpenEnterAnimation">@anim/fade_in</item>
        <item name="android:activityOpenExitAnimation">@anim/fade_out</item>
        <item name="android:activityCloseEnterAnimation">@anim/fade_in</item>
        <item name="android:activityCloseExitAnimation">@anim/fade_out</item>
    </style>
</resources>'''
upload(f"{VALUES}/themes.xml", themes)
print("✅ themes.xml")

print("\n✅ Theme + Colors updated to match reference!")
