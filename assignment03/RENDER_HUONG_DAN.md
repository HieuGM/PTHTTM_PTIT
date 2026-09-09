# 🚀 HƯỚNG DẪN DEPLOY RENDER — ASSIGNMENT 03

> 6 services (3 FastAPI + PyTorch MLP + 3 Streamlit) lên Render **free** region Singapore.

## Kiến trúc

```
diabetes3-web (Streamlit) ──┐
house3-web    (Streamlit) ──┼──▶ diabetes3-api / house3-api / comments3-api (FastAPI + PyTorch MLP)
comments3-web (Streamlit) ──┘         │
                                      └── /mobile → trang mobile client (host ngay trong API)
```

Repo: `https://github.com/HieuGM/PTHTTM_PTIT` — mỗi service trỏ `rootDir` vào
`assignment03/render-packages/<tên>/`.

## Khác biệt so với A02

| | A02 | A03 |
|---|---|---|
| Model | sklearn joblib (RF/GB) | **PyTorch .pth state_dict** + meta joblib |
| requirements | scikit-learn | + `torch==2.14.0` qua `--extra-index-url https://download.pytorch.org/whl/cpu` (CPU wheel ~200MB, nhẹ hơn CUDA 2GB) |
| Build time | ~3-4 phút | ~5-8 phút (torch tải chậm hơn) |
| RAM free | ~200MB | ~300-400MB (import torch + model nhỏ <2MB weights) |

## Link sau khi deploy

| Service | URL | Kiểm tra |
|---|---|---|
| diabetes3-api | https://diabetes3-api.onrender.com | `/health` · `/docs` · `/mobile` |
| house3-api | https://house3-api.onrender.com | `/health` · `/docs` · `/mobile` |
| comments3-api | https://comments3-api.onrender.com | `/health` · `/docs` · `/mobile` |
| diabetes3-web | https://diabetes3-web.onrender.com | mở web, bấm Dự đoán |
| house3-web | https://house3-web.onrender.com | mở web, bấm Định giá |
| comments3-web | https://comments3-web.onrender.com | mở web, bấm Phân tích |

## Script (đã chạy khi deploy)

```bash
cd assignment03/render-packages   # (trong repo clone)
python deploy-render-a03.py rnd_...   # tạo 6 services qua Render API
python fix-rootdir-a03.py             # PATCH rootDir top-level (bài học A02)
python poll-deploy-status.py          # theo dõi build
```

Lưu ý: **Render free giới hạn 25 services/workspace** — nếu đầy, xóa service cũ
suspended trên dashboard (đã xóa 1 ClubSync cũ suspended để lấy slot).

## Sự cố thường gặp

| Triệu chứng | Xử lý |
|---|---|
| Service ngủ sau 15 phút | Mở link — tự thức dậy sau ~50s (cold start) |
| Web báo "Không gọi được API" | API đang ngủ — mở link API trước, chờ `/health` |
| `rootDir` trống khi tạo qua API | PATCH **top-level** `rootDir` (không phải trong serviceDetails) |
| "Hobby Tier limited to 25 services" | Xóa service cũ suspended trên dashboard rồi tạo lại |
| Build fail vì torch | Đảm bảo `--extra-index-url .../whl/cpu` dòng đầu requirements |
| 429 rate limit khi gọi API Render | Đợi ~28 phút chạy lại script (service đã tạo sẽ bỏ qua) |

## Sau deploy

Đã điền 6 link vào `README.md` (bảng Link demo) + `report/BAO_CAO_A03.docx` mục 7.
