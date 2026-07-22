import subprocess

api_path = "/storage/emulated/0/AndroidCSProjects/collbomber/app/src/main/kotlin/com/rolex/mybasic/collbomber/ApiConfig.kt"

r = subprocess.run(['shizuku', 'sh', '-c', f"cat '{api_path}'"], capture_output=True, text=True, timeout=15)
content = r.stderr or r.stdout

old = '            ApiConfig("ThakurBombCyber",'
new = '            // 🔥🚨 IMPORTANT: ThakurBombCyber — exact 5s delay (delayMs=5000)\n            ApiConfig("ThakurBombCyber",'

content = content.replace(old, new, 1)

import base64
b64 = base64.b64encode(content.encode()).decode()
chunks = [b64[i:i+1500] for i in range(0, len(b64), 1500)]

subprocess.run(['shizuku', 'sh', '-c', f"rm -f '{api_path}'"], capture_output=True, timeout=10)
subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{chunks[0]}' > /sdcard/tmp/up.b64"], capture_output=True, timeout=30)
for c in chunks[1:]:
    subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{c}' >> /sdcard/tmp/up.b64"], capture_output=True, timeout=15)
subprocess.run(['shizuku', 'sh', '-c', f"base64 -d < /sdcard/tmp/up.b64 > '{api_path}' && rm /sdcard/tmp/up.b64"], capture_output=True, timeout=20)

v = subprocess.run(['shizuku', 'sh', '-c', f"wc -c '{api_path}'"], capture_output=True, text=True, timeout=10)
print(f"Uploaded: {v.stdout.strip() or v.stderr.strip()}")

r2 = subprocess.run(['shizuku', 'sh', '-c', f"cat '{api_path}' | head -n 84 | tail -n 5"], capture_output=True, text=True, timeout=10)
print(r2.stdout or r2.stderr)
