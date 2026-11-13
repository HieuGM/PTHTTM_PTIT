# CHƯƠNG 5. KNOWLEDGE GRAPH, WEB/PDF VÀ RAG

## 5.1. Corpus thực và nguồn Việt Nam

Corpus hiện có 12 tài liệu tải thật:11 Web gồm 7 WHO/NIDDK và 4 Vinmec, cùng 1 PDF tiếng Việt 77 trang do Sở Y tế Đồng Nai đăng tải. Ngoài ra có 14 record chỉ tham chiếu URL và 24 thẻ biên soạn có nguồn. Tổng 340 chunk đã bao gồm các thẻ; không cộng 24 lần nữa và không gọi 26 record là 26 tài liệu tải thành công.

Vinmec bổ sung nội dung tiếng Việt về chế độ ăn, xét nghiệm chẩn đoán type 2, tổng quan type 2 và thai kỳ. Bốn trang được tải HTTP 200, lưu hash, URL cuối, ngày tải và nhãn cập nhật hiển thị. Bài viết là evidence giáo dục, không là dữ liệu bệnh nhân gán nhãn hoặc dataset có giấy phép mở đã xác minh.

PDF là tài liệu hướng dẫn type 2 lịch sử năm 2020, bản tải từ website Sở Y tế Đồng Nai. File có 77 trang, SHA256 `305fc9c51d54418f5798e7691d59f94d24545e0dd728945e2225794730694486`. Không tuyên bố đây là hướng dẫn mới nhất. Số trang, văn bản trích và metadata giúp xác định nguồn khi trả kết quả.

## 5.2. Ingestion và provenance

Luồng ingestion tải nguồn → xác định HTML/PDF → bỏ phần giao diện khi trích HTML hoặc đọc text từng trang PDF → chia chunk có ngữ cảnh → gắn nguồn/hash/page → nhận diện concept → lưu corpus → tạo graph và Cypher. Corpus được chuẩn bị trước, app không cần tải lại tài liệu lúc startup.

Raw cache không phát hành; JSON corpus giữ phần văn bản dùng trong thực nghiệm và metadata. Cần tôn trọng quyền nội dung của nhà xuất bản, trích dẫn nguồn và không xem nguồn công khai đồng nghĩa dữ liệu mở để tái phân phối không giới hạn.

Nguồn CDC về ketoacidosis có lần tải HTTPError được ghi failures; không tính là tải thành công. Một số URL PDF cũ chuyển hướng lỗi nên không dùng làm bằng chứng đã ingest. Với cache cũ không có HTTP metadata, retrieved_at được ghi theo timestamp cache, không bịa thời gian HTTP ban đầu.

## 5.3. Schema graph

Graph có 34 Concept,26 Document và 340 Chunk, tổng 400 node. Document gồm 12 downloaded và 14 reference-only. HAS_CHUNK nối tài liệu và đoạn; MENTIONS nối chunk với concept. Có 2160 MENTIONS tự nhận diện từ alias, khác với 19 quan hệ chuyên môn có rule và đoạn nguồn.

19 quan hệ chuyên môn gồm 3 IS_A,1 REQUIRES,3 RISK_ASSOCIATION,5 MAY_HAVE_SYMPTOM,4 MAY_HAVE_COMPLICATION và 3 DIAGNOSED_USING. Mỗi relation có evidence_chunk_id, document_id, URL, page và phương pháp kiểm mẫu trong văn bản. Đây là đồ thị kiến thức giáo dục, không là đồ thị chẩn đoán cá nhân hay causal discovery.

DB_diabet.cypher đặt unique constraint cho Concept/Document/Chunk, dùng MERGE để import lặp không nhân node/edge. Tham chiếu source từ relation giúp truy ngược đến đoạn thực thay vì triple không có dẫn chứng. File seed không chứa mật khẩu hoặc khóa.

## 5.4. Neo4j thật và cache offline

