import base64, subprocess

img_path = "/root/.hermes/webui/attachments/a35c08fa3b81/735b09a4ea526500f758d243e5d6d2f4.jpg"
target = "/storage/emulated/0/AndroidCSProjects/collbomber/app/src/main/res/drawable/bg_home.jpg"

# Read and encode image
with open(img_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()

print(f"Image encoded: {len(b64)} chars base64")

# Upload in chunks
chunks = [b64[i:i+1500] for i in range(0, len(b64), 1500)]
print(f"Split into {len(chunks)} chunks")

# Write first chunk (overwrite)
cmd = f"printf '%s' '{chunks[0]}' > /sdcard/tmp/up.b64"
r = subprocess.run(['shizuku', 'sh', '-c', cmd], capture_output=True, text=True, timeout=30)
if r.returncode != 0:
    print(f"FAIL first chunk: {r.stderr[:100]}")
    exit(1)

# Append remaining chunks
for i, chunk in enumerate(chunks[1:]):
    r = subprocess.run(['shizuku', 'sh', '-c', f"printf '%s' '{chunk}' >> /sdcard/tmp/up.b64"],
                       capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        print(f"FAIL chunk {i+2}: {r.stderr[:100]}")
        break
    if (i+1) % 20 == 0:
        print(f"  chunk {i+2}/{len(chunks)} done")

# Decode to target
r = subprocess.run(['shizuku', 'sh', '-c', f"base64 -d < /sdcard/tmp/up.b64 > '{target}' && rm /sdcard/tmp/up.b64"],
                   capture_output=True, text=True, timeout=20)
if r.returncode == 0:
    print("Decode successful!")
else:
    print(f"Decode FAIL: {r.stderr[:100]}")
    exit(1)

# Verify
r = subprocess.run(['shizuku', 'sh', '-c', f"wc -c '{target}'"], capture_output=True, text=True, timeout=10)
print(f"Target file: {r.stdout.strip() or r.stderr.strip()}")

# Also copy as bg_main_wallpaper.jpg (used by some layouts)
r = subprocess.run(['shizuku', 'sh', '-c', f"cp '{target}' '/storage/emulated/0/AndroidCSProjects/collbomber/app/src/main/res/drawable/bg_main_wallpaper.jpg'"],
                   capture_output=True, text=True, timeout=10)
print(f"Copied to bg_main_wallpaper.jpg: {r.returncode}")

print("DONE - Background image set!")
