# -*- coding: utf-8 -*-
"""
DEPLOY 6 HF SPACES — Assignment 02 (3 API Docker + 3 Web Streamlit)
Môn học: Intelligent System Development

Cách chạy:
    python deploy-all.py

Script sẽ:
1. Hỏi HF token (dán vào khi được hỏi — quyền Write, tạo tại
   https://huggingface.co/settings/tokens)
2. Tạo 6 Spaces trên tài khoản của bạn:
   - isd02-diabetes-api    (Docker FastAPI + model + mobile page)
   - isd02-house-api       (Docker FastAPI + model + mobile page)
   - isd02-customer-api    (Docker FastAPI + model + mobile page)
   - isd02-diabetes-web    (Streamlit — gọi API)
   - isd02-house-web       (Streamlit)
   - isd02-customer-web    (Streamlit)
3. Upload code, tự động cài URL API thật vào web + mobile
4. In danh sách link công khai để nộp bài

Lưu ý: 6 Spaces free cùng lúc là OK (HF cho nhiều Space free).
Space free ngủ sau 48h không dùng — mở link là tự thức dậy (~30-60s lần đầu).
"""
import os
import sys
import getpass
import shutil
import re
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEPLOY_DIR = Path(__file__).parent
USERNAME_FILE = DEPLOY_DIR / ".hf_username"

SPACES = [
    # (space_id_suffix, pack_dir, sdk, kind)
    ("isd02-diabetes-api", "hf_diabetes_api", "docker", "api"),
    ("isd02-house-api", "hf_house_api", "docker", "api"),
    ("isd02-customer-api", "hf_customer_api", "docker", "api"),
    ("isd02-diabetes-web", "hf_diabetes_web", "streamlit", "web"),
    ("isd02-house-web", "hf_house_web", "streamlit", "web"),
    ("isd02-customer-web", "hf_customer_web", "streamlit", "web"),
]

# URL API public sẽ cài vào web/mobile sau khi Space API được tạo
API_URLS = {
    "diabetes": "https://{user}-isd02-diabetes-api.hf.space",
    "house": "https://{user}-isd02-house-api.hf.space",
    "customer": "https://{user}-isd02-customer-api.hf.space",
}


def main():
    print("=" * 64)
    print("DEPLOY 6 HF SPACES — ISD ASSIGNMENT 02")
    print("=" * 64)

    # 1) Token
    token = os.environ.get("HF_TOKEN") or getpass.getpass(
        "\n📌 Dán HF token (quyền Write) rồi Enter (không hiện ký tự):\n> ").strip()
    if not token:
        sys.exit("Không có token — thoát.")

    from huggingface_hub import HfApi
    api = HfApi(token=token)

    try:
        who = api.whoami()
        user = who["name"]
    except Exception as e:
        sys.exit(f"Token không hợp lệ: {e}")
    print(f"\n✅ Đăng nhập: {user} ({who.get('type', 'user')})")
    USERNAME_FILE.write_text(user, encoding="utf-8")

    # 2) Tạo + push từng Space
    created = {}
    for suffix, pack, sdk, kind in SPACES:
        repo_id = f"{user}/{suffix}"
        app_key = ("diabetes" if "diabetes" in suffix
                   else "house" if "house" in suffix else "customer")
        public_api = API_URLS[app_key].format(user=user)

        # Stage dir: copy pack → cài URL → upload
        stage = DEPLOY_DIR / f"_stage_{suffix}"
        if stage.exists():
            shutil.rmtree(stage)
        shutil.copytree(DEPLOY_DIR / pack, stage)

        # Ghi README Space (HF yêu cầu metadata trong README)
        extra = (f"title: ISD02 {suffix}\nemoji: 🩸\n"
                 if "diabetes" in suffix else
                 f"title: ISD02 {suffix}\nemoji: 🏠\n"
                 if "house" in suffix else
                 f"title: ISD02 {suffix}\nemoji: 🛒\n")
        (stage / "README.md").write_text(
            f"---\n{extra}sdk: {sdk}\nsdk_version: {'1.32.0' if sdk == 'streamlit' else ''}\n"
            f"app_file: {'app.py' if sdk == 'streamlit' else ''}\npinned: false\n---\n\n"
            f"# {suffix}\nAssignment 02 — Intelligent System Development (PTIT).",
            encoding="utf-8")
        if sdk == "streamlit":
            # bỏ dòng sdk_version rỗng gây lỗi
            rd = stage / "README.md"
            rd.write_text(re.sub(r"sdk_version: \n", "", rd.read_text(encoding="utf-8")),
                          encoding="utf-8")

        # Cài URL API công khai vào web app / mobile page
        if kind == "web":
            f = stage / "app.py"
            src = f.read_text(encoding="utf-8")
            env_names = {"diabetes": "DIABETES_API_URL", "house": "HOUSE_API_URL",
                         "customer": "CUSTOMER_API_URL"}
            src = re.sub(
                rf'os\.environ\.get\("{env_names[app_key]}",\s*"[^"]*"\)',
                f'os.environ.get("{env_names[app_key]}", "{public_api}")',
                src)
            f.write_text(src, encoding="utf-8")
        else:
            f = stage / "mobile" / "index.html"
            src = f.read_text(encoding="utf-8")
            src = re.sub(r'value="http://localhost:\d+"', f'value="{public_api}"', src)
            src = re.sub(r"localStorage.getItem\('\w+'\) \|\| \"[^\"]*\"",
                         f"'{public_api}'", src)
            f.write_text(src, encoding="utf-8")

        print(f"\n🚀 Deploy {repo_id} ...")
        try:
            api.create_repo(repo_id=repo_id, repo_type="space",
                            space_sdk=sdk, exist_ok=True, private=False)
            api.upload_folder(folder_path=str(stage), repo_id=repo_id,
                              repo_type="space", commit_message="deploy assignment 02")
            url = f"https://{user}-{suffix}.hf.space"
            created[suffix] = url
            print(f"   ✅ {url}")
        except Exception as e:
            print(f"   ❌ LỖI: {e}")
        finally:
            shutil.rmtree(stage, ignore_errors=True)

    # 3) Tổng kết
    print("\n" + "=" * 64)
    print("TỔNG KẾT — LINK CÔNG KHAI (chờ ~2-5 phút build lần đầu)")
    print("=" * 64)
    for suffix, url in created.items():
        kind = "API (Docker FastAPI)" if "api" in suffix else "WEB (Streamlit)"
        print(f"  [{kind:20s}] {url}")
    if created:
        print(f"\n📱 Trang mobile từng app: <api-url>/mobile")
        print("🔍 Swagger UI từng API:   <api-url>/docs")


if __name__ == "__main__":
    main()
