## Tách huấn luyện và đánh giá trong mã

### Môi trường và reward

Đây là phần tính chuyển đổi, doanh số và lợi nhuận từ phương thức step của môi trường. Hai hành động đã được chọn trước khi gọi step.

```python
{{REWARD_CODE}}
```

### Nguồn ngẫu nhiên chung khi đánh giá

```python
{{TAPE_CODE}}
```

Mỗi khách hàng có một uniform độc lập; khách mua khi uniform < p. Với N khách, tổng số lần mua có luật Binomial(N,p). Trong các trận riêng, giữ cùng uniforms cho cùng vai trò và cùng demand giúp chênh lệch ít bị nhiễu hơn. Hai người bán vẫn có uniforms riêng, không nhận doanh số giống hệt nhau chỉ vì cùng p.

Hàm evaluate tạo đối thủ luật mới, đặt lịch sử về [0,0] mỗi episode, dùng argmax từ Q đã học, ghi từng reward và đếm hành động. Không có lời gọi learn trong hàm này; cuối hàm kiểm tra Q trước và sau giống hệt nhau. CSV/JSON lưu tổng reward, reward/bước, số bước, số hành động và reward theo episode để kiểm tra lại phép cộng.

### Cách chạy và kiểm chứng

```text
python -m pip install -r requirements.txt
python code/agent02_experiment.py
python code/test-experiment.py
python notebook/build-notebook.py
python report/assemble-report.py
python report/render-report.py
```

Các lệnh chạy từ thư mục agent02. Chương trình benchmark chạy đủ 31 lượt; notebook cũng chứa toàn bộ mã và chạy đủ 31 lượt, không cần file Python, JSON hay hình có sẵn bên ngoài. Python {{PYTHON_VERSION}}, NumPy {{NUMPY_VERSION}} trên Windows là môi trường đã thực thi. Phiên bản cụ thể của các gói được lưu trong results/environment.json.
