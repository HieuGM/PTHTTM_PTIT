# 🚀 HƯỚNG DẪN DEPLOY WEB APP (2 phương án)

> Mục tiêu: có **2 link web công khai** nộp kèm assignment. Chọn **1 trong 2 phương án** — đều miễn phí.

## Chọn phương án nào?

| | ⚡ Phương án A: Render (NHANH NHẤT) | 🤗 Phương án B: Hugging Face Spaces |
|---|---|---|
| Thời gian | ~5 phút/app | ~5 phút/app |
| Cần gì | GitHub account (đẩy code lên) | HF account |
| Thẻ tín dụng | ⚠️ Render free có thể hỏi verify thẻ (không trừ tiền) | ❌ không cần |
| Ổn định | free 750 giờ/tháng | sleep sau 48h không dùng, mở lại là chạy |
| Streamlit SDK | tự nhận từ Dockerfile | chọn **Docker SDK** (Streamlit đã bị giấu) |

**Khuyên dùng: Phương án A (Render)** — vì bạn nói Render quen/được; script dưới đây lo hết.

---

## ⚡ PHƯƠNG ÁN A — RENDER.COM (như mẫu của bạn Linh dùng Flask + Render)

### A0. Push code lên GitHub (làm 1 lần)

1. Tạo repo trên GitHub: ví dụ `isd-assignment01` (Private hay Public đều được)
2. Từ thư mục `assignment01/`, đẩy code:

```bash
cd assignment01
git init
git add apps/ artifacts/
git commit -m "assignment01 apps"
git remote add origin https://github.com/TEN-BAN/isd-assignment01.git
git branch -M main
git push -u origin main
```

> ⚠️ File `ames_model.joblib` 10MB — GitHub cho tối đa 100MB/file, đẩy được bình thường.

### A1. Deploy app bệnh tim lên Render

1. Vào **https://dashboard.render.com** → đăng ký/đăng nhập (Google/GitHub)
2. **New + → Web Service**
3. **Connect a repository** → chọn repo `isd-assignment01`
4. Cấu hình (điền đúng từng ô):

| Ô | Giá trị |
|---|---|
| **Name** | `heart-disease-system` |
| **Region** | Singapore (gần VN) |
| **Branch** | `main` |
| **Runtime** | **Docker** ⚠️ (Render tự đọc Dockerfile) |
| **Root Directory** | `apps/heart_app` ⚠️ quan trọng |
| **Instance Type** | Free |

5. **Deploy Web Service** → chờ build ~3–5 phút (Render tự docker build)
6. Xong có link: `https://heart-disease-system.onrender.com` ✅

### A2. Deploy app giá nhà

Lặp lại A1 với:

| Ô | Giá trị |
|---|---|
| **Name** | `house-price-system` |
| **Root Directory** | `apps/house_app` |
| Còn lại | như trên |

Link: `https://house-price-system.onrender.com` ✅

### A3. Ghi link vào báo cáo

Mở `docs/BAO_CAO_A01.docx` → mục 25 → thay 2 dòng link placeholder bằng:
- `Link: https://heart-disease-system.onrender.com`
- `Link: https://house-price-system.onrender.com`

### Xử lý sự cố Render

| Triệu chứng | Sửa |
|---|---|
| Build fail "Dockerfile not found" | Kiểm tra Root Directory đúng `apps/heart_app` |
| App chạy nhưng 502 đầu tiên | Free tier ngủ — reload lại sau 30 giây |
| `ModuleNotFoundError` | Dockerfile đã `pip install -r requirements.txt` — kiểm tra file tồn tại trong repo |
| Free hết 750h/tháng | 2 app nhẹ, ít truy cập — khó hết |

---

## 🤗 PHƯƠNG ÁN B — HUGGING FACE SPACES (qua Docker SDK)

> Giao diện HF mới đã giấu chọn Streamlit — cách chắc chắn: chọn **Docker** rồi để HF tự build từ Dockerfile mình đã chuẩn bị (nghe port 7860 đúng chuẩn HF).

### B1. Tạo tài khoản + token
1. **https://huggingface.co/join** → đăng ký
2. **https://huggingface.co/settings/tokens** → New token (Write) → copy `hf_xxx`

### B2. Tạo Space kiểu Docker — app bệnh tim
1. **https://huggingface.co/new-space**
2. **Space name:** `heart-disease-system`
3. **Select the Space SDK:** nếu không thấy Streamlit → chọn **Docker** → **Blank**
4. License: mit · Hardware: CPU basic (free) · Public
5. **Create Space**

### B3. Đẩy code bằng git (HF yêu cầu git, upload web từng file cũng được nhưng model 10MB dễ lỗi)

```bash
git clone https://huggingface.co/spaces/TEN-BAN/heart-disease-system
cd heart-disease-system

# copy 4 file từ apps/heart_app/ vào đây
cp /duong-dan/assignment01/apps/heart_app/{app.py,requirements.txt,Dockerfile,heart_model.joblib} .

git add .
git commit -m "init app"
git push
# Username: TEN-BAN | Password: dán token hf_xxx
```

> Dockerfile đã sẵn: EXPOSE 7860 + streamlit run --server.port=$PORT — đúng chuẩn HF Spaces.

### B4. Chờ build ~3–5 phút ở tab Logs, rồi mở tab **App**
Link: `https://TEN-BAN-heart-disease-system.hf.space` ✅

### B5. App giá nhà — lặp lại B2–B4
Space name `house-price-system`, copy 4 file từ `apps/house_app/`.

---

## ✅ Checklist trước khi nộp

- [ ] Mở link bằng trình duyệt ẩn danh — app vẫn chạy
- [ ] Case "Nguy cơ cao" → hiện "CÓ BỆNH TIM"
- [ ] Nhà "cao cấp" → hiện ~$302k
- [ ] 2 link ghi vào mục 25 của `BAO_CAO_A01.docx`
- [ ] (Render) nhớ vào dashboard check 2 app còn Running
