# 🚀 HƯỚNG DẪN DEPLOY RENDER — ASSIGNMENT 02

> 6 services (3 FastAPI + 3 Streamlit) lên Render **free** — không cần thẻ tín dụng.

## Kiến trúc

```
diabetes-web (Streamlit) ──┐
house-web    (Streamlit) ──┼──▶ diabetes-api / house-api / customer-api (FastAPI + model)
customer-web (Streamlit) ──┘         │
                                     └── /mobile → trang mobile client (host ngay trong API)
```

Repo: `https://github.com/HieuGM/PTHTTM_PTIT` — mỗi service trỏ `rootDir` vào
`render-packages/<tên>/` (đã đẩy lên GitHub, URL onrender đã cài sẵn trong code).

## Cách 1 — Script tự động (đã làm xong 1 lần)

```bash
cd assignment02/render-packages
python deploy-render.py          # hỏi API key (rnd_...)
```

Lưu ý **rate limit Render API**: 20 requests / ~28 phút. Script sleep 3s giữa các POST
và 60s giữa các lần poll — nếu gặp 429, đợi ~28 phút chạy lại (script bỏ qua service đã tạo).

## Cách 2 — Blueprint trên web (không cần key)

1. Mở https://dashboard.render.com/blueprints → **New Blueprint Instance**
2. Chọn repo `HieuGM/PTHTTM_PTIT`
3. Render đọc `render-packages/render.yaml` → hiện 6 services → **Apply**
4. Đợi build ~5 phút/service

## Link sau khi deploy

| Service | URL | Kiểm tra |
|---|---|---|
| diabetes-api | https://diabetes-api-a02.onrender.com | `/health` · `/docs` · `/mobile` |
| house-api | https://house-api-a02.onrender.com | `/health` · `/docs` · `/mobile` |
| customer-api | https://customer-api-a02.onrender.com | `/health` · `/docs` · `/mobile` |
| diabetes-web | https://diabetes-web-a02.onrender.com | mở web, bấm Dự đoán |
| house-web | https://house-web-a02.onrender.com | mở web, bấm Định giá |
| customer-web | https://customer-web-a02.onrender.com | mở web, bấm Dự đoán sở thích |

## Sự cố thường gặp

| Triệu chứng | Xử lý |
|---|---|
| Free service ngủ sau 15 phút không dùng | Mở link — tự thức dậy sau ~50s (cold start) |
| Web báo "Không gọi được API" | API đang ngủ/chưa build — mở link API trước, chờ `/health` trả ok |
| Build failed | Dashboard → service → Events/Logs xem lỗi; thường là requirements hoặc path model |
| 429 rate limit khi tạo API | Đợi 28 phút, chạy lại script — service đã tạo sẽ được bỏ qua |
| Đổi model sau này | Chạy lại notebook → copy `*.joblib` vào `render-packages/<svc>/model/` → commit + push → Render auto-deploy |

## Sau deploy

Điền 6 link vào:
- `README.md` — bảng "Link demo" cuối file
- `report/BAO_CAO_A02.docx` — mục Web & Mobile Deployment (xuất lại PDF)