Neo4j Community 5.26 được chạy cục bộ bằng Docker riêng. Seed đã import; kiểm node/edge, idempotence và đối chiếu cache thực. Kết quả có 400 node và 2545 edge ở corpus này. Tập quan hệ gồm HAS_CHUNK, MENTIONS, MEDICAL_RELATION và SUPPORTS nên tổng edge không chỉ là 19.

Knowledge Agent query graph bằng tham số và lấy chunk liên quan; không cho người dùng chạy Cypher tùy ý. Khi thiếu Neo4j, cache SQLite trả bằng chứng công khai và trạng thái sqlite_cache/degraded. Neo4j local đã kiểm không đồng nghĩa Render có kết nối graph production; cần URI/user/password của instance truy cập được từ Render nếu muốn chế độ đó.

## 5.5. Ba phương pháp retrieval

Lexical dùng word TF-IDF unigram/bigram. Semantic dùng Latent Semantic Analysis với TruncatedSVD 32 trên TF-IDF; đây không phải neural embedding hoặc mô hình ngôn ngữ đã huấn luyện thêm. Hybrid_graph kết hợp word 0,50, character TF-IDF 0,25, LSA 0,25 và boost nhỏ cho chunk/concept graph liên quan. Alias Việt/Anh giúp nối truy vấn với ontology.

Mọi variant đều có prior cố định +0,045 cho curated card khi word score>0,03; lexical và semantic trong bảng cũng bao gồm prior này. Các kết quả có id, title, text, URL, document_id, page, retrieval_method, graph_backend, matched_entities và graph_paths. Score là điểm xếp hạng trong retriever, không là xác suất độ đúng. Threshold hạn chế kết quả không liên quan nhưng không bảo đảm luôn từ chối đúng.

## 5.6. Đánh giá retrieval và lỗi

Bộ 30 câu phát triển cũ gồm 22 câu có thẻ gold và 8 câu ngoài phạm vi. Để so sánh, dùng cùng 22 gold thẻ; cách chấm nghiêm này có thể bỏ qua chunk mới tương đương nội dung. Không xem đây là holdout y khoa độc lập vì thẻ và câu hỏi đã được dùng trong phát triển.

| Phương pháp | Recall@1 | Recall@3 | MRR@3 |
|---|---:|---:|---:|
| Lexical | 0,9545 | 1,0000 | 0,9773 |
| LSA semantic | 0,5909 | 0,8636 | 0,7121 |
| Hybrid graph | 0,9091 | 1,0000 | 0,9470 |

Hybrid graph không thắng lexical ở Recall@1 trong bộ này. Giá trị của graph là cấu trúc thực thể, đường quan hệ và provenance; cải thiện chất lượng retrieval cần đánh giá thêm. Không che kết quả semantic yếu hoặc dùng câu hỏi mới để chỉnh ranking rồi gọi holdout.

Ca Q22 trong phiên bản cũ đã có thẻ phù hợp ở hạng 2, nhưng giải thích ngắn lấy nguồn tổng quát hạng 1. Lỗi này cho thấy Recall@3 cao không đủ chứng minh câu trả lời cuối đúng trọng tâm. knowledge-verification.json giữ từng kết quả; các câu mới kiểm nguồn bổ sung có ghi phạm vi riêng.

Tám truy vấn mới chưa tune kiểm đúng tên tài liệu Vinmec có lexical Recall@1=0,0000, Recall@3=0,8750, MRR@3=0,4167; semantic=0,2500/0,5000/0,3750; hybrid=0,2500/0,5000/0,3542. Gold hẹp này có thể không chấp nhận thẻ hoặc bài khác vẫn liên quan. Không xem đây là clinical benchmark; các lỗi được giữ để thấy hạn chế retrieval.

## 5.7. FPT Cloud và grounded generation

