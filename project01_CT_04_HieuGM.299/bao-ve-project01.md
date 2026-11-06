# Chuẩn bị bảo vệ Project01 - Giáp Minh Hiếu, B23DCCN299

## Mở đầu trong khoảng một phút

“Em xây dựng DiaCare theo kiến trúc Hybrid Multiagent System được cung cấp, gồm bảy agent cốt lõi. Nhánh Deep Learning lấy dữ liệu thật qua SQLite, so sánh sáu loại mô hình trên bốn cohort với ba seed, tổng 72 lượt. Nhánh tri thức ingest Web/PDF, có Neo4j, truy xuất RAG và FPT Cloud sinh giải thích có nguồn. Em giữ model CDC/Hospital đã có để đúng yêu cầu tái sử dụng; KG được xây mới vì trước đó em chưa có. Đây là nguyên mẫu học thuật, chưa dùng chẩn đoán hoặc kê đơn.”

## Những con số cần nhớ

| Câu hỏi | Trả lời ngắn |
|---|---|
| Bao nhiêu dataset train? | 4 cohort: CDC, Hospital, Pima, Early Stage |
| Bao nhiêu loại model? | 6: Logistic, RF, HGB, MLP2, MLP3, ResMLP |
| Bao nhiêu model DL? | 3 kiến trúc; seed không tính thành loại mới |
| Bao nhiêu lượt? | 4 × 6 × 3=72;24 tổ hợp dataset-model |
| Bao nhiêu serving artifact? | 4 model đang nạp, một/cohort; CDC/Hospital giữ cũ |
| Bao nhiêu agent? | 7 core; RL tùy chọn nằm ngoài core |
| Corpus? | 12 tài liệu tải thật:11 Web+1 PDF77 trang;4 Web Vinmec |
| Chunk/graph? | 340 chunk gồm 24 thẻ;34 concept;19 quan hệ chuyên môn;2160 MENTIONS |
| Neo4j? | 400 node,2545 edge; đã import/query thật local |
| Dữ liệu Việt? | Có văn bản Việt cho KB, chưa có cohort bệnh nhân Việt để kiểm định DL |

## Câu hỏi về dữ liệu

**1. Vì sao dùng bốn bộ, có gộp không?**  
Để quan sát mô hình trên dữ liệu khảo sát lớn, tái nhập viện và hai cohort nhỏ. Không gộp vì nhãn, feature, quần thể khác nhau. Em so sáu model trong từng bộ, không tạo leaderboard AUC chung.

**2. CDC dự đoán gì?**  
Binary theo nguồn, gộp tiền đái tháo đường/đái tháo đường trong khảo sát. Đây không là chẩn đoán xác nhận và không chỉ riêng type 2.

**3. Hospital có phải dự đoán người bị đái tháo đường không?**  
Không. Người trong dữ liệu đã có đái tháo đường; nhãn là tái nhập viện dưới 30 ngày. Feature tổng kết đợt điều trị phù hợp thời điểm ra viện.

**4. Vì sao CDC còn 226.342, Early còn 251?**  
CDC bỏ nhóm feature có nhãn mâu thuẫn, rồi dedup. Early có 520 dòng với 269 duplicate nên giữ 251 vector trước split; không có conflict. Cách làm ngăn cùng vector lọt train/test.

**5. Vì sao không giữ 520 dòng Early để nhiều dữ liệu hơn?**  
Bản sao không bổ sung thông tin độc lập. Nếu cùng vector qua test, điểm có thể đẹp nhưng không phản ánh tổng quát hóa. Em công bố cả số nguồn và số sạch.

**6. Hospital chống rò rỉ thế nào?**  
Chia theo patient_nbr, cùng người không giao train/validation/test. ID chỉ tạo nhóm, không vào feature hoặc artifact. Chia nhóm chưa phải kiểm định theo thời gian hoặc bệnh viện mới.

