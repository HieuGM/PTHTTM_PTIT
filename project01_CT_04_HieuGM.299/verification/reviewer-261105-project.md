# Independent review — Project01

Ngày05/11/2026. Phạm vi: MAS/KB/API/UI, hợp đồng suy luận, Docker/dependency/config, tài liệu và sáu section báo cáo hiện có. Reviewer không review lại thuật toán ML do mình đã hiện thực; kết quả ML được tester kiểm tra với trọng số thật. Root README không tồn tại; đã đọc rules/kế hoạch và báo cáo tester.

## Kết luận

**Approve mã hiện tại; không còn finding chặn ở các phần đã review.** Sau sửa ba lỗi được báo, toàn bộ pytest đạt **55passed,1warning**,7,47giây. Root tiếp tục hoàn thành chương triển khai/phụ lục, kiểm tra image cuối bằngHTTPthật, xuất PDF/visualQA và ZIP; các bước đó chưa được coi hoàn thành trong kết luận review này.

## Finding và xử lý

1. **Trung bình — glucose bị ép kiểu ở chatAPI.** Bản sau50test vẫn chấp nhận JSONglucose=true, ép thành1mg/dL và trảHTTP200urgent; chuỗi"72" cũng được chấp nhận. Đã báo root; root đổi thành `StrictFloat | StrictInt | None` và giữ constraints/finitevalidator. Reviewer thêm testTrue/False/string; cả ba nay trả422, không sinh answer.
2. **Nhỏ — từ khóa bịa trùng từ bia.** Câu giáo dục uốngbia bị gắn yêu cầu bịa nguồn vì matchsubstring`bia` sau bỏ dấu. Root thay bằng cụm cụ thể về bịa nguồn/nghiên cứu. Regression xác nhận câu uốngbia không bị luậtfabrication chặn, câu bịa nguồn vẫnboundary.
3. **Nhỏ — endpointresults dùng tên tệp cũ.** Chỉpolicy-training xuất hiện dù hai modeltraining và systemevaluation tồn tại. Root cập nhật allowlist; testAPIxác nhận trả đủ bốn bản ghi hiện tại.
4. **Nhỏ — nhãnboundaryUI quá hẹp.** Dùng “ngoài phạm vi điều chỉnh thuốc” cho cả vị trí/lịch/bịa nguồn. Root đổi thành “Ngoài phạm vi hỗ trợ”.

Root đã nhận hai việc tài liệu cuối: đổi sốpytest50→55 và ghi prerequisitefetch/preparedata trước `scripts/test-models.py` do cache`data/splits` không nằm trongZIP. Đây là phần tài liệu đang hoàn thiện, không lỗi suy luận/runtime.

## Kiểm chứng độc lập

- Đọc `app/main.py`, agents contracts/coordinator/rules/policy, retrieval, JavaScript/HTML, Dockerfile/lock/render, README/DEPLOY, trainpolicy và section1–6.
- TestHTTPtrực tiếp tái hiện lỗi bool/stringglucose trước sửa và kiểm tra kết quảendpointresults.
- Được root giao sửa test; thêm5regression vào `tests/test_api_models.py` cho ba nhóm lỗi trên, không sửa productioncode hoặc số liệu.
- Chạy `python -m pytest tests -q -p no:cacheprovider`: **55passed**,1StarletteTestClient/httpxdeprecationwarning, không testfail. Các test dùng hai MLP thật, KB/policy thật; không mock.
- Báo cáo tester trước đó `plans/reports/261105-project-tester.md` giữ50casevà các lỗiNaN/Inf/SQLite/strictfeaturesđã sửa; bảnreviewbổ sung5case.

## Đánh giá thiết kế và độ trung thực

