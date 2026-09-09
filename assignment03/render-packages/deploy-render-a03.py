# -*- coding: utf-8 -*-
"""
DEPLOY 6 SERVICES LÊN RENDER — Assignment 03 (3 FastAPI + PyTorch + 3 Streamlit)
Môn học: Intelligent System Development

Cách chạy:
    python deploy-render-a03.py            # hỏi key bằng getpass
    python deploy-render-a03.py rnd_xxx    # hoặc truyền key trực tiếp

Yêu cầu:
    - Code đã push lên GitHub repo HieuGM/PTHTTM_PTIT (nhánh main, assignment03/)
    - Render API key (Account Settings → API Keys)

Script tạo 6 web services free region Singapore, đợi build, in URL.
Rate limit Render API: 20 req / ~28 phút — script sleep 3s giữa các POST.
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
    # (name, rootDir, startCommand, envVars)
    ("diabetes3-api", "assignment03/render-packages/diabetes3-api",
     "uvicorn main:app --host 0.0.0.0 --port $PORT", None),
    ("house3-api", "assignment03/render-packages/house3-api",
     "uvicorn main:app --host 0.0.0.0 --port $PORT", None),
    ("comments3-api", "assignment03/render-packages/comments3-api",
     "uvicorn main:app --host 0.0.0.0 --port $PORT", None),
    ("diabetes3-web", "assignment03/render-packages/diabetes3-web",
     "streamlit run app.py --server.port $PORT --server.address 0.0.0.0",
     {"DIABETES_API_URL": "https://diabetes3-api.onrender.com"}),
    ("house3-web", "assignment03/render-packages/house3-web",
     "streamlit run app.py --server.port $PORT --server.address 0.0.0.0",
     {"HOUSE_API_URL": "https://house3-api.onrender.com"}),
    ("comments3-web", "assignment03/render-packages/comments3-web",
     "streamlit run app.py --server.port $PORT --server.address 0.0.0.0",
     {"COMMENTS_API_URL": "https://comments3-api.onrender.com"}),
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
        try:
            return e.code, json.loads(e.read() or b"{}")
        except Exception:
            return e.code, {}


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else (
        os.environ.get("RENDER_API_KEY") or getpass.getpass(
            "\nDán Render API key (rnd_...) rồi Enter:\n> ").strip())
    if not key.startswith("rnd_"):
        sys.exit("Key không hợp lệ (phải bắt đầu rnd_)")

    status, me = call("GET", "/owners", key)
    if status != 200:
        sys.exit(f"Key không hợp lệ: {status} {me}")
    owner = me[0].get("owner", me[0])
    owner_id = owner["id"]
    print(f"\nĐăng nhập Render OK — owner: {owner.get('name', owner_id)}")

    # Bỏ qua service đã tồn tại (chạy lại sau rate limit không tạo trùng)
    _, svc_list = call("GET", "/services?limit=100", key)
    existing = {}
    existing_urls = {}
    if isinstance(svc_list, list):
        for item in svc_list:
            svc = item.get("service", item)
            existing[svc.get("name")] = svc.get("id")
            existing_urls[svc.get("name")] = svc.get("serviceDetails", {}).get("url")

    created = {}
    for name, root, start, env in SERVICES:
        if name in existing:
            print(f"\n==> {name}: ĐÃ TỒN TẠI (id {existing[name]}) — bỏ qua")
            created[name] = (existing[name], existing_urls.get(name)
                             or f"https://{name}.onrender.com")
            continue
        print(f"\n==> Tạo service {name} ...")
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
                        + ([{"key": k, "value": v} for k, v in env.items()]
                           if env else [])
                    ),
                },
            },
        }
        status, res = call("POST", "/services", key, body)
        if status in (200, 201):
            svc = res.get("service", res)
            sid = svc.get("id") or res.get("id")
            url = (svc.get("serviceDetails", {}).get("url")
                   or res.get("serviceDetails", {}).get("url")
                   or f"https://{name}.onrender.com")
            if not sid:
                print(f"    OK nhưng không lấy được id — response: "
                      f"{json.dumps(res, ensure_ascii=False)[:200]}")
            else:
                created[name] = (sid, url)
                print(f"    OK: {url} (id {sid})")
        else:
            print(f"    LỖI {status}: {json.dumps(res, ensure_ascii=False)[:300]}")
        time.sleep(3)

    if not created:
        sys.exit("Không tạo được service nào")

    print("\nChờ build lần đầu (~3-8 phút/service, torch CPU tải chậm hơn A02) ...")
    deadline = time.time() + 45 * 60
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
                    print(f"  !! {name} BUILD FAILED — xem log trên dashboard")
                    del pending[name]

    print("\n================ KẾT QUẢ ================")
    for name, (sid, url) in created.items():
        kind = "API" if "api" in name else "WEB"
        print(f"  [{kind:3s}] {url}")
    print("\n  Swagger:  <api-url>/docs")
    print("  Mobile:   <api-url>/mobile")


if __name__ == "__main__":
    main()
