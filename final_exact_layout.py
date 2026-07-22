import subprocess, base64

LAYOUT = "/storage/emulated/0/AndroidCSProjects/collbomber/app/src/main/res/layout"

def upload(path, content):
    b64 = base64.b64encode(content.encode()).decode()
    chunks = [b64[i:i+1500] for i in range(0, len(b64), 1500)]
    subprocess.run(['shizuku', 'sh', '-c', f"rm -f '{path}'"], capture_output=True, timeout=10)
    subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{chunks[0]}' > /sdcard/tmp/up.b64"], capture_output=True, timeout=30)
    for c in chunks[1:]:
        subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{c}' >> /sdcard/tmp/up.b64"], capture_output=True, timeout=15)
    subprocess.run(['shizuku', 'sh', '-c', f"base64 -d < /sdcard/tmp/up.b64 > '{path}' && rm /sdcard/tmp/up.b64"], capture_output=True, timeout=20)

layout = '''<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- BACKGROUND -->
    <ImageView android:id="@+id/bgAnimation"
        android:layout_width="match_parent" android:layout_height="match_parent"
        android:src="@drawable/bg_home" android:scaleType="centerCrop" android:alpha="0.85" />
    <View android:layout_width="match_parent" android:layout_height="match_parent"
        android:background="@drawable/bg_gradient" />

    <!-- SCROLLABLE -->
    <ScrollView android:layout_width="match_parent" android:layout_height="match_parent"
        android:scrollbars="none" android:overScrollMode="never"
        android:layout_marginBottom="80dp" android:clipToPadding="false">

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:orientation="vertical" android:paddingTop="36dp"
            android:paddingStart="18dp" android:paddingEnd="18dp" android:paddingBottom="20dp">

            <!-- PREMIUM BADGE -->
            <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_gravity="end" android:orientation="horizontal"
                android:background="@drawable/badge_premium" android:paddingHorizontal="14dp"
                android:paddingVertical="8dp" android:layout_marginBottom="12dp">
                <ImageView android:layout_width="16dp" android:layout_height="16dp"
                    android:src="@drawable/ic_crown" android:layout_marginEnd="8dp" />
                <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content"
                    android:orientation="vertical">
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="PREMIUM" android:textColor="@color/white"
                        android:textSize="12sp" android:textStyle="bold" android:letterSpacing="0.2" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="Unlimited Access" android:textColor="#B0FFFFFF"
                        android:textSize="8sp" />
                </LinearLayout>
            </LinearLayout>

            <!-- HEADER -->
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                android:orientation="vertical" android:gravity="center" android:layout_marginBottom="20dp">
                <FrameLayout android:layout_width="100dp" android:layout_height="100dp"
                    android:layout_gravity="center" android:layout_marginBottom="16dp">
                    <ImageView android:id="@+id/ivLogo" android:layout_width="88dp"
                        android:layout_height="88dp" android:layout_gravity="center"
                        android:src="@drawable/ic_logo_round" android:scaleType="centerCrop"
                        android:outlineProvider="bounds" android:clipToOutline="true" />
                    <View android:id="@+id/avatarRingGlow" android:layout_width="100dp"
                        android:layout_height="100dp" android:layout_gravity="center"
                        android:background="@drawable/avatar_ring" />
                    <View android:layout_width="14dp" android:layout_height="14dp"
                        android:layout_gravity="bottom|end" android:layout_marginBottom="4dp"
                        android:layout_marginEnd="4dp" android:background="@drawable/di_pulse_dot_active"
                        android:elevation="4dp" />
                </FrameLayout>
                <TextView android:id="@+id/tvAppTitle" android:layout_width="wrap_content"
                    android:layout_height="wrap_content" android:text="TOKYO 2.0"
                    android:textColor="@color/accent_purple" android:textSize="36sp"
                    android:fontFamily="sans-serif-medium" android:letterSpacing="0.25"
                    android:textStyle="bold" />
                <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content"
                    android:gravity="center" android:layout_marginTop="6dp">
                    <View android:layout_width="24dp" android:layout_height="1dp"
                        android:background="@color/text_quaternary" android:layout_marginEnd="10dp" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="AETHER COMMAND V3.0" android:textColor="@color/text_secondary"
                        android:textSize="10sp" android:letterSpacing="0.4" android:textStyle="bold" />
                    <View android:layout_width="24dp" android:layout_height="1dp"
                        android:background="@color/text_quaternary" android:layout_marginStart="10dp" />
                </LinearLayout>
                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                    android:text="●  MULTI-MOD  ●" android:textColor="@color/accent_purple_light"
                    android:textSize="10sp" android:textStyle="bold" android:letterSpacing="0.3"
                    android:layout_marginTop="8dp" />
            </LinearLayout>

            <!-- MIX MODE CARD -->
            <LinearLayout android:id="@+id/mixSection" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="vertical"
                android:background="@drawable/glow_card" android:padding="24dp"
                android:layout_marginBottom="20dp" android:elevation="10dp">
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:gravity="center_vertical" android:layout_marginBottom="18dp">
                    <ImageView android:layout_width="30dp" android:layout_height="30dp"
                        android:src="@drawable/ic_atom" android:scaleType="centerInside" />
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:orientation="vertical" android:layout_marginStart="12dp">
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="MIX MODE" android:textColor="@color/white"
                            android:textSize="20sp" android:textStyle="bold" android:letterSpacing="0.2" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="Intelligence assist on any number"
                            android:textColor="@color/text_tertiary" android:textSize="11sp"
                            android:layout_marginTop="2dp" />
                    </LinearLayout>
                </LinearLayout>
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:background="@drawable/bg_input" android:paddingHorizontal="16dp"
                    android:gravity="center_vertical" android:layout_marginBottom="18dp">
                    <ImageView android:layout_width="20dp" android:layout_height="20dp"
                        android:src="@drawable/ic_phone" android:scaleType="centerInside"
                        android:tint="#6A5CFF" android:layout_marginEnd="12dp" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="+91" android:textColor="@color/text_secondary"
                        android:textSize="14sp" android:layout_marginEnd="8dp" />
                    <EditText android:id="@+id/etMixPhone" android:layout_width="0dp"
                        android:layout_height="48dp" android:layout_weight="1" android:background="@null"
                        android:hint="Enter target number" android:inputType="phone" android:maxLines="1"
                        android:textColor="@color/white" android:textColorHint="@color/text_disabled"
                        android:textSize="15sp" />
                </LinearLayout>
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginBottom="18dp">
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:orientation="vertical" android:gravity="center"
                        android:background="@drawable/stat_tile" android:paddingVertical="12dp">
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="⊞" android:textColor="@color/accent_purple" android:textSize="16sp"
                            android:layout_marginBottom="4dp" />
                        <TextView android:id="@+id/tvMixTotal" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:text="0"
                            android:textColor="@color/white" android:textSize="20sp" android:textStyle="bold" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="TOTAL" android:textColor="@color/accent_purple"
                            android:textSize="9sp" android:textStyle="bold" android:letterSpacing="0.2" />
                    </LinearLayout>
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:orientation="vertical" android:gravity="center"
                        android:background="@drawable/stat_tile" android:paddingVertical="12dp"
                        android:layout_marginHorizontal="8dp">
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="✓" android:textColor="@color/status_success" android:textSize="16sp"
                            android:layout_marginBottom="4dp" />
                        <TextView android:id="@+id/tvMixSuccess" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:text="0"
                            android:textColor="@color/white" android:textSize="20sp" android:textStyle="bold" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="OK" android:textColor="@color/status_success"
                            android:textSize="9sp" android:textStyle="bold" android:letterSpacing="0.2" />
                    </LinearLayout>
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:orientation="vertical" android:gravity="center"
                        android:background="@drawable/stat_tile" android:paddingVertical="12dp">
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="✕" android:textColor="@color/status_error" android:textSize="16sp"
                            android:layout_marginBottom="4dp" />
                        <TextView android:id="@+id/tvMixFailed" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:text="0"
                            android:textColor="@color/white" android:textSize="20sp" android:textStyle="bold" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="FAIL" android:textColor="@color/status_error"
                            android:textSize="9sp" android:textStyle="bold" android:letterSpacing="0.2" />
                    </LinearLayout>
                </LinearLayout>
                <Button android:id="@+id/btnMixStart" android:layout_width="match_parent"
                    android:layout_height="58dp" android:background="@drawable/btn_start_all"
                    android:text="⚡  START ALL" android:textColor="@color/white" android:textSize="16sp"
                    android:textStyle="bold" android:letterSpacing="0.3" android:stateListAnimator="@null"
                    android:elevation="8dp" />
                <Button android:id="@+id/btnMixStop" android:layout_width="match_parent"
                    android:layout_height="58dp" android:background="@drawable/btn_premium_stop"
                    android:text="STOP ALL" android:textColor="@color/white" android:textSize="14sp"
                    android:textStyle="bold" android:stateListAnimator="@null" android:visibility="gone" />
            </LinearLayout>

            <!-- QUICK ACCESS (Reference Layout) -->
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                android:orientation="vertical" android:background="@drawable/glow_card"
                android:padding="20dp" android:layout_marginBottom="20dp" android:elevation="6dp">

                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                    android:text="QUICK ACCESS" android:textColor="@color/white"
                    android:textSize="14sp" android:textStyle="bold" android:letterSpacing="0.3"
                    android:layout_gravity="center" android:layout_marginBottom="20dp" />

                <FrameLayout android:layout_width="match_parent" android:layout_height="200dp"
                    android:clipChildren="false">

                    <!-- Center Ring -->
                    <FrameLayout android:layout_width="100dp" android:layout_height="100dp"
                        android:layout_gravity="center" android:background="@drawable/center_ring"
                        android:elevation="4dp">
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="QUICK&#10;ACCESS" android:textColor="@color/accent_purple_light"
                            android:textSize="11sp" android:textStyle="bold" android:letterSpacing="0.2"
                            android:gravity="center" android:layout_gravity="center" />
                    </FrameLayout>

                    <!-- Top Left: CALL -->
                    <LinearLayout android:layout_width="80dp" android:layout_height="80dp"
                        android:layout_gravity="top|start" android:layout_marginStart="12dp"
                        android:layout_marginTop="10dp" android:orientation="vertical"
                        android:gravity="center" android:background="@drawable/qa_card"
                        android:clickable="true" android:focusable="true"
                        android:id="@+id/tabCallBtn" android:elevation="2dp">
                        <ImageView android:layout_width="22dp" android:layout_height="22dp"
                            android:src="@drawable/ic_phone" android:scaleType="centerInside" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="CALL" android:textColor="@color/white"
                            android:textSize="9sp" android:textStyle="bold" android:letterSpacing="0.1"
                            android:layout_marginTop="6dp" />
                    </LinearLayout>

                    <!-- Top Right: SMS -->
                    <LinearLayout android:layout_width="80dp" android:layout_height="80dp"
                        android:layout_gravity="top|end" android:layout_marginEnd="12dp"
                        android:layout_marginTop="10dp" android:orientation="vertical"
                        android:gravity="center" android:background="@drawable/qa_card"
                        android:clickable="true" android:focusable="true"
                        android:id="@+id/tabSmsBtn" android:elevation="2dp">
                        <ImageView android:layout_width="22dp" android:layout_height="22dp"
                            android:src="@drawable/ic_sms2" android:scaleType="centerInside" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="SMS" android:textColor="@color/white"
                            android:textSize="9sp" android:textStyle="bold" android:letterSpacing="0.1"
                            android:layout_marginTop="6dp" />
                    </LinearLayout>

                    <!-- Bottom Left: WHATSAPP -->
                    <LinearLayout android:layout_width="80dp" android:layout_height="80dp"
                        android:layout_gravity="bottom|start" android:layout_marginStart="12dp"
                        android:layout_marginBottom="10dp" android:orientation="vertical"
                        android:gravity="center" android:background="@drawable/qa_card"
                        android:clickable="true" android:focusable="true"
                        android:id="@+id/tabWaBtn" android:elevation="2dp">
                        <ImageView android:layout_width="22dp" android:layout_height="22dp"
                            android:src="@drawable/ic_wa2" android:scaleType="centerInside" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="WA" android:textColor="@color/white"
                            android:textSize="9sp" android:textStyle="bold" android:letterSpacing="0.1"
                            android:layout_marginTop="6dp" />
                    </LinearLayout>

                    <!-- Bottom Right: INFO -->
                    <LinearLayout android:layout_width="80dp" android:layout_height="80dp"
                        android:layout_gravity="bottom|end" android:layout_marginEnd="12dp"
                        android:layout_marginBottom="10dp" android:orientation="vertical"
                        android:gravity="center" android:background="@drawable/qa_card"
                        android:clickable="true" android:focusable="true"
                        android:id="@+id/tabMixBtn" android:elevation="2dp">
                        <ImageView android:layout_width="22dp" android:layout_height="22dp"
                            android:src="@drawable/ic_info" android:scaleType="centerInside" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="INFO" android:textColor="@color/white"
                            android:textSize="9sp" android:textStyle="bold" android:letterSpacing="0.1"
                            android:layout_marginTop="6dp" />
                    </LinearLayout>
                </FrameLayout>
            </LinearLayout>

            <!-- ACTIVITY LOG -->
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                android:background="@drawable/glow_card" android:padding="18dp"
                android:gravity="center_vertical" android:elevation="4dp">
                <ImageView android:layout_width="24dp" android:layout_height="24dp"
                    android:src="@drawable/ic_shield" android:layout_marginEnd="12dp" />
                <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                    android:layout_weight="1" android:orientation="vertical">
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="ACTIVITY LOG" android:textColor="@color/white"
                        android:textSize="13sp" android:textStyle="bold" android:letterSpacing="0.2" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="System Ready to work..." android:textColor="@color/text_quaternary"
                        android:textSize="10sp" android:layout_marginTop="2dp" />
                </LinearLayout>
                <TextView android:id="@+id/tvLiveIndicator" android:layout_width="wrap_content"
                    android:layout_height="wrap_content" android:text="● LIVE"
                    android:textColor="@color/status_success" android:textSize="11sp"
                    android:textStyle="bold" />
            </LinearLayout>

            <!-- Hidden Sections -->
            <LinearLayout android:id="@+id/callSection" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="vertical"
                android:background="@drawable/glow_card" android:padding="18dp"
                android:layout_marginBottom="12dp" android:visibility="gone" android:elevation="4dp">
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:gravity="center_vertical" android:layout_marginBottom="12dp">
                    <ImageView android:layout_width="20dp" android:layout_height="20dp"
                        android:src="@drawable/ic_phone" android:tint="#FF9F0A" android:layout_marginEnd="10dp" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="CALL BOMBER" android:textColor="@color/white"
                        android:textSize="15sp" android:textStyle="bold" />
                </LinearLayout>
                <EditText android:id="@+id/etCallPhone" android:layout_width="match_parent"
                    android:layout_height="42dp" android:background="@drawable/bg_input"
                    android:hint="Phone number" android:inputType="phone" android:paddingHorizontal="14dp"
                    android:textColor="@color/white" android:textColorHint="@color/text_disabled"
                    android:textSize="13sp" android:layout_marginBottom="12dp" />
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:gravity="center">
                    <TextView android:id="@+id/tvCallStats" android:layout_width="0dp"
                        android:layout_weight="1" android:text="Total: 0  OK: 0  FAIL: 0"
                        android:textColor="@color/text_tertiary" android:textSize="9sp" />
                    <Button android:id="@+id/btnCallStart" android:layout_width="wrap_content"
                        android:layout_height="38dp" android:background="@drawable/btn_primary"
                        android:text="START" android:textColor="@color/white" android:textSize="11sp"
                        android:textStyle="bold" android:stateListAnimator="@null"
                        android:paddingHorizontal="20dp" android:layout_marginStart="8dp" />
                    <Button android:id="@+id/btnCallStop" android:layout_width="wrap_content"
                        android:layout_height="38dp" android:background="@drawable/btn_premium_stop"
                        android:text="STOP" android:textColor="@color/white" android:textSize="11sp"
                        android:textStyle="bold" android:stateListAnimator="@null"
                        android:paddingHorizontal="20dp" android:visibility="gone" />
                </LinearLayout>
            </LinearLayout>

            <LinearLayout android:id="@+id/smsSection" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="vertical"
                android:background="@drawable/glow_card" android:padding="18dp"
                android:layout_marginBottom="12dp" android:visibility="gone" android:elevation="4dp">
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:gravity="center_vertical" android:layout_marginBottom="12dp">
                    <ImageView android:layout_width="20dp" android:layout_height="20dp"
                        android:src="@drawable/ic_sms2" android:layout_marginEnd="10dp" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="SMS BOMBER" android:textColor="@color/white"
                        android:textSize="15sp" android:textStyle="bold" />
                </LinearLayout>
                <EditText android:id="@+id/etSmsPhone" android:layout_width="match_parent"
                    android:layout_height="42dp" android:background="@drawable/bg_input"
                    android:hint="Phone number" android:inputType="phone" android:paddingHorizontal="14dp"
                    android:textColor="@color/white" android:textColorHint="@color/text_disabled"
                    android:textSize="13sp" android:layout_marginBottom="12dp" />
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:gravity="center">
                    <TextView android:id="@+id/tvSmsStats" android:layout_width="0dp"
                        android:layout_weight="1" android:text="Total: 0  OK: 0  FAIL: 0"
                        android:textColor="@color/text_tertiary" android:textSize="9sp" />
                    <Button android:id="@+id/btnSmsStart" android:layout_width="wrap_content"
                        android:layout_height="38dp" android:background="@drawable/btn_primary"
                        android:text="START" android:textColor="@color/white" android:textSize="11sp"
                        android:textStyle="bold" android:stateListAnimator="@null"
                        android:paddingHorizontal="20dp" android:layout_marginStart="8dp" />
                    <Button android:id="@+id/btnSmsStop" android:layout_width="wrap_content"
                        android:layout_height="38dp" android:background="@drawable/btn_premium_stop"
                        android:text="STOP" android:textColor="@color/white" android:textSize="11sp"
                        android:textStyle="bold" android:stateListAnimator="@null"
                        android:paddingHorizontal="20dp" android:visibility="gone" />
                </LinearLayout>
            </LinearLayout>

            <LinearLayout android:id="@+id/whatsappSection" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="vertical"
                android:background="@drawable/glow_card" android:padding="18dp"
                android:layout_marginBottom="12dp" android:visibility="gone" android:elevation="4dp">
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:gravity="center_vertical" android:layout_marginBottom="12dp">
                    <ImageView android:layout_width="20dp" android:layout_height="20dp"
                        android:src="@drawable/ic_wa2" android:layout_marginEnd="10dp" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="WA BOMBER" android:textColor="@color/white"
                        android:textSize="15sp" android:textStyle="bold" />
                </LinearLayout>
                <EditText android:id="@+id/etWaPhone" android:layout_width="match_parent"
                    android:layout_height="42dp" android:background="@drawable/bg_input"
                    android:hint="Phone number" android:inputType="phone" android:paddingHorizontal="14dp"
                    android:textColor="@color/white" android:textColorHint="@color/text_disabled"
                    android:textSize="13sp" android:layout_marginBottom="12dp" />
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:gravity="center">
                    <TextView android:id="@+id/tvWaStats" android:layout_width="0dp"
                        android:layout_weight="1" android:text="Total: 0  OK: 0  FAIL: 0"
                        android:textColor="@color/text_tertiary" android:textSize="9sp" />
                    <Button android:id="@+id/btnWaStart" android:layout_width="wrap_content"
                        android:layout_height="38dp" android:background="@drawable/btn_primary"
                        android:text="START" android:textColor="@color/white" android:textSize="11sp"
                        android:textStyle="bold" android:stateListAnimator="@null"
                        android:paddingHorizontal="20dp" android:layout_marginStart="8dp" />
                    <Button android:id="@+id/btnWaStop" android:layout_width="wrap_content"
                        android:layout_height="38dp" android:background="@drawable/btn_premium_stop"
                        android:text="STOP" android:textColor="@color/white" android:textSize="11sp"
                        android:textStyle="bold" android:stateListAnimator="@null"
                        android:paddingHorizontal="20dp" android:visibility="gone" />
                </LinearLayout>
            </LinearLayout>

            <View android:layout_width="match_parent" android:layout_height="20dp" />
        </LinearLayout>
    </ScrollView>

    <!-- BOTTOM NAV -->
    <LinearLayout android:id="@+id/bottomNav" android:layout_width="match_parent"
        android:layout_height="72dp" android:layout_gravity="bottom" android:layout_marginHorizontal="16dp"
        android:layout_marginBottom="12dp" android:orientation="horizontal" android:gravity="center"
        android:background="@drawable/nav_glass" android:elevation="24dp" android:paddingBottom="6dp">
        <LinearLayout android:id="@+id/tabMix" android:layout_width="0dp" android:layout_height="match_parent"
            android:layout_weight="1" android:orientation="vertical" android:gravity="center"
            android:clickable="true" android:focusable="true" android:background="?attr/selectableItemBackgroundBorderless">
            <ImageView android:id="@+id/iconMix" android:layout_width="22dp" android:layout_height="22dp"
                android:src="@drawable/ic_sparkle" android:scaleType="centerInside" android:tint="#6A5CFF" />
            <TextView android:id="@+id/labelMix" android:layout_width="wrap_content"
                android:layout_height="wrap_content" android:text="MIX" android:textColor="#6A5CFF"
                android:textSize="10sp" android:textStyle="bold" android:letterSpacing="0.1"
                android:layout_marginTop="4dp" />
            <View android:id="@+id/indicatorMix" android:layout_width="20dp" android:layout_height="2dp"
                android:background="@color/accent_purple" android:layout_marginTop="3dp" />
        </LinearLayout>
        <LinearLayout android:id="@+id/tabCall" android:layout_width="0dp" android:layout_height="match_parent"
            android:layout_weight="1" android:orientation="vertical" android:gravity="center"
            android:clickable="true" android:focusable="true" android:background="?attr/selectableItemBackgroundBorderless">
            <ImageView android:id="@+id/iconCall" android:layout_width="22dp" android:layout_height="22dp"
                android:src="@drawable/ic_phone" android:scaleType="centerInside" android:tint="#666666" />
            <TextView android:id="@+id/labelCall" android:layout_width="wrap_content"
                android:layout_height="wrap_content" android:text="CALL" android:textColor="#666666"
                android:textSize="10sp" android:textStyle="bold" android:letterSpacing="0.1"
                android:layout_marginTop="4dp" />
            <View android:id="@+id/indicatorCall" android:layout_width="20dp" android:layout_height="2dp"
                android:background="@color/status_error" android:layout_marginTop="3dp" android:visibility="gone" />
        </LinearLayout>
        <LinearLayout android:id="@+id/tabSms" android:layout_width="0dp" android:layout_height="match_parent"
            android:layout_weight="1" android:orientation="vertical" android:gravity="center"
            android:clickable="true" android:focusable="true" android:background="?attr/selectableItemBackgroundBorderless">
            <ImageView android:id="@+id/iconSms" android:layout_width="22dp" android:layout_height="22dp"
                android:src="@drawable/ic_sms2" android:scaleType="centerInside" android:tint="#666666" />
            <TextView android:id="@+id/labelSms" android:layout_width="wrap_content"
                android:layout_height="wrap_content" android:text="SMS" android:textColor="#666666"
                android:textSize="10sp" android:textStyle="bold" android:letterSpacing="0.1"
                android:layout_marginTop="4dp" />
            <View android:id="@+id/indicatorSms" android:layout_width="20dp" android:layout_height="2dp"
                android:background="@color/status_error" android:layout_marginTop="3dp" android:visibility="gone" />
        </LinearLayout>
        <LinearLayout android:id="@+id/tabWa" android:layout_width="0dp" android:layout_height="match_parent"
            android:layout_weight="1" android:orientation="vertical" android:gravity="center"
            android:clickable="true" android:focusable="true" android:background="?attr/selectableItemBackgroundBorderless">
            <ImageView android:id="@+id/iconWa" android:layout_width="22dp" android:layout_height="22dp"
                android:src="@drawable/ic_wa2" android:scaleType="centerInside" android:tint="#666666" />
            <TextView android:id="@+id/labelWa" android:layout_width="wrap_content"
                android:layout_height="wrap_content" android:text="WA" android:textColor="#666666"
                android:textSize="10sp" android:textStyle="bold" android:letterSpacing="0.1"
                android:layout_marginTop="4dp" />
            <View android:id="@+id/indicatorWa" android:layout_width="20dp" android:layout_height="2dp"
                android:background="@color/status_error" android:layout_marginTop="3dp" android:visibility="gone" />
        </LinearLayout>
    </LinearLayout>
</FrameLayout>'''

print("Uploading REFERENCE-EXACT layout...")
upload(f"{LAYOUT}/activity_main.xml", layout)

v = subprocess.run(['shizuku', 'sh', '-c', f"wc -c '{LAYOUT}/activity_main.xml'"], capture_output=True, text=True, timeout=10)
print(f"activity_main.xml: {v.stdout.strip() or v.stderr.strip()}")
