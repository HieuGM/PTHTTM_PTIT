## Kết quả baseline và đánh giá policy

### Câu 6 Tính reward trung bình

Baseline huấn luyện 100.000 bước, seed 42. RL thu tổng 3.345.548, trung bình **33,45548 mỗi bước**; đối thủ luật thu 3.283.930, trung bình **32,83930**. Trong huấn luyện RL còn exploration và Q còn thay đổi, vì vậy các số này không đại diện trực tiếp cho chất lượng policy greedy cuối cùng.

| Giai đoạn và agent | Tổng reward | Số bước T | Reward/T | Không giảm / giảm |
|---|---|---|---|---|
| Training RL | 3345548 | 100000 | 33,45548 | 82476 / 17524 |
| Training đối thủ luật | 3283930 | 100000 | 32,83930 | 91677 / 8323 |
| Eval RL trong RL-vs-rule | 349185 | 10000 | 34,91850 | 10000 / 0 |
| Eval đối thủ trong RL-vs-rule | 349315 | 10000 | 34,93150 | 10000 / 0 |
| Eval luật trong rule-vs-rule riêng | 349185 | 10000 | 34,91850 | 10000 / 0 |

Phép tính ví dụ: R_RL_eval = 349185 / (500 × 20) = **34,9185**. Đối thủ trong cùng trận nhận 34,9315 vì có chuỗi Bernoulli khác; không dùng chênh lệch này làm so sánh cùng vai trò. So sánh công bằng ở vai trò focal là **RL 34,9185 và luật 34,9185**, trong hai trận riêng với cùng nguồn ngẫu nhiên.

### Q table và policy sau baseline

{{Q_TABLE}}

Hai trạng thái có c = 1 chọn giảm giá, nhưng trong đánh giá episode bắt đầu lịch sử [0,0], RL chọn 0 ở cả hai trạng thái c = 0 và luật không tự khởi phát giảm giá. Do đó các trạng thái c = 1 không xuất hiện trên quỹ đạo này. Policy ghi trong bảng khác policy luật ở một số trạng thái, nhưng hành động thực tế của hai policy vẫn giống nhau.

Khi cả hai luôn chọn 0, lợi nhuận kỳ vọng mỗi bước = 0,5 × 15 + 0,5 × 55 = **35**. Số đo 34,9185 gần giá trị này nhưng không phải bằng chứng hội tụ. Nhiều seed cho biết độ nhạy khởi tạo và nhiễu; phạm vi vẫn giới hạn trong simulator và ngân sách đã chọn. Bảng nhiều seed được trình bày ở phần learning rate và exploration.