**7. Xử lý số 0 Pima ra sao?**  
Năm cột Glucose/BloodPressure/SkinThickness/Insulin/BMI zero-coded được coi missing, median chỉ fit train. Pregnancies 0 vẫn hợp lệ. Không impute bằng toàn bộ tập.

**8. “Từ Database” thể hiện ở đâu?**  
CSV thật được ingest thành bảng raw SQLite, SELECT làm sạch/chia rồi lưu prepared. Mỗi vòng benchmark lấy X/y bằng SELECT split từ bảng prepared. Em có SQL, manifest và hash; không chỉ đổi đuôi NPZ thành database.

**9. Nguồn Pima là UCI hay OpenML?**  
Bản dùng hiện tại là ARFF OpenML37 phân phối nguồn UCI/NIDDK lịch sử, được kiểm toàn bộ giá trị và MD5. UCI34 là bộ time-series khác, không dùng thay. Metadata ghi licence Public, em không tự gán CC0.

**10. Vinmec dùng ở đâu?**  
Bốn bài viết công khai làm văn bản RAG: chế độ ăn, xét nghiệm type 2, tổng quan type 2, thai kỳ. Đây không là dữ liệu bệnh nhân gán nhãn để train DL. PDF kiến trúc không ghi bắt buộc Vinmec; em bổ sung nguồn Việt theo yêu cầu trao đổi.

## Câu hỏi về model và thực nghiệm

**11. Sáu model gồm gì, vì sao chọn?**  
Logistic là baseline tuyến tính; RF/HGB là baseline phi tuyến trên bảng; MLP2/MLP3 so độ sâu; ResMLP khảo sát shortcut residual. Đây là ma trận có lý do so sánh, không tăng số lượng chỉ để đếm.

**12. Có 72 model khác nhau không?**  
Có 72 lần fit,24 tổ hợp dataset-model nhưng chỉ 6 loại. Ba seed đo độ nhạy khởi tạo trên cùng split. Em không đếm seed như architecture mới.

**13. Chọn checkpoint và threshold bằng gì?**  
Checkpoint neural theo validation ROC-AUC; threshold theo maximum validation F 1, rồi đóng băng trước đo test. Test không tham gia fit/chọn checkpoint/ngưỡng/model serving.

**14. Tại sao validation và test riêng?**  
Validation phục vụ lựa chọn trong phát triển, test đo sau lựa chọn. Dùng test để chọn model đẹp nhất sẽ làm đánh giá lạc quan, test không còn độc lập với quá trình chọn.

**15. Vì sao CDC/Hospital không đổi sang model benchmark mới?**  
Đặc tả yêu cầu tái sử dụng DL. Em bảo toàn 11 artifact cũ bằng SHA256; benchmark mới lưu riêng. Pima/Early chưa có model nên chọn DL bằng validation AUC, không theo test.

**16. Có phải DL luôn thắng?**  
Không. Logistic trên Pima rất cạnh tranh; RF trên Early có AUC cao. CDC các model gần nhau; Hospital tất cả còn yếu. Em giữ cả kết quả không thuận lợi.

**17. Tại sao không dùng accuracy chính?**  
Dữ liệu lệch lớp có thể cho accuracy cao khi luôn đoán âm. Em dùng ROC-AUC/AP cùng F 1, sensitivity, specificity, Brier, confusion và prevalence để đọc đầy đủ.

**18. AP khác ROC-AUC thế nào?**  
ROC-AUC dùng TPR/FPR để đo thứ hạng; AP tổng hợp precision theo recall và phụ thuộc prevalence. AP được tính bằng average_precision_score, không gọi là trapezoidal PR-AUC.

**19. Mean ± SD nghĩa gì?**  
Biến thiên ba seed trên cùng split. Không là khoảng tin cậy quần thể hoặc uncertainty đầy đủ cho một người. SD 0 có thể do thuật toán xác định trên cùng dữ liệu.