Explanation Agent dùng HTTPS Chat Completions với Bearer key và model người dùng cấu hình. Gateway AI Marketplace đã xác minh là https://mkp-api.fptcloud.com, full endpoint /chat/completions. Không tự thêm /v 1 vì gateway này có route theo tài liệu nhà cung cấp; base và full URL là hai cách cấu hình thay thế.

Prompt chỉ gửi câu hỏi, evidence giới hạn, kết quả mô hình đã chọn trường và rule. Không gửi toàn bộ raw feature/patient ID. LLM được yêu cầu trả JSON chứa answer và citation_ids, mỗi đoạn gắn [ID], không thêm URL hoặc chẩn đoán/kê liều. Request có timeout, giới hạn token, không theo redirect để tránh gửi Bearer key sang đích khác.

Validator kiểm cấu trúc, ID thuộc evidence, citation inline khớp danh sách và không có URL mới. Validator không kiểm chứng ngữ nghĩa từng claim và không thay chuyên gia. Không có evidence thì từ chối; thiếu cấu hình/lỗi API/JSON/citation thì template có nhãn. Bằng chứng API thực chỉ ghi status/model/usage/citation, không khóa. Lượt gọi thực đã tạo câu trả lời có citation KB08 và đoạn PDF trang 19 trong 4,78 giây; usage 1612 prompt token và 388 completion token, gồm 256 reasoning token. Đây là số đo một request, không là benchmark latency hoặc kiểm chứng đúng y khoa. Kết quả nằm tại results/fpt-api-verification.json.

## 5.8. Giới hạn của RAG hiện tại

Corpus nhỏ và không bảo đảm bao phủ mọi câu hỏi. PDF lịch sử cần ngày/phiên bản rõ; nhiều nguồn có thể khác ngữ cảnh. Concept graph dùng alias và rule lexical nên có thể nhận diện thiếu hoặc dư. LSA nhỏ không có năng lực ngữ nghĩa như embedding hiện đại; ngôn ngữ Việt/Anh và câu hỏi dài có thể giảm thứ hạng.

Chưa có hội đồng lâm sàng chấm claim-level support trên tập lớn, chưa đánh giá đầy đủ prompt injection hoặc thay đổi nguồn theo thời gian. Số citation hợp lệ không là tỷ lệ đúng y khoa. Hướng tiếp theo là bộ hỏi đáp độc lập có người thẩm định, kiểm nguồn/phiên bản và đo riêng retrieval, groundedness, refusal, latency/cost.

## 5.9. Phân biệt KB, KG, retrieval và generation

Knowledge Base là toàn bộ tri thức đã tổ chức để hệ thống sử dụng, gồm văn bản, thẻ và metadata. Knowledge Graph là phần biểu diễn thực thể cùng quan hệ: nó giúp truy theo concept và tìm đoạn hỗ trợ một cạnh. Retrieval chọn những đoạn phù hợp với một câu hỏi; generation diễn đạt câu trả lời từ các đoạn đã chọn. Một graph có nhiều cạnh không tự tạo ra câu trả lời, và LLM không thay việc lưu nguồn.

Lewis và cộng sự (2020) kết hợp bộ nhớ tham số của mô hình sinh với bộ nhớ tài liệu bên ngoài được truy xuất. DiaCare áp dụng ý tưởng truy xuất rồi cung cấp ngữ cảnh, nhưng không huấn luyện mô hình RAG end-to-end như bài báo gốc. Mô hình dự đoán DL trên bảng bệnh nhân và dịch vụ LLM sinh giải thích là hai thành phần khác nhau: một bên tạo score nghiên cứu từ feature, bên kia diễn đạt từ evidence/model/rule đã cung cấp.

