# Chạy và triển khai DiaCare

## Bản Render đang hoạt động

- [Mở DiaCare](https://diacare-mas-hieugm299.onrender.com)
- [Tài liệu API](https://diacare-mas-hieugm299.onrender.com/docs)
- [Endpoint sẵn sàng](https://diacare-mas-hieugm299.onrender.com/health)
- [Quản lý dịch vụ](https://dashboard.render.com/web/srv-dbm5dfgu01pc738ercq0)

Render xác nhận deploy `dep-dbm5dgou01pc738erfu0` chuyển sang `live` lúc **17:16 ngày 05/11/2026** (giờ Việt Nam). Bộ kiểm tra HTTP trên URL công khai đạt **13/13**, gồm frontend, tài nguyên tĩnh, KB, hai mô hình, nguồn trích dẫn, cảnh báo và dữ liệu nhập không hợp lệ. Xem `results/render-deployment.json` và `results/render-http-verification.json`.

| Cấu hình | Giá trị thực tế |
|---|---|
| Dịch vụ | `diacare-mas-hieugm299` — `srv-dbm5dfgu01pc738ercq0` |
| Workspace | Giáp Minh Hiếu's workspace, đã được người dùng xác nhận |
| Runtime / gói / vùng | Docker / Free / Singapore |
| Repository / nhánh | `https://github.com/HieuGM/PTHTTM_PTIT` / `main` |
| Commit đã kiểm tra | `6eb79dc0468bc76347b10c2ef0ab1a360974686a` |
| Root Directory | Để trống, tức gốc repository |
| Dockerfile Path | `project01_CT_04_HieuGM.299/Dockerfile` |
| Docker Build Context | `project01_CT_04_HieuGM.299` |
| Biến môi trường | `APP_DATA_DIR=/tmp/diacare`, `OMP_NUM_THREADS=2`, `PORT=8000` |
| Tiến trình | Một worker Uvicorn, bind `0.0.0.0:8000` |
| Kiểm tra sẵn sàng của Render | TCP mặc định; endpoint HTTP `/health` đã được kiểm tra riêng |

Dịch vụ được tạo trực tiếp qua MCP. Blueprint `render.yaml` ở gốc repo mô tả phương án quản lý bằng cấu hình, trong đó dùng `rootDir: project01_CT_04_HieuGM.299` và các đường dẫn Docker tương đối với thư mục đó. Không coi Blueprint là cấu hình đã được áp dụng cho dịch vụ hiện tại. Không tạo thêm dịch vụ trùng tên nếu chỉ cần cập nhật bản đang chạy.

Gói Free có thể ngủ khi không có truy cập; lần mở lại có thể chậm. Ứng dụng không cần GPU, LLM hay API key để phục vụ demo. SQLite được dựng lại từ KB JSON khi khởi động, không cần persistent disk và không lưu câu hỏi hoặc hồ sơ sức khỏe.

Kiểm tra lại URL thực tế từ thư mục project:

```powershell
python scripts/verify-deployment.py --url https://diacare-mas-hieugm299.onrender.com --output results/render-http-verification.json
```

Các kết quả đo là kiểm tra chức năng của lần deploy này, không phải kiểm tra tải hoặc cam kết thời gian hoạt động. Workspace từng chạm giới hạn số dịch vụ; người dùng đã tự xóa một dịch vụ cũ để giải phóng hạn mức. Các dịch vụ cũ khác không được thay đổi trong lượt deploy DiaCare.

## Chạy Docker cục bộ

Từ thư mục chứa Dockerfile:

```powershell
docker build -t diacare-hieugm299:1.0 .
docker run -d --name diacare-demo -p 127.0.0.1:8000:8000 diacare-hieugm299:1.0
Invoke-RestMethod http://localhost:8000/health
```

Mở http://localhost:8000. Image kèm trọng số, KB và policy, không cần tải dữ liệu hay train lại lúc chạy. Image chạy dưới user không phải root; SQLite sinh lại tại `/tmp/diacare`. Docker healthcheck kiểm tra cổng 8000 nên cấu hình Render hiện tại cũng đặt `PORT=8000`.

Bản container Linux đã kiểm tra bằng Docker Engine 29.9.2 trong WSL2 riêng: 55/55 pytest, HTTP 13/13 và healthcheck healthy. Bằng chứng ở `results/docker-verification.json`. Bản kiểm tra trên máy có thể mở tại http://localhost:8012 khi distro `codex-diacare-261105` và container `diacare-verified` đang chạy.

Docker Desktop gốc từng gặp lỗi I/O khi ổ C đầy, sau đó đã khởi động lại và phản hồi Engine 29.6.1. Bản kiểm chứng dùng engine riêng trên ổ D; không sửa hoặc xóa VHD, image cũ.

Để dừng container do lệnh trên tạo: `docker stop diacare-demo`. Để chạy lại: `docker start diacare-demo`.

## Cập nhật và vận hành

Service đang bật auto-deploy theo nhánh `main`. Sau khi push thay đổi ứng dụng, theo dõi deploy mới trên Dashboard, đợi trạng thái `live`, rồi chạy lại kiểm tra HTTP. Với thay đổi chỉ liên quan tài liệu, có thể dùng commit message chứa `[skip render]` để tránh build lại không cần thiết.

Một worker giúp tránh nhân đôi model và index. `OMP_NUM_THREADS=2` giới hạn thread CPU. Nếu mở cho nhiều người dùng, cần theo dõi RAM/CPU, bổ sung rate limiting ở proxy và kiểm tra chính sách log của nhà cung cấp. Chưa có benchmark tải hoặc SLA.

Tham khảo: [Render Blueprint](https://render.com/docs/blueprint-spec), [Render Deploys](https://render.com/docs/deploys), [FastAPI Docker](https://fastapi.tiangolo.com/deployment/docker/).