**20. Vì sao Early AUC cao không kết luận tốt nhất?**  
Task/quần thể khác, test chỉ 38 dòng và đã loại duplicate. Một vài dự đoán đổi là metric đổi mạnh. AUC của Hospital thấp hơn không có nghĩa model kém hơn cho cùng bài toán, vì đây là bài toán khác.

**21. Huấn luyện mất bao lâu?**  
Tổng thời gian fit+evaluate từng run 145,588 giây trên CPU môi trường ghi trong environment.json. Không gồm mọi bước tải/build/test. elapsed 23,449 giây là invocation resume 18 run, không là 72 run.

**22. Sao có resume?**  
Sau 54 run, copy 2 gặp lỗi cập nhật timestamp trên Windows bind-mount khi sao model Pima. Sửa thành copyfile chỉ sao nội dung, kiểm hash/nhãn 54 record rồi chạy 18 run còn lại; không thay thuật toán để cải thiện test.

## Câu hỏi về Knowledge Graph và RAG

**23. Knowledge Graph khác tìm văn bản thế nào?**  
Graph biểu diễn concept và quan hệ có nguồn; tìm văn bản trả chunk liên quan. RAG kết hợp evidence và giải thích. MENTIONS tự động chỉ là xuất hiện concept, không tự là quan hệ y khoa hoặc nhân quả.

**24. Có dùng Neo4j thật không?**  
Có instance localDocker đã import/query seed, kiểm 400 node/2545 edge, import lặp không tăng số và đối chiếu cache. Trên Render, backend thực phải đọc health; thiếu URI accessible thì sqlite_cache/degraded. Em không gọi kiểm local là production graph.

**25.19 relation là ít, sao 2160 MENTIONS?**  
MENTIONS nối chunk-concept theo alias nên nhiều.19 relation chuyên môn có pattern/rule và evidence cụ thể; em giữ distinction để không làm đẹp số graph bằng cách coi mọi cặp concept đồng xuất hiện là tri thức lâm sàng.

**26. Dùng embedding nào?**  
Word/characterTF-IDF và LSA32 bằng TruncatedSVD, không là neural embedding. Hybrid cộng graph boost; mọi variant có prior nhỏ cố định cho thẻ. Đây là lựa chọn gọn, tái lập CPU; neural embedding là hướng mở rộng.

**27. Graph có cải thiện retrieval không?**  
Trên 22 câu phát triển gold thẻ, lexicalR@1=0,9545 và hybrid 0,9091; R@3 cả hai=1. Em không tuyên bố graph thắng. Giá trị hiện tại là cấu trúc thực thể/quan hệ/provenance; cần tập độc lập và retriever tốt hơn để chứng minh cải thiện.

**28. Tám câu Vinmec mới cho kết quả thế nào?**  
Gold kiểm đúng tên tài liệu; lexicalR@3=0,875, hybrid 0,5. Relevant card hoặc tài liệu khác có thể không được gold này chấp nhận. Đây là kiểm hẹp chưa tune, không là benchmark lâm sàng; giữ cả lỗi và giới hạn gold.

**29. FPT làm gì?**  
Explanation Agent gửi câu hỏi, evidence, model output chọn trường và rule tới Chat Completions. Không dùng FPT để train DL và không gửi patient ID. LLM trả JSON answer/citation_ids, qua kiểm cấu trúc và nguồn.

**30. Endpoint/base URL khác nhau?**  
Base là gateway https://mkp-api.fptcloud.com; full URL của route này là https://mkp-api.fptcloud.com/chat/completions. App ưu tiên FPT_API_URL; nếu chỉ BASE thì thêm path. Không tự thêm/v 1 theo ví dụ nhà cung cấp khác.

