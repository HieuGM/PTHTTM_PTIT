# CHƯƠNG 5. KNOWLEDGE BASE VÀ TRUY XUẤT TĂNG CƯỜNG TRẢ LỜI

## 5.1. Xây dựng Knowledge Base

KB gồm 24 thẻ biên soạn bằng tiếng Việt, dựa trên 19 URL từ WHO, NIDDK, CDC, NHS và nguồn chuyên môn Việt Nam. Mỗi thẻ chứa id, title, text, topics, source_title, url và retrieved_at. Văn bản là phần tóm tắt phục vụ học tập; không sao chép nguyên sách hoặc tự nhận đã đọc hướng dẫn điều trị đầy đủ nếu mới xác minh trang giới thiệu.

Các nhóm nội dung gồm khái niệm, típ 1/típ 2/thai kỳ, triệu chứng, yếu tố nguy cơ, xét nghiệm, HbA1c, phòng ngừa, dinh dưỡng, vận động, thuốc, hạ đường huyết, nhiễm toan ceton, theo dõi, biến chứng, bàn chân, thận, mắt, tài liệu Việt Nam và nguồn dữ liệu mô hình. Mã thẻ cho phép kiểm tra đầu ra đang dùng đúng văn bản nào, nguồn nào và ngày thu thập nào.

Kho thẻ đặt trong app/knowledge/cards.json là nguồn có kiểm soát phiên bản. Khi khởi động, ứng dụng đồng bộ các thẻ sang SQLite để minh họa thành phần DB của kiến trúc và phục vụ kiểm kê. Tài liệu không được tải tự động lại từ web trong mỗi câu hỏi; khả năng cập nhật phụ thuộc việc rà soát phiên bản KB. retrieved_at không đồng nghĩa tài liệu còn là phác đồ mới nhất cho mọi trường hợp.

## 5.2. Quy trình truy xuất

Câu hỏi và văn bản thẻ được chuyển về chữ thường, bỏ dấu để giảm khác biệt khi người dùng gõ tiếng Việt không dấu, giữ chữ số để phân biệt típ 1 và típ 2. TF-IDF dùng unigram và bigram, sublinear term frequency. Vector thẻ được chuẩn hóa L2; tích vô hướng giữa vector câu hỏi và thẻ tương ứng độ tương đồng cosine trong không gian này.

Mỗi request lấy tối đa ba thẻ có điểm từ 0,09 trở lên. Ngoài ngưỡng điểm, một kiểm tra phạm vi chủ đề giúp hạn chế câu hỏi hoàn toàn không liên quan. Ngưỡng và từ khóa là tham số kỹ thuật của demo, chưa được tối ưu trên tập kiểm định độc lập. Điểm tương đồng không là xác suất câu trả lời đúng và không tự chứng minh câu hỏi có thể trả lời.

TF-IDF phù hợp với KB nhỏ, chạy CPU và không cần tải embedding lớn. Hạn chế chính là phụ thuộc từ vựng, nhạy với cách diễn đạt và không suy luận được câu hỏi đa bước. Có thể nghiên cứu dense retrieval, reranking và GraphRAG ở bước sau, nhưng phải đo cùng giao thức và bộ câu hỏi tách riêng để đánh giá lợi ích.

## 5.3. Tạo câu trả lời dựa trên bằng chứng

Sau truy xuất, PolicyAgent chọn abstain, brief hoặc detail. Với brief, EducationAgent lấy một thẻ; detail có thể lấy hai thẻ. Văn bản được ghép trực tiếp với mã nguồn dạng [KBxx], sau đó danh sách URL đi kèm để người dùng mở tài liệu. CriticAgent kiểm tra ID thuộc KB và URL dùng HTTPS trước khi Coordinator trả kết quả.