| Thành phần | Biểu diễn lưu | Công cụ trong bài | Trả lời được câu hỏi nào? |
|---|---|---|---|
| Dữ liệu học có giám sát | Bảng feature/target/split | SQLite, datasets.py | Model được fit trên bản ghi và nhãn nào? |
| KB văn bản | Document/chunk/title/URL/page | corpus.json, store.py | Đoạn nào nói về chủ đề đang hỏi, nguồn ở đâu? |
| KG | Concept và quan hệ có evidence | graph_builder.py, Neo4j/cache | Concept liên quan thế nào và cạnh dựa trên đoạn nào? |
| Retriever | Vector chỉ mục và ranking | retrieval.py | Những đoạn nào phù hợp nhất với câu hỏi này? |
| Generator | Prompt gồm evidence/model/rule | generation.py, FPT hoặc template | Có thể giải thích kết quả bằng ngôn ngữ thế nào? |

Trong retrieval.py, query được mở rộng bằng alias concept. Word TF-IDF và character TF-IDF đều chuẩn hóa vector; tích vô hướng tương ứng cosine trong không gian đó. LSA chiếu vector word xuống không gian 32 chiều rồi chuẩn hóa. Với phương pháp hybrid, điểm nền bằng 0,50 × word + 0,25 × character + 0,25 × LSA. Code cộng 0,055 nếu chunk thuộc ứng viên graph và word>0,015; cộng 0,025 nếu concept giao truy vấn; prior thẻ biên soạn là 0,045 khi word>0,03.

Các hệ số này là heuristic của bản thử nghiệm. Điểm cuối không phải xác suất một phát biểu đúng. Bộ lọc score≥0,09 và điều kiện tối thiểu word/character chỉ giảm nhiễu; chúng không bảo đảm câu hỏi ngoài miền luôn bị từ chối. KnowledgeAgent trong luồng report yêu cầu tối đa bốn hit; generator còn giới hạn ngữ cảnh theo cấu hình. Người đọc có thể đối chiếu toàn bộ ranking đã lưu để giải thích vì sao một tài liệu liên quan nhưng không lên hạng đầu.

## 5.10. Truy vết một kết quả tri thức

Theo mục 7.2 của đặc tả, K = (G_Neo4j, D_RAG): G là graph và D là tập văn bản phục vụ truy xuất. Bản local đã kiểm G trên Neo4j; khi chạy offline, cache giữ bản biểu diễn đã materialize từ cùng corpus. Việc có D hoặc cache không được dùng để tuyên bố một kết nối G_Neo4j đang hoạt động.

Một hit cần đi được theo chuỗi: ID chunk → document_id → URL và page nếu là PDF. Nếu có graph_path, relation cần evidence_chunk_id tương ứng; đường graph là chỉ mục bằng chứng, không là chứng minh quan hệ nhân quả. Document reference-only chỉ cung cấp metadata nguồn của thẻ, không được tính là trang đã tải và trích văn bản thành công.

Việc kiểm citation xảy ra sau retrieval/generation. Đầu tiên chọn evidence từ corpus tin cậy theo ID; tiếp theo prompt giới hạn ID cho LLM; cuối cùng validate_generated kiểm JSON và đối chiếu citation_ids với citation trong câu trả lời. Một citation đúng cấu trúc vẫn có thể đi kèm diễn giải quá mức. Vì vậy, bài đánh giá riêng chất lượng xếp hạng, kiểm cấu trúc nguồn và hành vi fallback, đồng thời ghi rõ chưa có kiểm chứng ngữ nghĩa toàn diện.

## 5.11. Chính sách truy xuất thích ứng 2.1.1

KnowledgeAgent.run gọi AdaptiveRetrieval.run trong app/knowledge/adaptive.py. Controller diễn giải alias, xác định anchor từ ontology; khi không có concept phù hợp, có thể dùng topic cụ thể của thẻ biên soạn. Mỗi hit được đối chiếu ID, text, URL, document_id và page với source_index. Một lượt đủ điều kiện khi có hit được chấp nhận, có giao token truy vấn và các anchor yêu cầu được bao phủ. Đây là heuristic điều khiển, không là confidence y khoa hoặc bằng chứng từng claim đúng.

