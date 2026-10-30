## Mã Python thiết yếu

### Chọn hành động và cập nhật Q

Các trích đoạn dưới lấy từ file reference_core.py của bài làm, phát triển từ Python trong agent02_code.tex. Q có kích thước (2,2,2). Mọi reward thực nghiệm được tạo bằng thực thi; không điền số kỳ vọng thay kết quả lấy mẫu.

```python
{{ACT_CODE}}
```

```python
{{LEARN_CODE}}
```

### Agent theo luật

```python
{{RULE_CODE}}
```

Mã đầy đủ nằm trong code/reference_core.py; điều phối thí nghiệm trong code/agent02_experiment.py; đánh giá common random numbers trong code/evaluation.py; xuất dữ liệu và hình trong code/results_io.py. Notebook đi kèm chứa toàn bộ mã trong một file, tự chạy đủ 31 lượt thí nghiệm từ kernel mới, tạo bảng, Q-table và biểu đồ.
