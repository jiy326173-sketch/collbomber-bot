#!/usr/bin/env python3
"""Upload smartisland project - v3 with skip-existing."""
import base64, os, subprocess, sys

REMOTE_BASE = '/storage/emulated/0/AndroidCSProjects/smartlsland'
LOCAL_BASE = '/root/workspace/smartisland'

def sh(cmd, t=30):
    r = subprocess.run(['shizuku','sh','-c',cmd], capture_output=True, text=True, timeout=t)
    return r.returncode==0, (r.stdout+r.stderr).strip()

def upload_one(local, remote):
    with open(local,'rb') as f: content=f.read()
    if not content:
        sh(f"mkdir -p '{os.path.dirname(remote)}' && touch '{remote}'", 10)
        return True

    # Check if already correct
    ok, out = sh(f"test -f '{remote}' && wc -c '{remote}'", 10)
    if ok and out:
        try:
            sz = int(out.split()[0])
            if sz == len(content): return True
        except: pass

    sh(f"mkdir -p '{os.path.dirname(remote)}'", 10)
    sh(f"rm -f '{remote}'", 10)

    b64 = base64.b64encode(content).decode()
    chunks = [b64[i:i+1000] for i in range(0, len(b64), 1000)]

    ok, err = sh(f"printf '%s' '{chunks[0]}' > /sdcard/tmp/_u.b64", 30)
    if not ok: return False
    for c in chunks[1:]:
        ok, _ = sh(f"printf '%s' '{c}' >> /sdcard/tmp/_u.b64", 20)
        if not ok: return False
    ok, _ = sh(f"base64 -d < /sdcard/tmp/_u.b64 > '{remote}' && rm -f /sdcard/tmp/_u.b64", 20)
    if not ok: return False

    ok, out = sh(f"wc -c '{remote}'", 10)
    if ok and out:
        try:
            return int(out.split()[0]) == len(content)
        except: pass
    return sh(f"test -f '{remote}' && echo ok", 10)[1]=='ok'

def main():
    files = []
    for root, dirs, fns in os.walk(LOCAL_BASE):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fn in fns:
            l = os.path.join(root, fn)
            r = os.path.join(REMOTE_BASE, os.path.relpath(l, LOCAL_BASE))
            files.append((l,r))

    total=len(files); ok=0; fail=[]
    for i,(l,r) in enumerate(files,1):
        rel=os.path.relpath(l,LOCAL_BASE)
        sys.stdout.write(f"[{i}/{total}] {rel}..."); sys.stdout.flush()
        if upload_one(l,r):
            print(" OK",flush=True); ok+=1
        else:
            print(" FAIL",flush=True); fail.append(rel)
    print(f"\nDone: {ok}/{total}")
    if fail: print(f"Failed: {fail}")

if __name__=='__main__': sys.exit(0 if not main() else 1)