**31. Citation đúng có bảo đảm câu trả lời đúng không?**  
Không. Validator kiểm ID thuộc evidence và inline khớp danh sách, chưa kiểm ngữ nghĩa từng claim. Muốn đánh giá groundedness cần người thẩm định hoặc pipeline chấm support riêng. Không có evidence thì từ chối, lỗi API thì template có nhãn.

## Câu hỏi về MAS, triển khai và giới hạn

**32. Bảy agent là những agent nào?**  
Data, DL Prediction, Rule-Based, KG/RAG, Coordinator, Explanation, Monitoring. Mỗi agent có trách nhiệm/hợp đồng riêng. Hiện chạy trong một process, chưa là mạng agent phân tán.

**33. Input sai thì sao?**  
Data/API từ chối thiếu/thừa feature, chuỗi/bool, NaN/Infinity, ngoài miền hoặc category lẻ. Có request_id/trace lỗi; DL và các bước phụ thuộc không chạy. Không sinh score mặc định để tiếp tục.

**34. Bất định và xung đột được xử lý thế nào?**  
Report nêu giới hạn và review flags; score gần threshold 0,05 là cờ vận hành, không là ngưỡng y khoa. Model thấp không phủ quyết cảnh báo luật; evidence tổng quát không xác nhận trạng thái cá nhân. Không đủ cơ sở thì yêu cầu human review.

**35. RL học điều trị phải không?**  
Không. Contextual bandit một bước, gamma 0, bốn state/ba action chọn cách trình bày theo rubric synthetic.4.000 episode và 4/4 state chỉ là minh họa; core không cần RL.

**36. Notebook có chỉ gọi file.py không?**  
Mã chạy nằm trực tiếp trong ô và thực thi từ trên xuống. Builder là công cụ bảo trì. Dữ liệu/model/corpus nhúng có provenance; benchmark vẫn fit thật, output riêng không ghi đè artifact serving.

Bản notebook bàn giao đã kiểm 72 lượt fit, 80 kiểm tra ML và 68 kiểm tra API trong kernel mới có cache nguồn thật/hash; đây là phạm vi khác với 102 pytest của ứng dụng.

**37. Render có lưu hồ sơ không?**  
Bản demo không lưu vector/câu hỏi trong audit mặc định; cache chỉ chứa tri thức công khai. AUDIT_LOG_PATH nếu bật chỉ ghi metadata. Đây chưa là hệ thống hồ sơ bệnh án hay quản trị quyền bệnh viện.

**38. Bài còn hạn chế gì?**  
Chưa external/temporal validation, calibration Việt, bộ bệnh nhân Việt, đánh giá claim-level support lớn, benchmark tải/SLA. Hai test nhỏ, graphrule còn đơn giản, corpus nhỏ. Nêu giới hạn là phần thiết kế nghiên cứu, không là điều cần che.

## Demo khoảng năm phút

1. Mở Benchmark: chỉ bốn cohort, sáu model, mean/SD, khác task.
2. Mở Report, chọn CDC, dùng feature mặc định minh họa; chỉ task/version/score/threshold/limitations.
3. Hỏi về chế độ ăn hoặc xét nghiệm; mở evidence Vinmec/PDF và trace bảy agent.
4. Mở Graph: đây là snapshot corpus; chọn relation xem nguồn. Giải thích live query Neo4j và cache khác nhau.
5. Thử thiếu feature hoặc yêu cầu kê liều; chỉ dừng sớm/luật ưu tiên.
6. Chỉ health và generation thực để biết FPT/Neo4j đang bật hay fallback; không tuyên bố live nếu chưa kiểm.

## Khi chưa biết câu trả lời

Nói rõ phần đã đo và phần chưa đo, mở artifact liên quan thay vì đoán. Ví dụ: “Em mới đo ba seed trên một split, chưa có khoảng tin cậy quần thể; kết quả đó nằm ngoài phạm vi hiện tại.” Không hứa kết quả lâm sàng hoặc nói dùng dữ liệu Vinmec train model khi chỉ ingest bài viết.
