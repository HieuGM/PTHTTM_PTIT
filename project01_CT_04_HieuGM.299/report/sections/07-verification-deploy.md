# CHƯƠNG 7. TÁI LẬP, NOTEBOOK, KIỂM THỬ VÀ TRIỂN KHAI

## 7.1. Notebook là lối chạy chính

Notebook chứa mã trực tiếp trong ô, chạy từ trên xuống trong kernel mới, không import module Python cục bộ của project. Script builder chỉ dùng bảo trì. Luồng gồm môi trường, schema/nguồn, CSV→SQLite→SELECT, benchmark/biểu đồ, serving model tái sử dụng, KB/graph/RAG, bảy agent, demo/API.

Bản 2.1 nhúng thêm source adaptive retrieval, output review và registry trước các module sử dụng chúng. Các ô demo/API kiểm attempts, budget, quality, timing và feature_usage. Kết quả thực thi mới lưu riêng tại results/notebook-agent-upgrade-verification.json; không dùng số ô hoặc output cũ để khẳng định notebook mới đã chạy.

Full chạy ngân sách đầy đủ; smoke giảm seed/epoch/cây để kiểm luồng, không thay số đo full. Output ở thư mục riêng, không ghi đè serving model hoặc báo cáo. Dữ liệu tải thật/cache phải có provenance; model nhúng để reuse không thay việc fit benchmark trên nguồn thật.

## 7.2. Tái chạy bằng module khi bảo trì

Các lệnh dưới tương đương thao tác trong notebook, dùng khi phát triển ứng dụng. Chạy từ thư mục Project01; không bắt buộc người học chạy chúng để xem notebook.

```powershell
python scripts/prepare-database.py
python scripts/run-benchmark.py --mode full --seeds 42 43 44 --reuse-prepared-db
python scripts/ingest-knowledge.py --help
python scripts/load-neo4j.py --help
python -m compileall -q app scripts tests report
python -m pytest tests -q
```

Ingestion/Neo4j dùng thông tin kết nối môi trường; không đặt key/password trực tiếp trong câu lệnh được đưa lên Git. Refit cây cần cùng dữ liệu, preprocessing, seed và config. Phiên bản thư viện hoặc nền tảng khác có thể làm sai số số học và thời gian thay đổi.

## 7.3. Các lớp bằng chứng

Kiểm mô hình cần tính lại metric từ y/score, kiểm hash weights, threshold validation, scaler train-only, split/nhóm không giao và bảo toàn serving model cũ. Kiểm MAS cần request_id, thứ tự agent, dừng sớm, lỗi dependency, báo cáo và không ghi dữ liệu nhạy cảm. Kiểm KG cần import/query Neo4j thật, counts, idempotence, provenance và cache parity.

Kiểm notebook cần chạy kernel mới trong thư mục không có source app; không chỉ kiểm JSON hoặc syntax. Kiểm Docker cần build đúng source cuối, gọi API/model/KB và kiểm health. Kiểm public cần chờ deploy live rồi gọi HTTPS, đối chiếu version/commit; việc localhost đạt không thay bằng chứng public.

55/55 pytest và 13/13 HTTP ghi ngày 05/11/2026 là bằng chứng lịch sử phiên bản đầu. Bộ 30 câu phát triển và 11 ca an toàn lịch sử không phải bộ clinical validation. Bản nâng cấp thay schema, retrieval, API và UI nên cần kết quả kiểm tra mới; đối chiếu file verification mới nhất khi nộp.

Bản 2.0 đạt 102 pytest ở lượt kiểm ngày 06/11. Kiểm độc lập tính lại 72 run/144 bộ metric, 36 checkpoint, 24 summary và 11 hash legacy. Bằng chứng lịch sử nằm tại results/pytest-verification-v2.json; lượt kiểm code 2.1 được ghi riêng trong agent-upgrade-pytest.json.

Bản 2.0 đã kiểm giao diện desktop/mobile với 24 kiểm tra, gồm bốn form, benchmark, graph, metadata, chat và năm tab. Footprint khoảng 302 MiB chỉ áp dụng môi trường lượt đó. Notebook 2.0 có 61 ô/51 ô mã/25 mô-đun inline; lượt full dùng cache nguồn thật đạt 72 fit, 80 kiểm tra ML và 68 kiểm tra API trong 211,575 giây. Lượt tải nguồn trước đó mất 339,18 giây. Đây là bằng chứng lịch sử trong notebook-verification.json, không thay cho việc chạy notebook 2.1; cũng không thay tổng fit từng run 145,588 giây của benchmark báo cáo.

## 7.4. Docker và cấu hình FPT

Image chứa model/corpus và không train tại startup. Một worker Uvicorn hạn chế nhân bản bộ nhớ; OMP_NUM_THREADS=2 giới hạn CPU thread. SQLite cache dựng lại dưới APP_DATA_DIR=/tmp/diacare. Raw/database và notebook-output không trong image.

