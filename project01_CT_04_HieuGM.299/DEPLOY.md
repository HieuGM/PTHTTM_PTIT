# Chạy và triển khai DiaCare

## Bản Docker

Từ thư mục chứa Dockerfile:

```powershell
docker build -t diacare-hieugm299:1.0 .
docker run -d --name diacare-demo -p 127.0.0.1:8000:8000 diacare-hieugm299:1.0
Invoke-RestMethod http://localhost:8000/health
```

Mở http://localhost:8000. Trọng số, KB và policy có sẵn; không cần GPU/LLM/APIkey. Image chạy dưới user không phải root; SQLite sinh lại tại `/tmp/diacare`. Docker healthcheck dùng cổng8000 mặc định. Khi đặt PORTkhác, nền tảng cloud nên kiểm tra `/health` trên cổng được cấp.

Bản kiểm tra thực đã build từ Dockerfile này và chạy trên Docker Engine29.9.2 trong WSL2 riêng: HTTP13/13đạt, healthcheck healthy. Bằng chứng ở `results/docker-verification.json`. Trên máy hiện tại, bản đã chạy có thể mở tại http://localhost:8012 khi distro `codex-diacare-261105` và container `diacare-verified` đang hoạt động. Docker Desktop gốc từng gặp lỗi I/O khi ổ C đầy, sau đó đã phản hồi lại Engine29.6.1 khi ổ có dung lượng và khởi động lại. Bản kiểm tra dùng engine riêng trên ổ D; không sửa/xóa VHD hoặc image cũ.

Để dừng bản do mình khởi tạo: `docker stop diacare-demo`. Để chạy lại: `docker start diacare-demo`. Tên container khác nhau cần dùng tên đúng theo `docker ps`.

## Render

1. Tạo repository riêng chứa **nội dung bên trong** thư mục project này, Dockerfile ở root. Không đưa cả workspace học tập hoặc dữ liệu gốc lên repository.
2. Kết nối repository với Render, chọn Blueprint `render.yaml`, hoặc tạo WebService với runtimeDocker và healthcheck `/health`.
3. Cấu hình đã ghi `plan: free`; kiểm tra thông tin gói/tài nguyên trong giao diện trước khi tạo. Không chuyển sang gói trả phí nếu chưa chủ động chọn.
4. Ứng dụng đọc biến PORTdo Render cấp; APP_DATA_DIRdùng `/tmp/diacare`. Không cần thêm secret.
5. Đợi deploy xong và kiểm tra `/health`, hỏi đáp HbA1c, cảnh báo glucose, phân tích CDC và Hospital. Dùng `python scripts/verify-deployment.py --url https://TEN-SERVICE.onrender.com` để lưu bằng chứng HTTPthực của endpoint.

Freeinstance có thể ngủ hoặc có giới hạn tài nguyên. Chỉ có thể kết luận URLcloud hoạt động sau khi deploy và kiểm tra thật. Hiện tại đã kiểm tra containerLinux cục bộ; chưa tạo servicecloud hoặc URLcông khai trong phiên này.

`render.yaml` dành cho repositoryriêng nói trên. Nếu đặt project trong monorepo, cần thêm `rootDir: project01_CT_04_HieuGM.299` và chỉnh context/path Docker theo cấu trúc repositorythực tế, hoặc dùng giao diện tạo service với RootDirectorytương ứng.

Tham khảo chính thức: [Render Blueprint](https://render.com/docs/blueprint-spec), [FastAPI Docker](https://fastapi.tiangolo.com/deployment/docker/).

## Tài nguyên và vận hành

Một workergiúp tránh nhân bản hai mô hình và index. OMP_NUM_THREADS=2giới hạn CPUtrong container. Không có kiểm tra tải công khai hoặc SLA. Nếu cho nhiều người dùng truy cập, cần theo dõi RAM/CPU, thêm rate limiting ở lớp proxyvà xem chính sách logcủa nhà cung cấp để tránh thu thập dữ liệu nhập ngoài chủ đích.
