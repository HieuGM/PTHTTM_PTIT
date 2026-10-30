## Quan sát quá trình học

### Thí nghiệm B Reward theo cửa sổ

![Lợi nhuận RL theo cửa sổ 100 episode không chồng lấp của năm seed](../results/baseline.png)

Đường thể hiện trung bình của seed 11, 22, 33, 44, 55. Mỗi điểm tổng hợp 100 episode, tức 2.000 bước cho từng seed. Vùng tô là ±1 SD mẫu giữa seed. Cách tính cho một cửa sổ: tổng reward của 100 episode chia (100 × 20), sau đó lấy trung bình giữa seed.

Với baseline seed 42, trung bình 100 episode đầu là **31,9210**, 100 episode cuối là **33,5690**. SD reward mỗi episode sau khi chia 20 ở 1.000 episode cuối là **5,2144**. Đây là độ dao động theo episode của một lượt chạy, khác SD giữa seed. Số cuối cao hơn số đầu 1,6480; quan sát này phù hợp với cải thiện trong lượt chạy đó nhưng chưa chứng minh hội tụ hay tổng quát hóa.

### Reward tích lũy và cách diễn giải

Tổng reward tích lũy cuối huấn luyện là 3.345.548 cho RL và 3.283.930 cho đối thủ luật. Chuỗi đầy đủ được tính bằng tổng lũy kế reward từng episode; đồ thị bổ sung lưu ở results/baseline-cumulative.png và dữ liệu gốc trong baseline-seed-42-training.csv.

Tổng tích lũy tăng vì reward trong cấu hình chuẩn không âm; chỉ một đường tích lũy tăng chưa chứng minh agent học tốt hơn. Cần xem độ dốc và reward/bước cùng đánh giá đóng băng. Training RL đạt 33,45548, còn greedy evaluation 34,91850; khác biệt vừa liên quan exploration vừa liên quan Q thay đổi và mẫu đánh giá, không thể quy toàn bộ cho một nguyên nhân từ một lần đo.
