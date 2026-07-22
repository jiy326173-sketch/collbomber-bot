import subprocess, base64

BASE = "/storage/emulated/0/AndroidCSProjects/collbomber/app/src/main"
LAYOUT = f"{BASE}/res/layout"
KOTLIN = f"{BASE}/kotlin/com/rolex/mybasic/collbomber"

def upload(path, content):
    b64 = base64.b64encode(content.encode()).decode()
    chunks = [b64[i:i+1500] for i in range(0, len(b64), 1500)]
    subprocess.run(['shizuku', 'sh', '-c', f"rm -f '{path}'"], capture_output=True, timeout=10)
    subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{chunks[0]}' > /sdcard/tmp/up.b64"], capture_output=True, timeout=30)
    for c in chunks[1:]:
        subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{c}' >> /sdcard/tmp/up.b64"], capture_output=True, timeout=15)
    subprocess.run(['shizuku', 'sh', '-c', f"base64 -d < /sdcard/tmp/up.b64 > '{path}' && rm /sdcard/tmp/up.b64"], capture_output=True, timeout=20)

# Write correct layout directly (no fitsSystemWindows on root)
kt_layout = '''<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/bg_primary">

    <ImageView android:id="@+id/bgAnimation"
        android:layout_width="match_parent" android:layout_height="match_parent"
        android:src="@drawable/bg_home" android:scaleType="centerCrop" android:alpha="0.8" />

    <View android:layout_width="match_parent" android:layout_height="match_parent"
        android:background="@drawable/bg_gradient" />

    <ImageView android:id="@+id/lightSweep"
        android:layout_width="2400dp" android:layout_height="2dp"
        android:src="@drawable/light_sweep_bg" android:scaleType="matrix"
        android:translationX="-1200dp" android:alpha="0.5" android:translationY="120dp" />

    <ScrollView android:layout_width="match_parent" android:layout_height="match_parent"
        android:scrollbars="none" android:overScrollMode="never"
        android:layout_marginBottom="80dp" android:clipToPadding="false">

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:orientation="vertical" android:paddingTop="40dp"
            android:paddingStart="16dp" android:paddingEnd="16dp" android:paddingBottom="24dp">

            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                android:orientation="vertical" android:gravity="center" android:layout_marginBottom="28dp">
                <FrameLayout android:layout_width="80dp" android:layout_height="80dp"
                    android:layout_gravity="center" android:layout_marginBottom="12dp">
                    <ImageView android:id="@+id/ivLogo" android:layout_width="72dp" android:layout_height="72dp"
                        android:layout_gravity="center" android:src="@drawable/ic_logo_round"
                        android:scaleType="centerCrop" android:outlineProvider="bounds" android:clipToOutline="true" />
                    <View android:id="@+id/avatarRingGlow" android:layout_width="80dp" android:layout_height="80dp"
                        android:layout_gravity="center" android:background="@drawable/avatar_ring" />
                    <View android:layout_width="10dp" android:layout_height="10dp"
                        android:layout_gravity="bottom|end" android:layout_marginBottom="2dp"
                        android:layout_marginEnd="2dp" android:background="@drawable/di_pulse_dot_active" android:elevation="4dp" />
                </FrameLayout>
                <TextView android:id="@+id/tvAppTitle" android:layout_width="wrap_content" android:layout_height="wrap_content"
                    android:text="@string/app_name" android:textColor="@color/text_primary"
                    android:textSize="32sp" android:fontFamily="sans-serif-thin" android:letterSpacing="0.4" android:alpha="0.95" />
                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                    android:text="@string/subtitle" android:textColor="@color/text_tertiary"
                    android:textSize="9sp" android:textStyle="bold" android:letterSpacing="0.6" android:layout_marginTop="4dp" />
                <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center"
                    android:background="@drawable/badge_prefix" android:paddingHorizontal="14dp"
                    android:paddingVertical="4dp" android:layout_marginTop="10dp">
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="MULTI MOD" android:textColor="@color/accent_blue_light"
                        android:textSize="8sp" android:textStyle="bold" android:letterSpacing="0.5" />
                </LinearLayout>
            </LinearLayout>

            <LinearLayout android:id="@+id/mixSection" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="vertical"
                android:background="@drawable/liquid_glass_card" android:padding="24dp"
                android:layout_marginBottom="16dp" android:elevation="8dp">
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center_vertical" android:layout_marginBottom="20dp">
                    <ImageView android:id="@+id/iconMixMode" android:layout_width="32dp" android:layout_height="32dp"
                        android:src="@drawable/ic_sparkle" android:scaleType="centerInside" android:tint="@color/mix_accent" />
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1"
                        android:orientation="vertical" android:layout_marginStart="12dp">
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="MIX MODE" android:textColor="@color/text_primary"
                            android:textSize="18sp" android:textStyle="bold" android:letterSpacing="0.3" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="Simultaneous assault on all channels"
                            android:textColor="@color/text_quaternary" android:textSize="11sp" android:layout_marginTop="2dp" />
                    </LinearLayout>
                </LinearLayout>
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center_vertical"
                    android:background="@drawable/bg_input" android:paddingHorizontal="16dp" android:paddingVertical="4dp"
                    android:layout_marginBottom="16dp">
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="+91" android:textColor="@color/text_tertiary" android:textSize="14sp" android:layout_marginEnd="8dp" />
                    <EditText android:id="@+id/etMixPhone" android:layout_width="0dp" android:layout_height="48dp"
                        android:layout_weight="1" android:background="@null" android:hint="Phone number"
                        android:inputType="phone" android:maxLines="1" android:textColor="@color/text_primary"
                        android:textColorHint="@color/text_disabled" android:textSize="16sp" />
                </LinearLayout>
                <LinearLayout android:id="@+id/mixStatsContainer" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:orientation="horizontal" android:gravity="center"
                    android:layout_marginBottom="16dp">
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1"
                        android:orientation="vertical" android:gravity="center" android:background="@drawable/stat_tile" android:paddingVertical="10dp">
                        <TextView android:id="@+id/tvMixTotal" android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="0" android:textColor="@color/text_primary" android:textSize="20sp" android:textStyle="bold" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="TOTAL" android:textColor="@color/text_quaternary" android:textSize="8sp" android:letterSpacing="0.3" />
                    </LinearLayout>
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1"
                        android:orientation="vertical" android:gravity="center" android:background="@drawable/stat_tile"
                        android:paddingVertical="10dp" android:layout_marginHorizontal="6dp">
                        <TextView android:id="@+id/tvMixSuccess" android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="0" android:textColor="@color/status_success" android:textSize="20sp" android:textStyle="bold" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="OK" android:textColor="@color/status_success" android:textSize="8sp" android:letterSpacing="0.3" />
                    </LinearLayout>
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1"
                        android:orientation="vertical" android:gravity="center" android:background="@drawable/stat_tile" android:paddingVertical="10dp">
                        <TextView android:id="@+id/tvMixFailed" android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="0" android:textColor="@color/status_error" android:textSize="20sp" android:textStyle="bold" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="FAIL" android:textColor="@color/status_error" android:textSize="8sp" android:letterSpacing="0.3" />
                    </LinearLayout>
                </LinearLayout>
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center" android:layout_marginTop="4dp">
                    <Button android:id="@+id/btnMixStart" android:layout_width="0dp" android:layout_height="56dp"
                        android:layout_weight="1" android:background="@drawable/btn_premium_start"
                        android:text="START ALL" android:textColor="@color/white" android:textSize="14sp"
                        android:textStyle="bold" android:letterSpacing="0.2" android:stateListAnimator="@null" android:elevation="6dp" />
                    <Button android:id="@+id/btnMixStop" android:layout_width="0dp" android:layout_height="56dp"
                        android:layout_weight="1" android:background="@drawable/btn_premium_stop"
                        android:text="STOP ALL" android:textColor="@color/white" android:textSize="14sp"
                        android:textStyle="bold" android:letterSpacing="0.2" android:stateListAnimator="@null"
                        android:elevation="6dp" android:visibility="gone" />
                </LinearLayout>
            </LinearLayout>

            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                android:orientation="horizontal" android:gravity="center" android:layout_marginBottom="16dp">
                <LinearLayout android:id="@+id/tabCallBtn" android:layout_width="0dp" android:layout_height="wrap_content"
                    android:layout_weight="1" android:orientation="vertical" android:gravity="center"
                    android:background="@drawable/liquid_glass_small" android:paddingVertical="14dp" android:layout_marginEnd="6dp"
                    android:clickable="true" android:focusable="true">
                    <ImageView android:layout_width="24dp" android:layout_height="24dp" android:src="@drawable/ic_calls"
                        android:scaleType="centerInside" android:tint="@color/call_accent" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="CALL"
                        android:textColor="@color/text_secondary" android:textSize="10sp" android:textStyle="bold"
                        android:letterSpacing="0.2" android:layout_marginTop="6dp" />
                </LinearLayout>
                <LinearLayout android:id="@+id/tabSmsBtn" android:layout_width="0dp" android:layout_height="wrap_content"
                    android:layout_weight="1" android:orientation="vertical" android:gravity="center"
                    android:background="@drawable/liquid_glass_small" android:paddingVertical="14dp" android:layout_marginHorizontal="6dp"
                    android:clickable="true" android:focusable="true">
                    <ImageView android:layout_width="24dp" android:layout_height="24dp" android:src="@drawable/ic_sms"
                        android:scaleType="centerInside" android:tint="@color/sms_accent" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="SMS"
                        android:textColor="@color/text_secondary" android:textSize="10sp" android:textStyle="bold"
                        android:letterSpacing="0.2" android:layout_marginTop="6dp" />
                </LinearLayout>
                <LinearLayout android:id="@+id/tabWaBtn" android:layout_width="0dp" android:layout_height="wrap_content"
                    android:layout_weight="1" android:orientation="vertical" android:gravity="center"
                    android:background="@drawable/liquid_glass_small" android:paddingVertical="14dp" android:layout_marginHorizontal="6dp"
                    android:clickable="true" android:focusable="true">
                    <ImageView android:layout_width="24dp" android:layout_height="24dp" android:src="@drawable/ic_whatsapp"
                        android:scaleType="centerInside" android:tint="@color/whatsapp_accent" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="WA"
                        android:textColor="@color/text_secondary" android:textSize="10sp" android:textStyle="bold"
                        android:letterSpacing="0.2" android:layout_marginTop="6dp" />
                </LinearLayout>
                <LinearLayout android:id="@+id/tabMixBtn" android:layout_width="0dp" android:layout_height="wrap_content"
                    android:layout_weight="1" android:orientation="vertical" android:gravity="center"
                    android:background="@drawable/liquid_glass_small" android:paddingVertical="14dp" android:layout_marginStart="6dp"
                    android:clickable="true" android:focusable="true">
                    <ImageView android:layout_width="24dp" android:layout_height="24dp" android:src="@drawable/ic_sparkle"
                        android:scaleType="centerInside" android:tint="@color/mix_accent" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="MIX"
                        android:textColor="@color/text_secondary" android:textSize="10sp" android:textStyle="bold"
                        android:letterSpacing="0.2" android:layout_marginTop="6dp" />
                </LinearLayout>
            </LinearLayout>

            <LinearLayout android:id="@+id/callSection" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="vertical"
                android:background="@drawable/liquid_glass_card" android:padding="20dp"
                android:layout_marginBottom="12dp" android:visibility="gone" android:elevation="4dp">
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center_vertical" android:layout_marginBottom="14dp">
                    <ImageView android:layout_width="20dp" android:layout_height="20dp" android:src="@drawable/ic_calls"
                        android:scaleType="centerInside" android:tint="@color/call_accent" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="CALL BOMBER"
                        android:textColor="@color/text_primary" android:textSize="15sp" android:textStyle="bold"
                        android:layout_marginStart="10dp" android:letterSpacing="0.1" />
                </LinearLayout>
                <EditText android:id="@+id/etCallPhone" android:layout_width="match_parent" android:layout_height="42dp"
                    android:background="@drawable/bg_input" android:hint="Phone number" android:inputType="phone"
                    android:textColor="@color/text_primary" android:textColorHint="@color/text_disabled"
                    android:textSize="14sp" android:paddingHorizontal="14dp" android:layout_marginBottom="12dp" />
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center">
                    <LinearLayout android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content"
                        android:orientation="vertical" android:gravity="center" android:background="@drawable/stat_tile" android:paddingVertical="8dp">
                        <TextView android:id="@+id/tvCallStats" android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="Total: 0  OK: 0  FAIL: 0" android:textColor="@color/text_tertiary" android:textSize="9sp" />
                    </LinearLayout>
                    <Button android:id="@+id/btnCallStart" android:layout_width="wrap_content" android:layout_height="38dp"
                        android:background="@drawable/btn_primary" android:text="START" android:textColor="@color/white"
                        android:textSize="11sp" android:textStyle="bold" android:stateListAnimator="@null"
                        android:paddingHorizontal="20dp" android:layout_marginStart="8dp" />
                    <Button android:id="@+id/btnCallStop" android:layout_width="wrap_content" android:layout_height="38dp"
                        android:background="@drawable/btn_premium_stop" android:text="STOP" android:textColor="@color/white"
                        android:textSize="11sp" android:textStyle="bold" android:stateListAnimator="@null"
                        android:paddingHorizontal="20dp" android:layout_marginStart="8dp" android:visibility="gone" />
                </LinearLayout>
            </LinearLayout>

            <LinearLayout android:id="@+id/smsSection" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="vertical"
                android:background="@drawable/liquid_glass_card" android:padding="20dp"
                android:layout_marginBottom="12dp" android:visibility="gone" android:elevation="4dp">
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center_vertical" android:layout_marginBottom="14dp">
                    <ImageView android:layout_width="20dp" android:layout_height="20dp" android:src="@drawable/ic_sms"
                        android:scaleType="centerInside" android:tint="@color/sms_accent" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="SMS BOMBER"
                        android:textColor="@color/text_primary" android:textSize="15sp" android:textStyle="bold"
                        android:layout_marginStart="10dp" android:letterSpacing="0.1" />
                </LinearLayout>
                <EditText android:id="@+id/etSmsPhone" android:layout_width="match_parent" android:layout_height="42dp"
                    android:background="@drawable/bg_input" android:hint="Phone number" android:inputType="phone"
                    android:textColor="@color/text_primary" android:textColorHint="@color/text_disabled"
                    android:textSize="14sp" android:paddingHorizontal="14dp" android:layout_marginBottom="12dp" />
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center">
                    <LinearLayout android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content"
                        android:orientation="vertical" android:gravity="center" android:background="@drawable/stat_tile" android:paddingVertical="8dp">
                        <TextView android:id="@+id/tvSmsStats" android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="Total: 0  OK: 0  FAIL: 0" android:textColor="@color/text_tertiary" android:textSize="9sp" />
                    </LinearLayout>
                    <Button android:id="@+id/btnSmsStart" android:layout_width="wrap_content" android:layout_height="38dp"
                        android:background="@drawable/btn_primary" android:text="START" android:textColor="@color/white"
                        android:textSize="11sp" android:textStyle="bold" android:stateListAnimator="@null"
                        android:paddingHorizontal="20dp" android:layout_marginStart="8dp" />
                    <Button android:id="@+id/btnSmsStop" android:layout_width="wrap_content" android:layout_height="38dp"
                        android:background="@drawable/btn_premium_stop" android:text="STOP" android:textColor="@color/white"
                        android:textSize="11sp" android:textStyle="bold" android:stateListAnimator="@null"
                        android:paddingHorizontal="20dp" android:layout_marginStart="8dp" android:visibility="gone" />
                </LinearLayout>
            </LinearLayout>

            <LinearLayout android:id="@+id/whatsappSection" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="vertical"
                android:background="@drawable/liquid_glass_card" android:padding="20dp"
                android:layout_marginBottom="12dp" android:visibility="gone" android:elevation="4dp">
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center_vertical" android:layout_marginBottom="14dp">
                    <ImageView android:layout_width="20dp" android:layout_height="20dp" android:src="@drawable/ic_whatsapp"
                        android:scaleType="centerInside" android:tint="@color/whatsapp_accent" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="WA BOMBER"
                        android:textColor="@color/text_primary" android:textSize="15sp" android:textStyle="bold"
                        android:layout_marginStart="10dp" android:letterSpacing="0.1" />
                </LinearLayout>
                <EditText android:id="@+id/etWaPhone" android:layout_width="match_parent" android:layout_height="42dp"
                    android:background="@drawable/bg_input" android:hint="Phone number" android:inputType="phone"
                    android:textColor="@color/text_primary" android:textColorHint="@color/text_disabled"
                    android:textSize="14sp" android:paddingHorizontal="14dp" android:layout_marginBottom="12dp" />
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center">
                    <LinearLayout android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content"
                        android:orientation="vertical" android:gravity="center" android:background="@drawable/stat_tile" android:paddingVertical="8dp">
                        <TextView android:id="@+id/tvWaStats" android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="Total: 0  OK: 0  FAIL: 0" android:textColor="@color/text_tertiary" android:textSize="9sp" />
                    </LinearLayout>
                    <Button android:id="@+id/btnWaStart" android:layout_width="wrap_content" android:layout_height="38dp"
                        android:background="@drawable/btn_primary" android:text="START" android:textColor="@color/white"
                        android:textSize="11sp" android:textStyle="bold" android:stateListAnimator="@null"
                        android:paddingHorizontal="20dp" android:layout_marginStart="8dp" />
                    <Button android:id="@+id/btnWaStop" android:layout_width="wrap_content" android:layout_height="38dp"
                        android:background="@drawable/btn_premium_stop" android:text="STOP" android:textColor="@color/white"
                        android:textSize="11sp" android:textStyle="bold" android:stateListAnimator="@null"
                        android:paddingHorizontal="20dp" android:layout_marginStart="8dp" android:visibility="gone" />
                </LinearLayout>
            </LinearLayout>

            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                android:orientation="vertical" android:background="@drawable/liquid_glass_card"
                android:padding="16dp" android:elevation="4dp">
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center_vertical" android:layout_marginBottom="10dp">
                    <TextView android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1"
                        android:text="ACTIVITY LOG" android:textColor="@color/text_tertiary"
                        android:textSize="10sp" android:textStyle="bold" android:letterSpacing="0.4" />
                    <TextView android:id="@+id/tvLiveIndicator" android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="LIVE" android:textColor="@color/status_success"
                        android:textSize="8sp" android:textStyle="bold" android:letterSpacing="0.2" />
                </LinearLayout>
                <ScrollView android:id="@+id/logScroll" android:layout_width="match_parent"
                    android:layout_height="140dp" android:scrollbars="none">
                    <TextView android:id="@+id/tvLog" android:layout_width="match_parent" android:layout_height="wrap_content"
                        android:text="Ready..." android:textColor="@color/text_quaternary"
                        android:textSize="10sp" android:fontFamily="monospace" android:lineSpacingExtra="4dp" />
                </ScrollView>
            </LinearLayout>
            <View android:layout_width="match_parent" android:layout_height="24dp" />
        </LinearLayout>
    </ScrollView>

    <LinearLayout android:id="@+id/bottomNav" android:layout_width="match_parent" android:layout_height="72dp"
        android:layout_gravity="bottom" android:orientation="horizontal" android:gravity="center"
        android:background="#CC121212" android:elevation="24dp" android:paddingBottom="8dp">
        <LinearLayout android:id="@+id/tabMix" android:layout_width="0dp" android:layout_height="match_parent"
            android:layout_weight="1" android:orientation="vertical" android:gravity="center"
            android:clickable="true" android:focusable="true" android:background="?attr/selectableItemBackgroundBorderless">
            <View android:id="@+id/indicatorMix" android:layout_width="28dp" android:layout_height="2.5dp"
                android:background="@drawable/indicator_mix" android:visibility="visible" />
            <ImageView android:id="@+id/iconMix" android:layout_width="22dp" android:layout_height="22dp"
                android:src="@drawable/ic_sparkle" android:scaleType="centerInside" android:layout_marginTop="4dp" android:tint="@color/mix_accent" />
            <TextView android:id="@+id/labelMix" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="MIX" android:textColor="@color/mix_accent" android:textSize="9sp" android:textStyle="bold" android:letterSpacing="0.1" android:layout_marginTop="2dp" />
        </LinearLayout>
        <LinearLayout android:id="@+id/tabCall" android:layout_width="0dp" android:layout_height="match_parent"
            android:layout_weight="1" android:orientation="vertical" android:gravity="center"
            android:clickable="true" android:focusable="true" android:background="?attr/selectableItemBackgroundBorderless">
            <View android:id="@+id/indicatorCall" android:layout_width="28dp" android:layout_height="2.5dp"
                android:background="@drawable/indicator_call" android:visibility="gone" />
            <ImageView android:id="@+id/iconCall" android:layout_width="22dp" android:layout_height="22dp"
                android:src="@drawable/ic_calls" android:scaleType="centerInside" android:layout_marginTop="4dp" android:tint="#555555" />
            <TextView android:id="@+id/labelCall" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="CALL" android:textColor="#666666" android:textSize="9sp" android:textStyle="bold" android:letterSpacing="0.1" android:layout_marginTop="2dp" />
        </LinearLayout>
        <LinearLayout android:id="@+id/tabSms" android:layout_width="0dp" android:layout_height="match_parent"
            android:layout_weight="1" android:orientation="vertical" android:gravity="center"
            android:clickable="true" android:focusable="true" android:background="?attr/selectableItemBackgroundBorderless">
            <View android:id="@+id/indicatorSms" android:layout_width="28dp" android:layout_height="2.5dp"
                android:background="@drawable/indicator_sms" android:visibility="gone" />
            <ImageView android:id="@+id/iconSms" android:layout_width="22dp" android:layout_height="22dp"
                android:src="@drawable/ic_sms" android:scaleType="centerInside" android:layout_marginTop="4dp" android:tint="#555555" />
            <TextView android:id="@+id/labelSms" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="SMS" android:textColor="#666666" android:textSize="9sp" android:textStyle="bold" android:letterSpacing="0.1" android:layout_marginTop="2dp" />
        </LinearLayout>
        <LinearLayout android:id="@+id/tabWa" android:layout_width="0dp" android:layout_height="match_parent"
            android:layout_weight="1" android:orientation="vertical" android:gravity="center"
            android:clickable="true" android:focusable="true" android:background="?attr/selectableItemBackgroundBorderless">
            <View android:id="@+id/indicatorWa" android:layout_width="28dp" android:layout_height="2.5dp"
                android:background="@drawable/indicator_wa" android:visibility="gone" />
            <ImageView android:id="@+id/iconWa" android:layout_width="22dp" android:layout_height="22dp"
                android:src="@drawable/ic_whatsapp" android:scaleType="centerInside" android:layout_marginTop="4dp" android:tint="#555555" />
            <TextView android:id="@+id/labelWa" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="WA" android:textColor="#666666" android:textSize="9sp" android:textStyle="bold" android:letterSpacing="0.1" android:layout_marginTop="2dp" />
        </LinearLayout>
    </LinearLayout>
</FrameLayout>'''

print("Uploading clean layout (no fitsSystemWindows)...")
upload(f"{LAYOUT}/activity_main.xml", kt_layout)

v = subprocess.run(['shizuku', 'sh', '-c', f"wc -c '{LAYOUT}/activity_main.xml'"], capture_output=True, text=True, timeout=10)
print(f"activity_main.xml: {v.stdout.strip() or v.stderr.strip()}")

r = subprocess.run(['shizuku', 'sh', '-c', f"cat '{LAYOUT}/activity_main.xml' | head -5"], capture_output=True, text=True, timeout=10)
print(f"First lines: {(r.stdout or r.stderr).strip()[:150]}")