FPT_API_KEY, FPT_MODEL và FPT_API_URL cấu hình bằng biến môi trường. Gateway AI Marketplace đã kiểm endpoint HTTPS https://mkp-api.fptcloud.com/chat/completions. FPT_BASE_URL là lựa chọn thay thế; full URL được ưu tiên. Key thật không xuất hiện trong notebook/PDF/repository. HTTP 200 xác nhận kết nối chưa đủ để chứng minh câu trả lời grounded; cần thêm kiểm citation/evidence của output thật.

## 7.5. Render và trạng thái phiên bản

Demo tại https://diacare-mas-hieugm299.onrender.com, API docs tại /docs và readiness tại /health. Dịch vụ hiện có dùng Docker Free Singapore, repo HieuGM/PTHTTM_PTIT nhánh main, service `srv-dbm5dfgu01pc738ercq0`. Root Directory trống; Dockerfile và build context trỏ thư mục `project01_CT_04_HieuGM.299`.

Bản 2.0 chuyển live lúc 14:40:42 ngày 06/11/2026 theo giờ Việt Nam, commit `1d08d9ba7bc1d757ee856268f671ca035399a7b8`, deploy `dep-dbmo7ne7bikc73bj5rv0`. Kiểm public lượt đó đạt 30/30, gồm suy luận bốn model, corpus/graph/benchmark và sinh câu trả lời FPT thật. Lượt trước đạt 29/30 vì một câu FPT dùng template fallback; giữ nguyên tại results/render-http-attempts.json. Đây là kiểm chức năng lịch sử, không bảo đảm LLM luôn thành công hoặc chứng minh code 2.1 đã được phát hành. Kết quả ở results/render-http-verification.json, metadata ở render-deployment.json; khi demo cần đọc system_version từ /health của chính môi trường đang dùng.

Dịch vụ dùng public Git URL nên cần manual deploy theo commit mới sau push; deploy do đổi environment ở commit cũ không được tính là bản nâng cấp. FPT Environment đã cấu hình riêng trên Render, không ship .env. Free có thể ngủ; lần mở đầu chậm không tự chứng minh lỗi model.

Neo4j Docker cục bộ không truy cập từ Render bằng localhost. Muốn live graph production cần URI accessible và credential riêng; khi thiếu dùng sqlite_cache/degraded có nhãn. Không tạo thêm tài nguyên trả phí. Live của ứng dụng không chứng minh đã có Neo4j production hoặc kiểm định lâm sàng.

### 7.5.1. Bản mã 2.1 được kiểm chứng công khai

Bản 2.1 đã live lúc 11:26:33 ngày 13/11/2026 trên chính dịch vụ Free hiện có, từ commit `bc67a979d74db02195ed2b9d927cb59d63c3c7fb`, deploy `dep-dbr926lg1s2s73fpu7qg`. Sau khi trạng thái deploy là live, 39/39 phép kiểm HTTPS đạt: phiên bản mới, bốn model, quality/duration, capabilities, retry thật và từ chối câu ngoài miền. Ca CDC sinh bằng FPT thật; ca “Mờ mắt là gì?” gọi truy xuất hai lượt và cũng có final generation=fpt_cloud_llm. Neo4j public vẫn là sqlite_cache có nhãn. Bằng chứng mới ở render-agent-upgrade-deployment.json và render-agent-upgrade-http.json; không suy từ Git push hoặc localhost.

Một lượt kiểm FPT cục bộ sau sửa đã chuyển sang template vì ValueError khi xử lý phản hồi; giữ nguyên tại provider-review-verification.json. Lượt trước đó có phản hồi FPT hợp lệ được giữ riêng với nhãn before-review-fix. Các ca public sau deploy cho thấy dịch vụ có thể sinh thật, nhưng không bảo đảm mọi request LLM thành công. Cả fallback và generation được ghi theo đường đi thực tế. Đợt này cập nhật mã của dịch vụ cũ, không tạo tài nguyên trả phí mới.

## 7.6. Kịch bản demo bảo vệ

Mở bảng benchmark, chọn lần lượt bốn cohort và giải thích khác nhiệm vụ. Trên report, chọn CDC và feature mặc định minh họa; đọc task, score, threshold, version. Nhập câu hỏi về chế độ ăn hoặc xét nghiệm, mở evidence Vinmec/PDF và trace để chỉ ra KG/RAG/Explanation.

Thử thiếu feature hoặc nhập ngoài miền: Data từ chối trước DL. Thử yêu cầu kê liều: luật giới hạn phản hồi. Tắt FPT hoặc Neo4j có chủ đích trong môi trường cục bộ để xem nhãn fallback; không giả định fallback chính là dịch vụ ngoài đang chạy. Khi demo LLM thật, dùng câu hỏi công khai và không cung cấp hồ sơ nhận dạng.

