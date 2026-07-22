import subprocess, base64

BASE = "/storage/emulated/0/AndroidCSProjects/collbomber/app/src/main"

def upload(path, content):
    b64 = base64.b64encode(content.encode()).decode()
    chunks = [b64[i:i+1500] for i in range(0, len(b64), 1500)]
    subprocess.run(['shizuku', 'sh', '-c', f"rm -f '{path}'"], capture_output=True, timeout=10)
    subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{chunks[0]}' > /sdcard/tmp/up.b64"], capture_output=True, timeout=30)
    for c in chunks[1:]:
        subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{c}' >> /sdcard/tmp/up.b64"], capture_output=True, timeout=15)
    subprocess.run(['shizuku', 'sh', '-c', f"base64 -d < /sdcard/tmp/up.b64 > '{path}' && rm /sdcard/tmp/up.b64"], capture_output=True, timeout=20)

# ===== RESTORE ORIGINAL COLORS =====
colors = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="bg_primary">#FF020204</color>
    <color name="bg_secondary">#FF0B0B12</color>
    <color name="bg_tertiary">#FF151520</color>
    <color name="bg_surface">#FF12121B</color>
    <color name="bg_elevated">#FF1C1C2B</color>
    <color name="bg_overlay">#B0000000</color>
    <color name="bg_gradient_start">#FF020204</color>
    <color name="bg_gradient_end">#FF0B0B12</color>
    <color name="accent_primary">#FF007AFF</color>
    <color name="accent_primary_dark">#FF005BBF</color>
    <color name="accent_primary_light">#FF4DA6FF</color>
    <color name="accent_purple">#FF5E5CE6</color>
    <color name="accent_cyan">#FF00D1FF</color>
    <color name="accent_mint">#FF34C759</color>
    <color name="call_accent">#FFFF6B00</color>
    <color name="call_accent_light">#FFFF9500</color>
    <color name="sms_accent">#FF007AFF</color>
    <color name="sms_accent_light">#FF4DA6FF</color>
    <color name="whatsapp_accent">#FF25D366</color>
    <color name="whatsapp_accent_light">#FF6EE7A0</color>
    <color name="mix_accent">#FF8B5CF6</color>
    <color name="mix_accent_light">#FFA78BFA</color>
    <color name="text_primary">#FFFFFFFF</color>
    <color name="text_secondary">#FFB0B0B8</color>
    <color name="text_tertiary">#FF8E8E93</color>
    <color name="text_quaternary">#FF636366</color>
    <color name="text_disabled">#FF3A3A3C</color>
    <color name="status_success">#FF34C759</color>
    <color name="status_error">#FFFF3B30</color>
    <color name="status_warning">#FFFFCC00</color>
    <color name="status_info">#FF007AFF</color>
    <color name="status_whatsapp">#FF25D366</color>
    <color name="status_active">#FF007AFF</color>
    <color name="status_idle">#FF48484A</color>
    <color name="glass_body">#20FFFFFF</color>
    <color name="glass_sheen">#15FFFFFF</color>
    <color name="glass_frost">#0AFFFFFF</color>
    <color name="glass_stroke">#30FFFFFF</color>
    <color name="glass_stroke_accent">#40007AFF</color>
    <color name="glass_shadow">#40000000</color>
    <color name="glass_dark">#1A000000</color>
    <color name="white">#FFFFFFFF</color>
    <color name="black">#FF000000</color>
</resources>'''
upload(f"{BASE}/res/values/colors.xml", colors)
print("✅ colors.xml restored")

# ===== RESTORE ORIGINAL NIGHT COLORS =====
night_colors = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="bg_primary">#FF000000</color>
    <color name="bg_secondary">#FF1C1C1E</color>
    <color name="bg_tertiary">#FF2C2C2E</color>
    <color name="bg_gradient_start">#FF000000</color>
    <color name="bg_gradient_end">#FF0A0A1A</color>
</resources>'''
upload(f"{BASE}/res/values-night/colors.xml", night_colors)
print("✅ night/colors.xml restored")

# ===== RESTORE ORIGINAL THEMES =====
themes = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="SplashTheme" parent="Theme.AppCompat.DayNight.NoActionBar">
        <item name="android:windowBackground">@color/bg_primary</item>
        <item name="android:statusBarColor">@android:color/transparent</item>
        <item name="android:navigationBarColor">@android:color/transparent</item>
        <item name="android:windowLightStatusBar">false</item>
        <item name="android:windowLightNavigationBar">false</item>
        <item name="android:windowTranslucentStatus">true</item>
        <item name="android:windowTranslucentNavigation">true</item>
    </style>
    <style name="AppTheme" parent="Theme.AppCompat.DayNight.NoActionBar">
        <item name="android:windowBackground">@color/bg_primary</item>
        <item name="android:statusBarColor">@android:color/transparent</item>
        <item name="android:navigationBarColor">@android:color/transparent</item>
        <item name="android:windowLightStatusBar">false</item>
        <item name="android:windowLightNavigationBar">false</item>
        <item name="android:windowTranslucentStatus">true</item>
        <item name="android:windowTranslucentNavigation">true</item>
    </style>
</resources>'''
upload(f"{BASE}/res/values/themes.xml", themes)
print("✅ themes.xml restored")

# ===== RESTORE ORIGINAL NIGHT THEMES =====
night_themes = '''<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Base.AppTheme" parent="Theme.AppCompat.DayNight.NoActionBar">
        <item name="android:windowBackground">@color/bg_primary</item>
        <item name="android:statusBarColor">@color/bg_primary</item>
        <item name="android:navigationBarColor">@color/bg_primary</item>
    </style>
    <style name="AppTheme" parent="Base.AppTheme" />
</resources>'''
upload(f"{BASE}/res/values-night/themes.xml", night_themes)
print("✅ night/themes.xml restored")

# ===== RESTORE ORIGINAL STRINGS =====
strings = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Tokyo 2.0</string>
    <string name="subtitle">AETHER COMMAND v3.0</string>
    <string name="update_required">Update Required</string>
    <string name="update_now">UPDATE NOW</string>
    <string name="exit_app">EXIT</string>
</resources>'''
upload(f"{BASE}/res/values/strings.xml", strings)
print("✅ strings.xml restored")

# ===== RESTORE ORIGINAL BG_GRADIENT =====
gradient = '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient
        android:startColor="#FF050508"
        android:endColor="#FF0F0F24"
        android:centerColor="#FF0A0A18"
        android:angle="270" />
</shape>'''
upload(f"{BASE}/res/drawable/bg_gradient.xml", gradient)
print("✅ bg_gradient.xml restored")

print("\n✅ All original resource files restored!")
