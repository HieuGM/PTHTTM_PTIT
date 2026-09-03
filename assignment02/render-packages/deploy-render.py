# -*- coding: utf-8 -*-
"""
DEPLOY 6 SERVICES LÊN RENDER — Assignment 02 (3 FastAPI + 3 Streamlit)
Môn học: Intelligent System Development

Cách chạy:
    python deploy-render.py            # hỏi key bằng getpass (không hiện ký tự)
    python deploy-render.py rnd_xxx    # hoặc truyền key trực tiếp

Yêu cầu trước đó:
    - Code đã push lên GitHub repo HieuGM/PTHTTM_PTIT (nhánh main)
    - Render API key (Account Settings → API Keys → New API Key)

Script sẽ:
1. Tạo 6 web services (free) qua Render API, mỗi service trỏ vào thư mục con
   render-packages/<tên> của repo
2. Đợi build + health-check từng API service (/health trả 200)
3. In danh sách URL công khai
"""
import sys
import os
import time
import json
import getpass
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_URL = "https://github.com/HieuGM/PTHTTM_PTIT"
BRANCH = "main"
API = "https://api.render.com/v1"

SERVICES = [
    # (name, rootDir, startCommand, envVars, is_api)
    ("diabetes-api", "render-packages/diabetes-api",
     "uvicorn main:app --host 0.0.0.0 --port $PORT", None, True),
    ("house-api", "render-packages/house-api",
     "uvicorn main:app --host 0.0.0.0 --port $PORT", None, True),
    ("customer-api", "render-packages/customer-api",
     "uvicorn main:app --host 0.0.0.0 --port $PORT", None, True),
    ("diabetes-web", "render-packages/diabetes-web",
     "streamlit run app.py --server.port $PORT --server.address 0.0.0.0",
     {"DIABETES_API_URL": "https://diabetes-api-a02.onrender.com"}, False),
    ("house-web", "render-packages/house-web",
     "streamlit run app.py --server.port $PORT --server.address 0.0.0.0",
     {"HOUSE_API_URL": "https://house-api-a02.onrender.com"}, False),
    ("customer-web", "render-packages/customer-web",
     "streamlit run app.py --server.port $PORT --server.address 0.0.0.0",
     {"CUSTOMER_API_URL": "https://customer-api-a02.onrender.com"}, False),
]


def call(method: str, path: str, key: str, body: dict | None = None):
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json",
                 "Accept": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else (
        os.environ.get("RENDER_API_KEY") or getpass.getpass(
            "\nDán Render API key (rnd_...) rồi Enter:\n> ").strip())
    if not key.startswith("rnd_"):
        sys.exit("Key không hợp lệ (phải bắt đầu rnd_)")

    # verify key — response dạng [{"owner": {...}}]
    status, me = call("GET", "/owners", key)
    if status != 200:
        sys.exit(f"Key không hợp lệ: {status} {me}")
    owner = me[0].get("owner", me[0])
    owner_id = owner["id"]
    print(f"\nDang nhap Render OK — owner: {owner.get('name', owner_id)}")

    # Tạo service — cấu trúc serviceDetails + envSpecificDetails (Render API v1)
    created = {}
    for name, root, start, env, is_api in SERVICES:
        print(f"\n==> Tao service {name} ...")
        body = {
            "type": "web_service",
            "name": name,
            "ownerId": owner_id,
            "repo": REPO_URL,
            "branch": BRANCH,
            "autoDeploy": "yes",
            "serviceDetails": {
                "runtime": "python",
                "region": "singapore",
                "plan": "free",
                "rootDir": root,
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": start,
                "envSpecificDetails": {
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": start,
                    "envVars": (
                        [{"key": "PYTHON_VERSION", "value": "3.11.9"}]
                        + ([{"key": k, "value": v} for k, v in env.items()] if env else [])
                    ),
                },
            },
        }
        status, res = call("POST", "/services", key, body)
        if status in (200, 201):
            sid = res["id"]
            url = res.get("serviceDetails", {}).get("url", f"https://{name}-a02.onrender.com")
            created[name] = (sid, url)
            print(f"    OK: {url} (id {sid})")
        else:
            print(f"    LOI {status}: {json.dumps(res, ensure_ascii=False)[:300]}")
        time.sleep(3)  # tránh rate limit (limit 20 req / ~28 phút)

    if not created:
        sys.exit("Khong tao duoc service nao")

    # Đợi deploy xong (build lần đầu ~3-6 phút/service; poll mỗi 60s để tiết kiệm rate limit)
    print("\nCho build lan dau (~3-6 phut moi service) ...")
    deadline = time.time() + 35 * 60
    pending = dict(created)
    while pending and time.time() < deadline:
        time.sleep(60)
        for name in list(pending):
            sid, url = pending[name]
            st, dep = call("GET", f"/services/{sid}/deploys?limit=1", key)
            if st == 200 and dep:
                item = dep[0].get("deploy", dep[0])
                state = item.get("status")
                print(f"  {name}: {state}")
                if state == "live":
                    del pending[name]
                elif state in ("build_failed", "update_failed", "canceled"):
                    print(f"  !! {name} BUILD FAILED — xem log tren dashboard")
                    del pending[name]

    print("\n================ KET QUA ================")
    for name, (sid, url) in created.items():
        kind = "API" if "api" in name else "WEB"
        print(f"  [{kind:3s}] {url}")
    print("\n  Swagger:  <api-url>/docs")
    print("  Mobile:   <api-url>/mobile")


if __name__ == "__main__":
    main()