Với code 2.1, mở tab Công nghệ và kiểm chứng hoặc /api/capabilities, chỉ source symbol của một phương pháp rồi chạy request tương ứng. So “HbA1c phản ánh điều gì?” với “Mờ mắt là gì?” để xem dừng ngay hoặc alias_rewrite có lý do. Mở mục 6 của report để xem retrieval/quality và feature_usage. Câu bóng đá cho thấy nhánh thiếu evidence; các test draft có nhãn minh họa sửa output khi không thể cố ý điều khiển phản hồi của LLM thật.

## 7.7. Hướng phát triển

Ưu tiên bộ câu hỏi độc lập có thẩm định chuyên môn, đánh giá claim-level support, nguồn mới và prompt injection; so sánh retriever với neural embedding phù hợp tiếng Việt. Với ML, thêm external/temporal validation, calibration và phân tích nhóm. Với hệ thống, đo tải/RAM/latency/cost, rate limit và hạ tầng log có chính sách rõ.

Không mở rộng số model chỉ để tăng số lượng khi chưa có giả thuyết so sánh. Ma trận hiện tại hữu hạn, có baseline và ba neural architecture, cho thấy cả kết quả tốt và yếu. Giá trị của bài là pipeline tái lập, không rò rỉ, provenance và ranh giới nghiên cứu được thể hiện trong sản phẩm.

## 7.8. Kiểm chứng phần nâng cấp mã 2.1

Lần bổ sung tài liệu ngày 12/11/2026 giữ runtime và notebook cũ, đạt 102 pytest cùng 8 ca minh họa; các file resubmission-* là ảnh chụp bằng chứng của giai đoạn đó. Sau yêu cầu nâng cấp mã, bản 2.1 thêm controller truy xuất, reviewer, timing, registry và UI. Hai giai đoạn được tách để tránh dùng bằng chứng “không đổi mã” cho một bản đã đổi hành vi. Bìa và các trọng số serving được bảo toàn.

<!-- UPGRADE_EVIDENCE_START -->

Đợt kiểm chứng mã nâng cấp hoàn tất ngày 13/11/2026. Các kết quả dưới đây được ghi riêng với đợt bổ sung tài liệu trước đó.

| Bằng chứng của mã nâng cấp | Kết quả | Phạm vi |
|---|---|---|
| Pytest | 156 đạt, 0 lỗi | Model thật/cache/template và ca lỗi có chủ đích |
| API minh họa | 10/10 đạt | Bốn cohort, safety, input sai, retry và từ chối |
| Notebook | 72 fit, 80 ML, 99 API, 37 kiểm tra nâng cấp | Kernel mới; weights sandbox tách artifact phục vụ |
| FPT thật | Structured response: False; final generation: template | Một câu hỏi công khai, không phải benchmark y khoa |
| Review cuối của lượt FPT | True | Chỉ các điều kiện của bộ kiểm xác định |
| Nguồn công nghệ | technology-map.json | Mỗi tính năng có file/hàm/dòng; phân biệt implemented và executed |

Lượt notebook mới ghi riêng môi trường, source/hash và số kiểm tra trong verification. Các model Pima/Early được chọn lại trong thư mục sandbox của notebook; trọng số phục vụ trong gói nộp và số benchmark lịch sử không bị thay. Một lượt full đã dừng khi review phát hiện lỗi xử lý xuống dòng; lượt đó không được tính là hoàn tất.

Rà soát độc lập phát hiện bản sửa extractive có thể ghép những mảnh xuống dòng thành một phát biểu không đạt kiểm tra. Bản cuối kiểm lại đoạn đã ghép và chuyển sang REFUSAL tin cậy nếu candidate sau sửa vẫn bị từ chối; verdict của candidate lỗi được giữ trong metadata. Đây là sửa lỗi trong cơ chế kiểm duyệt, không là chứng minh an toàn y tế tổng quát.

<!-- UPGRADE_EVIDENCE_END -->

Các test mới kiểm provenance giả, retrieval lỗi/rỗng và trần số call; draft sai nguồn/chẩn đoán/liều; không sửa draft đạt; số lượt revision; metadata timing; feature_usage và source symbol của registry. Predictor cũng từ chối khi thứ tự feature trong metadata không khớp schema. Các sự cố hoặc draft không an toàn được chủ động tạo là ca kiểm thử có nhãn, không phải sự cố production hay output FPT được quan sát.