- Bảy vai trò chuyên trách cộngCoordinator, không tự nhận là tám tiến trình hoặcLLMtựlập kế hoạch. Context/request riêng, tracegiới hạn8message; nhánh hỏiđáp và phân tích thể hiện trong báo cáo đúng code.
- Safetyoverride đi trước truyxuất/policy, không dùngMLPđể loại trừ cấp cứu. Thuốc/liều và thông tin không có công cụ có boundary; report thừa nhận luật phủ định/triệu chứng chưa bao phủ mọi tiếng Việt.
- Câu trả lời dùng văn bản thẻ vớiID/URL, khôngLLM. Critickiểm traID+HTTPS, không được mô tả là chứng minh semanticanswerability hoặc chẩn đoán. Corpus24thẻ/19URLvà lỗiQ22được ghi rõ.
- Q-learning đúng scopecontextualbandit một bước gamma0,4state/3action,4.000episode, rewardrubrictựthiết kế. Greedypolicy[abstain,abstain,brief,detail]; không dùng kết cục bệnh nhân, không tự nhận lợi ích y khoa hoặc tốt hơnif/else.
- Catalogmetadata khớp biểu mẫu, labelsemantics hai task riêng, default có nhãn minh họa. UI dùngtextContent/relnoopener, không đưa câu hỏi thànhHTML; sigmoid hiển thị điểm nghiên cứu chưa hiệu chuẩn, không tự đặt nhãn nguy cơlâm sàng.
- APIpredict strictfeatures, missing/unknown/range/integer/NaN/Inf bịtừchối; chatglucose sau sửa cùng nguyên tắc. Validationhandlerkhông phản chiếu rawhealthinput, sửa lỗi serialize nonfinite đã được tester kiểm tra.
- SQLitechỉ chứa thẻ, đóng kết nối rõ; truyxuất vector từ cùng corpus. Không lưurequestpatientidentifier, không có publicendpointghi hoặc xuất hồ sơ.

## Dữ liệu và báo cáo

- Sáu section hiện có mô tả đúngCDC/Hospitalkhác nhãn/quần thể, datasetMỹlịch sử, chia patientgroup, CDCremoveconflictinggroups+dedupe, trainonlyscaler, validationcheckpoint/threshold.
- Bảng metric và sốparam4.033/3.329 khớp artifacts. Brier/APkhông bị đánh đồng là calibrationhoàn chỉnh hoặcPRtrapezoid. Report nêu false negatives, sensitivitycòn thấp và mộtseedchưa là bằng chứng ưu thế thống kê.
- Source/KBphần giới thiệu ViệtNam thừa nhận chưa có dữ liệu ngườiViệttrain; không biến nguồn đặt tạiViệtNam thành dân sốViệtNam.
- Recall@3/answerability/citationqualitytách biệt; Q22retrievalđúngtop3nhưngbriefchọnthẻ quá rộng được giữ. Bộ30câu/11rulecase được gọi bộphát triển, không là benchmarkkín hoặc kiểmđịnhlâm sàng.

## Deployment và phần cần xác nhận cuối

- Dockerfile nguồn dùngPython3.12slim, khóa dependencyLinux qua constraints, userappuser, mộtworker,PORTenv,KBSQLiteở/tmp. .dockerignore loại rawdata/report/runtime/tests/cache/secrets; runtimechỉCOPYapp/models/results.
- Renderconfig có healthCheckPath, PORTdo nhàcungcấp, khôngsecret; DEPLOYphân biệt containercục bộ và URLcloudchưa phát hành, có hướng dẫn rootDirkhirepođơn hoặcmonorepo.
- DockerHEALTHCHECKdùng8000cốđịnh; DEPLOYđã nêu giới hạnPORTkhác và dựa healthcheckroutecủacloud. Không coi cấu hìnhready là bằng chứng publicURLđã chạy.
- Root đang xử lý imagecuối sau diskfull; đã đề nghị giữ Dockerfilephânphối có basecôngkhai, chỉ dùng Dockerfiletạm cho offlineCOPYimagecục bộ. Reviewer chưa tự chạy DockerLinux và không thay kết luận đó bằngpytestWindows.
- READMEđang tham chiếu docker-verification/PDFchưa hoàn tất tại lúc review; chỉ bàn giao sau root tạo và kiểm tra những tệp thực đó. Kiểm tra visualPDF, manifest/giảinénZIP vẫn là shippinggate còn lại.

Không còn câu hỏi hoặc findingproductioncodechặn trong phạm vi review; root quản lý các bước bàn giao cuối.
