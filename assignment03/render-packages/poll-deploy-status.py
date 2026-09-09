# -*- coding: utf-8 -*-
"""Poll deploy status 6 services A03 tới khi live/failed, sau đó health-check."""
import json
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KEY = "rnd_DowSbLLt8R98PvFBrsuTqh1Ed6Lo"
SERVICES = {
    "diabetes3-api": "srv-daggkuh42hec73c8ptl0",
    "house3-api": "srv-daggm1qjnfac73dku0d0",
    "comments3-api": "srv-daggm3u7bikc73b4dhrg",
    "diabetes3-web": "srv-daggm5qjnfac73dku72g",
    "house3-web": "srv-daggm7uk1f9s73csf800",
    "comments3-web": "srv-daggpgbl550s73bjv2l0",
}


def get(path):
    req = urllib.request.Request(
        f"https://api.render.com/v1{path}",
        headers={"Authorization": f"Bearer {KEY}", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, {}


deadline = time.time() + 45 * 60
states = {n: "?" for n in SERVICES}
while time.time() < deadline:
    time.sleep(90)
    done = 0
    for name, sid in SERVICES.items():
        if states[name] in ("live", "build_failed", "deactivated"):
            done += 1
            continue
        st, dep = get(f"/services/{sid}/deploys?limit=1")
        if st == 200 and dep:
            states[name] = dep[0].get("deploy", dep[0]).get("status", "?")
    print(" | ".join(f"{n.split('-')[0][:4]}:{s}" for n, s in states.items()))
    if all(s in ("live", "build_failed", "deactivated") for s in states.values()):
        break

print("\n==== TRẠNG THÁI CUỐI ====")
for name, s in states.items():
    print(f"  {name}: {s}")