Mã bảy agent vẫn hữu hạn, nhưng KG/RAG tự quyết định có cần lượt tiếp theo và Explanation tự quyết định nhận/sửa/từ chối trong ngân sách. Đây là cải tiến về hành vi và khả năng quan sát. Bảng ở 5.11 cho thấy bộ lọc có thể giảm Recall; các số kiểm chức năng không được diễn giải thành độ đúng y khoa hoặc thắng lợi retrieval tổng thể. Bằng chứng FPT/Neo4j/Render ngày 06/11 giữ nguyên ngày và phạm vi.

## 7.9. Giao diện và quan sát luồng phối hợp

Các ảnh sau được chụp từ ứng dụng của chính project tại localhost, với vector mặc định minh họa và câu hỏi công khai. Ảnh là các vùng trên giao diện thật, không dựng mô phỏng hay thay nội dung DOM. Lượt trình duyệt riêng có UUID và thời gian khác request TestClient ở Chương 6; generation/backend tại thời điểm chụp phải được đọc trên ảnh hoặc metadata kiểm UI.

![Vùng dự đoán Pima: score, ngưỡng, nhãn và phiên bản được trình bày riêng](figures/ui-report.png)

Score hiển thị ba chữ số sau dấu thập phân để dễ đọc; response JSON giữ giá trị chính xác hơn. Việc nhãn bằng 0 chỉ mô tả output phân lớp theo ngưỡng của artifact, không là kết luận “không có bệnh”. Người xem luôn có task/label_semantics và phiên bản bên cạnh score.

![Trace giao diện gồm tám message của bảy vai trò; Coordinator xuất hiện hai lần](figures/ui-trace.png)

Trong cấu hình cache/template, KG/RAG mang nhãn degraded và Explanation có thể mang llm_not_configured. Monitoring vẫn hoàn tất. Trace 2.1 bổ sung duration_ms của từng call và decision; elapsed_ms vẫn là mốc tích lũy. Không cộng các mốc này để tính tổng latency.

![Vùng giải thích dùng template, có ID nguồn và tách khỏi điểm dự đoán](figures/ui-explanation.png)

Hai vùng còn lại của giao diện cung cấp nguồn truy xuất và bất định/giới hạn. Tab So sánh mô hình đọc 24 hàng summary theo cohort; tab Knowledge Graph hiển thị snapshot thực thể/quan hệ có nguồn của corpus. Snapshot trên giao diện giúp khám phá tri thức, không phải bằng chứng rằng một kết nối Neo4j production đang hoạt động.

![Mục quyết định và kiểm duyệt hiển thị attempts, lý do và số lần sửa thực tế](figures/ui-controls.png)

![Tab Công nghệ và kiểm chứng nối phương pháp với vai trò, source symbol và demo](figures/ui-technology.png)

Bảng công nghệ khai báo phần đã triển khai; report ghi phần đã chạy. Ví dụ, RL có mã và dùng trong chat nhưng feature_usage.rl_policy=False ở /api/report. Registry công bố neural_embedding, LangGraph/checkpoint/resume và streaming là chưa triển khai. Cách trình bày này giúp trả lời trực tiếp “có dùng không, dùng ở đâu, chứng minh bằng gì” mà không suy từ tên thư viện hoặc hình kiến trúc.

## 7.10. Kết luận và đóng góp

DiaCare đã hiện thực một nguyên mẫu Hybrid MAS theo bảy vai trò của đặc tả. Nhánh DL nhận dữ liệu từ SQLite, có baseline cùng ba kiến trúc neural và giao thức ngăn rò rỉ. Nhánh tri thức kết nối tài liệu Web/PDF, concept graph và truy xuất có provenance. Coordinator ghép dự đoán, luật và evidence thành báo cáo có cấu trúc; Explanation diễn đạt; Monitoring cung cấp metadata truy vết. Ví dụ chạy thật chứng minh các nhánh này gặp nhau trong cùng một request, đồng thời các loại thông tin vẫn được giữ riêng.

Kết quả thực nghiệm không xác nhận DL luôn vượt mô hình cổ điển hoặc graph luôn tăng retrieval. Các trường hợp baseline cạnh tranh, Hospital khó dự đoán, Early dao động giữa seed và lỗi ranking đều được giữ trong báo cáo. Chúng chỉ ra giới hạn dữ liệu/phương pháp và giúp xác định bước cải thiện tiếp theo có căn cứ.

Bản 2.1 bổ sung mã truy xuất thích ứng và kiểm duyệt hữu hạn, thời lượng từng call, decision trace, feature_usage và registry gắn phương pháp với source. Báo cáo, notebook và hướng dẫn bảo vệ kết nối các phần này tới ca chạy có thể kiểm tra. Các trọng số phục vụ được giữ để đáp ứng yêu cầu tái sử dụng. Neo4j đã có bằng chứng cục bộ; trạng thái môi trường public cần đọc riêng theo phiên bản. Xác thực lâm sàng, kiểm định ngoài miền, kiểm chứng từng claim và đánh giá tải vẫn là công việc tương lai.