Đây là pipeline truy xuất tăng cường trả lời theo hướng trích xuất. Bản chạy mặc định không có LLM, không fine-tune và không đo chất lượng sinh văn bản của mô hình ngôn ngữ. Vì vậy kết quả có nguồn không được trình bày như đánh giá một hệ RAG sinh tự do. Cách trích xuất giảm nguy cơ tự tạo claim mới nhưng vẫn có thể chọn sai thẻ hoặc trả lời quá tổng quát.

Quan hệ với RAG nằm ở nguyên tắc lấy bằng chứng bên ngoài thành phần trả lời, giữ thông tin nguồn và kiểm soát khi không đủ chứng cứ. Muốn chuyển sang generation bằng LLM cần bổ sung provider, prompt chỉ dùng context, kiểm tra claim–citation, xử lý prompt injection, chi phí và bộ đánh giá khác. Những thành phần đó chưa là kết quả thực nghiệm của project.

## 5.4. Đánh giá truy xuất và khả năng trả lời

Bộ phát triển có 30 câu tự biên soạn: 22 câu có nguồn mong đợi, 8 câu yêu cầu tính liều/kê đơn, dữ liệu thời gian thực, nội dung ngoài lĩnh vực hoặc bịa bằng chứng. Mỗi câu có expected_ids, answerable và kind. Bộ này là kiểm thử chức năng nhỏ được dùng trong quá trình phát triển, không phải benchmark độc lập, kiểm định chuyên gia y tế hoặc bằng chứng an toàn lâm sàng.

| Phép đo | Kết quả | Mẫu số và ý nghĩa |
|---|---|---|
| Recall@1 | 21/22 = 95,45% | Nguồn mong đợi đứng đầu với câu có đáp án |
| Recall@3 | 22/22 = 100% | Nguồn mong đợi nằm trong top 3 |
| MRR@3 | 0,97727 | Trung bình nghịch đảo hạng nguồn đúng |
| Quyết định trả lời/từ chối | 30/30 | Phân loại khả năng trả lời trên bộ phát triển |
| Từ chối câu âm | 8/8 | Gồm cả rule boundary và thiếu bằng chứng |
| Nguồn mong đợi được trích trong câu trả lời | 21/22 | Khác Recall@3 vì brief chỉ chọn một thẻ |

Ở Q22 về tiền đái tháo đường, KB24 nằm hạng 2 nhưng câu trả lời ngắn chọn KB01 tổng quát ở hạng 1. Truy xuất top 3 thành công không bảo đảm phần trả lời dùng nguồn cụ thể nhất. Lỗi này được giữ trong system-evaluation.json và báo cáo để tránh đồng nhất chất lượng truy xuất với chất lượng câu trả lời.

Các giá trị trên có thể tăng cao vì corpus nhỏ và câu hỏi được viết sau khi biết phạm vi KB. Chưa có đánh giá người dùng, nhiều cách viết không dấu/lỗi chính tả, câu hỏi dài có phủ định phức tạp, đa bệnh hoặc xung đột tài liệu. Những hạn chế đó quan trọng hơn việc làm tròn chỉ số thành 100%.

## 5.5. Ví dụ tương tác

Câu hỏi “HbA1c là gì?” đi qua kiểm tra phạm vi, truy xuất thẻ xét nghiệm, chọn brief và trả đoạn tóm tắt cùng nguồn NIDDK. Câu hỏi về điều chỉnh liều insulin dừng ở SafetyAgent, không chạy nhánh giáo dục thông thường. Câu hỏi về cổ phiếu hoặc địa chỉ phòng khám đang mở cửa không được thay bằng một đoạn y tế bất kỳ chỉ vì có vài từ trùng.

Khi không có bằng chứng, ứng dụng trả trạng thái insufficient_evidence và nêu phạm vi hiện có. Khi yêu cầu vượt phạm vi, trạng thái boundary đi kèm lý do trong trace. Nhờ phân biệt các trạng thái này, người dùng và người chấm có thể quan sát lý do hệ thống dừng thay vì chỉ nhìn một câu trả lời cuối.