Controller thử hybrid_graph trên câu hỏi gốc; nếu chưa đủ và có alias thay thế thì thử câu đã chuẩn hóa; cuối cùng có thể thử lexical. Tối đa ba call, mỗi call lấy tối đa bốn hit. Không so trực tiếp raw score giữa hybrid và lexical. Khi hết ngân sách mà chưa đủ, evidence trả rỗng để Explanation từ chối. KnowledgeBase.retrieve gốc giữ nguyên để kết quả baseline lịch sử vẫn có cùng ý nghĩa.

Ca “Mờ mắt là gì?” minh họa retry có nguyên nhân: lượt gốc chưa bao phủ anchor blurred_vision; alias “nhìn mờ” ở lượt hai lấy được KB05. Ngược lại, “HbA1c phản ánh điều gì?” đủ ngay lượt đầu. Metadata attempts ghi method, query_strategy, số ứng viên, coverage, reason và duration; không ghi lại câu hỏi gốc trong audit.

<!-- ADAPTIVE_EVAL_START -->

Bảng sau đọc từ agent-upgrade-evaluation.json. Đây là phép đo phát triển sau khi đã xem lỗi phiên bản đầu (post-hoc); không phải holdout độc lập hoặc kiểm định lâm sàng.

| Bộ câu hỏi / phương pháp | Recall@1 | Recall@3 | MRR@3 |
|---|---:|---:|---:|
| 22 câu gold ID / baseline_hybrid | 0,9091 | 1,0000 | 0,9470 |
| 22 câu gold ID / adaptive | 0,8636 | 0,9545 | 0,9015 |
| 8 câu gold tài liệu / baseline_hybrid | 0,2500 | 0,5000 | 0,3542 |
| 8 câu gold tài liệu / adaptive | 0,2500 | 0,5000 | 0,3542 |

Policy đánh giá: adaptive-evidence-2.1.1. Bản thử đầu được giữ tại agent-upgrade-evaluation-v1.json. Adaptive còn bỏ sót Q21 trong bộ gold ID; phép kiểm đủ bằng chứng có thể từ chối một câu hợp lệ về nguồn dữ liệu. Tám gold tài liệu vẫn có những lỗi của baseline. Không kết luận nâng cấp làm tăng mọi metric.

Ca “Mờ mắt là gì?” minh họa một nhánh bổ sung thật: lượt đầu thiếu hỗ trợ concept, lượt sau chuẩn hóa alias thành “nhìn mờ” và lấy được KB05. Nếu lượt đầu đã đủ, bộ điều khiển kết thúc ngay; không ép gọi thêm để trình diễn.

<!-- ADAPTIVE_EVAL_END -->

Bảng lấy từ results/agent-upgrade-evaluation.json. Chính sách 2.1 ban đầu có hồi quy và một điều kiện gây retry dù evidence đã đủ; kết quả được giữ nguyên trong agent-upgrade-evaluation-v1.json. Bản 2.1.1 bỏ điều kiện đó, bổ sung diễn giải topic/alias sau khi xem lỗi phát triển. Đây là so sánh hậu kiểm trên cùng tập phát triển, không phải holdout độc lập. Q21 vẫn bị từ chối và làm giảm Recall@3; các lỗi gold tài liệu vẫn được giữ. Nâng cấp đem lại điều khiển, truy vết và một số ca diễn đạt lại có ích, chưa chứng minh chất lượng xếp hạng tăng tổng thể. Thêm retrieval cũng có thể làm tăng thời gian.

Chính sách này không học một mô hình phản tư hoặc neural retriever. Bài chưa triển khai learned Self-RAG, bge-m3 hay neural embedding; LSA32 vẫn là phép giảm chiều trên TF-IDF. Khi bảo vệ, nên mở attempts và ca lỗi để giải thích hành vi thay vì chỉ nêu tên phương pháp.
