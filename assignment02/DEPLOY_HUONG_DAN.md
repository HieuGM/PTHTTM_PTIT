# 🚀 HƯỚNG DẪN DEPLOY 6 HF SPACES — ASSIGNMENT 02

> Toàn bộ 3 hệ thống (Diabetes, House Price, Customer Behavior) lên web công khai
> **miễn phí, không cần thẻ tín dụng, ~10 phút**.

## Kiến trúc deploy

```
┌─────────────────────────── Hugging Face Spaces (free) ───────────────────────────┐
│                                                                                   │
│  isd02-diabetes-web (Streamlit) ──┐                                               │
│  isd02-house-web    (Streamlit) ──┼──▶ 3 API Spaces (Docker FastAPI + model)      │
│  isd02-customer-web (Streamlit) ──┘        │                                      │
│                                             └── /mobile → trang mobile client     │
│                                                 (mỗi API Space tự host mobile UI)  │
└───────────────────────────────────────────────────────────────────────────────────┘
```

- **Web app** (Streamlit): người dùng nhập form → gọi REST API → hiện kết quả.
- **API** (Docker FastAPI): load `model/*.joblib` (pipeline sklearn) → `POST /predict`.
- **Mobile**: trang HTML mobile-first host ngay trong API Space tại `/mobile` —
  mở trên điện thoại thật được (gọi same-origin, không lỗi CORS).

## Các bước (chạy 1 lần)

### Bước 1 — Tạo HF token (2 phút)

1. Vào **https://huggingface.co/settings/tokens**
2. **New token** → đặt tên `isd02-deploy` → quyền **Write** → Create
3. Copy token (chỉ hiện 1 lần)

### Bước 2 — Chạy script (5–8 phút)

```bash
cd assignment02/deploy
python deploy-all.py
```

Script hỏi token → dán vào (không hiện ký tự, an toàn) → tự động:

1. Tạo 6 Spaces trên tài khoản bạn
2. Upload code + model + mobile page
3. **Tự cài URL API công khai vào web + mobile** (không phải sửa gì thêm)
4. In 6 link công khai

### Bước 3 — Kiểm tra (2 phút)

Chờ 2–5 phút build lần đầu, sau đó mở lần lượt:

| Kiểm tra | Link |
|---|---|
| Swagger UI API 1 | `https://<user>-isd02-diabetes-api.hf.space/docs` |
| Mobile app 1 | `https://<user>-isd02-diabetes-api.hf.space/mobile` |
| Web app 1 | `https://<user>-isd02-diabetes-web.hf.space` |
| ...tương tự cho house, customer | đổi tên trong URL |

Mỗi web: nhập số → bấm **Dự đoán** → thấy kết quả + confidence là OK.
Mỗi mobile: mở `/mobile` trên điện thoại → bấm **Dự đoán** → kết quả hiện.

## Lưu ý

- **Space free ngủ sau 48h không truy cập** — mở link là tự thức dậy (~30–60s).
- Muốn đổi model: chạy lại notebook → copy `model/*.joblib` vào
  `deploy/hf_*_api/` → chạy lại `python deploy-all.py` (script ghi đè an toàn).
- Token KHÔNG được lưu vào repo — script chỉ dùng trong phiên chạy.
- Sau khi deploy xong, **điền 6 link vào `report/` mục Web & Mobile Deployment**
  và README mục "Link demo".

## Sự cố thường gặp

| Triệu chứng | Nguyên nhân & cách xử lý |
|---|---|
| Space "Building" lâu >10 phút | Docker build lần đầu tải sklearn ~2 phút; nếu >15 phút → Runtime tab → Restart |
| Web báo "Không gọi được API" | API Space chưa build xong — chờ rồi refresh; kiểm tra `/health` |
| Lỗi 401 khi deploy | Token hết hạn/quyền Read-only → tạo lại token Write |
| Mobile gọi API lỗi | Mở lại `/mobile`, kiểm tra ô "Địa chỉ REST API" đúng URL Space |
