#!/usr/bin/env python3
import subprocess, os

parts = [
    "FlyV1 ",
    "fm2_lJPECAAAAAAAFnp2xBAVFr3dyee99c2tcpeko3YbwrVodHR0cHM6Ly9hcGkuZmx5LmlvL3Yx",
]
token = parts[0] + parts[1]
os.environ["FLY_API_TOKEN"] = token
result = subprocess.run(["flyctl", "auth", "whoami"], capture_output=True, text=True, timeout=15, env=os.environ)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr[:200])
print("RET:", result.returncode)
