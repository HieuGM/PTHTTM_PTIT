# -*- coding: utf-8 -*-
"""Fix rootDir cho 5 services A03 — PATCH top-level rootDir (bài học A02:
rootDir KHÔNG nằm trong serviceDetails mà ở top level của PATCH body)."""
import json
import os
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KEY = os.environ.get("RENDER_API_KEY", "")  # không hardcode key!
FIX = {
    "srv-daggkuh42hec73c8ptl0": ("diabetes3-api", "assignment03/render-packages/diabetes3-api"),
    "srv-daggm1qjnfac73dku0d0": ("house3-api", "assignment03/render-packages/house3-api"),
    "srv-daggm3u7bikc73b4dhrg": ("comments3-api", "assignment03/render-packages/comments3-api"),
    "srv-daggm5qjnfac73dku72g": ("diabetes3-web", "assignment03/render-packages/diabetes3-web"),
    "srv-daggm7uk1f9s73csf800": ("house3-web", "assignment03/render-packages/house3-web"),
}


def call(method, path, body=None):
    req = urllib.request.Request(
        f"https://api.render.com/v1{path}",
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {KEY}",
                 "Content-Type": "application/json", "Accept": "application/json"},
        method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


for sid, (name, root) in FIX.items():
    st, res = call("PATCH", f"/services/{sid}", {"rootDir": root})
    ok = "OK" if st == 200 else f"LỖI {st}"
    print(f"{name}: PATCH rootDir -> {root} = {ok}")
    if st != 200:
        print("   ", json.dumps(res, ensure_ascii=False)[:200])
    time.sleep(3)

# Trigger deploy lại
print("\nTrigger deploy lại ...")
for sid, (name, _) in FIX.items():
    st, res = call("POST", f"/services/{sid}/deploys", {})
    print(f"  {name}: deploy trigger = {st}")
    time.sleep(3)
