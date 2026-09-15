# -*- coding: utf-8 -*-
"""
DEPLOY 6 SERVICES LÊN RENDER — Assignment 04 (3 FastAPI + PyTorch CNN + 3 Streamlit)
Môn học: Intelligent System Development

Chạy:
    python deploy-render-a04.py rnd_xxx      # key qua arg
    python deploy-render-a04.py              # hoặc env RENDER_API_KEY / getpass

Trước đó: code đã push lên GitHub HieuGM/PTHTTM_PTIT (main, assignment04/render-packages/).

Bài học A02/A03 áp dụng:
  - rootDir KHÔNG set được lúc POST /services → PATCH top-level sau tạo
  - envVars cũng phải PUT riêng /services/{id}/env-vars rồi deploy lại
  - rate limit ~20 req/28 phút → script tự sleep 100s khi gặp 429
"""
import getpass
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_URL = "https://github.com/HieuGM/PTHTTM_PTIT"
BRANCH = "main"
API = "https://api.render.com/v1"
RP = "assignment04/render-packages"

SERVICES = [
    # (name, rootDir, startCommand, envVars)
    ("mnist4-api", f"{RP}/mnist4-api",
     "uvicorn main:app --host 0.0.0.0 --port $PORT", None),
    ("cifar4-api", f"{RP}/cifar4-api",
     "uvicorn main:app --host 0.0.0.0 --port $PORT", None),
    ("comments4-api", f"{RP}/comments4-api",
     "uvicorn main:app --host 0.0.0.0 --port $PORT", None),
    ("mnist4-web", f"{RP}/mnist4-web",
     "streamlit run app.py --server.port $PORT --server.address 0.0.0.0",
     {"MNIST_API_URL": "https://mnist4-api.onrender.com"}),
    ("cifar4-web", f"{RP}/cifar4-web",
     "streamlit run app.py --server.port $PORT --server.address 0.0.0.0",
     {"CIFAR_API_URL": "https://cifar4-api.onrender.com"}),
    ("comments4-web", f"{RP}/comments4-web",
     "streamlit run app.py --server.port $PORT --server.address 0.0.0.0",
     {"COMMENTS_API_URL": "https://comments4-api.onrender.com"}),
]


def call(method, path, key, body=None):
    """Gọi Render API — tự sleep+retry khi 429 rate limit."""
    for attempt in range(20):
        req = urllib.request.Request(
            f"{API}{path}",
            data=json.dumps(body).encode() if body else None,
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json", "Accept": "application/json"},
            method=method)
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 100
                print(f"    [429 rate limit — chờ {wait}s]")
                time.sleep(wait)
                continue
            try:
                return e.code, json.loads(e.read() or b"{}")
            except Exception:
                return e.code, {}
        except Exception as e:
            print("    [lỗi mạng:", str(e)[:80], "- retry 20s]")
            time.sleep(20)
    return 0, {}


def main():
    key = (sys.argv[1] if len(sys.argv) > 1 else
           os.environ.get("RENDER_API_KEY") or
           getpass.getpass("\nDán Render API key (rnd_...) rồi Enter:\n> ").strip())
    if not key.startswith("rnd_"):
        sys.exit("Key không hợp lệ (phải rnd_...)")

    st, me = call("GET", "/owners", key)
    if st != 200:
        sys.exit(f"Key không hợp lệ: {st} {me}")
    owner_id = me[0].get("owner", me[0])["id"]
    print("Đăng nhập Render OK — owner id:", owner_id)

    # services hiện có (bỏ qua nếu trùng tên)
    _, lst = call("GET", "/services?limit=100", key)
    existing = {}
    for item in (lst if isinstance(lst, list) else []):
        svc = item.get("service", item)
        existing[svc.get("name")] = svc.get("id")
    print("Services hiện có:", len(existing))

    created = {}
    for name, root, start, env in SERVICES:
        if name in existing:
            print(f"\n==> {name}: ĐÃ TỒN TẠI ({existing[name]}) — bỏ qua tạo")
            created[name] = existing[name]
            continue
        print(f"\n==> Tạo {name} ...")
        body = {
            "type": "web_service", "name": name, "ownerId": owner_id,
            "repo": REPO_URL, "branch": BRANCH, "autoDeploy": "yes",
            "serviceDetails": {
                "runtime": "python", "region": "singapore", "plan": "free",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": start,
                "envSpecificDetails": {
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": start,
                    "envVars": [{"key": "PYTHON_VERSION", "value": "3.11.9"}],
                },
            },
        }
        st, res = call("POST", "/services", key, body)
        if st in (200, 201):
            svc = res.get("service", res)
            sid = svc.get("id") or res.get("id")
            created[name] = sid
            print(f"    OK id {sid}")
        else:
            print(f"    LỖI {st}: {json.dumps(res, ensure_ascii=False)[:250]}")
        time.sleep(4)

    # PATCH rootDir top-level (bài học A02/A03: không set được lúc tạo)
    print("\n==> PATCH rootDir top-level ...")
    for name, sid in created.items():
        root = next(r for n, r, _, _ in SERVICES if n == name)
        st, res = call("PATCH", f"/services/{sid}", key, {"rootDir": root})
        print(f"  {name}: {st}")
        time.sleep(4)

    # PUT env-vars (web cần API URL) + PYTHON_VERSION mọi service
    print("\n==> PUT env-vars ...")
    for name, sid in created.items():
        env = next(e for n, _, _, e in SERVICES if n == name) or {}
        vars_ = [{"key": "PYTHON_VERSION", "value": "3.11.9"}]
        vars_ += [{"key": k, "value": v} for k, v in env.items()]
        st, res = call("PUT", f"/services/{sid}/env-vars", key, vars_)
        print(f"  {name}: {st}")
        time.sleep(4)

    # Trigger deploy với cấu hình đúng
    print("\n==> Trigger deploy ...")
    for name, sid in created.items():
        st, _ = call("POST", f"/services/{sid}/deploys", key, {})
        print(f"  {name}: {st}")
        time.sleep(4)

    # Chờ build
    print("\nChờ build (~5-10 phút/service; torch CPU tải chậm) ...")
    deadline = time.time() + 60 * 60
    pending = dict(created)
    while pending and time.time() < deadline:
        time.sleep(90)
        for name in list(pending):
            st, dep = call("GET", f"/services/{pending[name]}/deploys?limit=1", key)
            if st == 200 and dep:
                state = dep[0].get("deploy", dep[0]).get("status")
                print(f"  {name}: {state}")
                if state in ("live", "build_failed", "update_failed", "canceled"):
                    del pending[name]

    print("\n============ KẾT QUẢ ============")
    for name, sid in created.items():
        print(f"  https://{name}.onrender.com   (id {sid})")
    print("\n  Swagger: <api-url>/docs · Mobile: <api-url>/mobile")


if __name__ == "__main__":
    main()
