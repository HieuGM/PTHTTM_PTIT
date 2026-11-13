"""Executable feature inventory for the academic demo; implementation is not usage."""

VERSION = 'hybrid-mas-2.1'


def entry(identifier, name, agent, path, symbol, endpoint, scope, demo, implemented=True):
    return dict(id=identifier, name=name, agent=agent, implemented=implemented,
                source={'path': path, 'symbol': symbol}, endpoint=endpoint, scope=scope, demo=demo)


FEATURES = [
    entry('sql_training', 'Dữ liệu huấn luyện từ SQLite', 'DL Prediction',
        'app/ml/datasets.py', 'load_prepared', 'notebook / benchmark',
        'SELECT prepared tables cấp dữ liệu fit; không train trong request.', 'Mở database-manifest.json'),
    entry('deep_learning', 'Deep Learning suy luận từ trọng số thật', 'DL Prediction',
        'app/ml/predict.py', 'Predictor.predict', '/api/report',
        'Bốn cohort, model/version/scaler riêng; score chưa hiệu chuẩn lâm sàng.', 'Bốn form model mặc định'),
    entry('classical_ml', 'ML cổ điển làm baseline', 'Thực nghiệm offline',
        'app/ml/training.py', 'train_one', 'notebook / benchmark',
        'Logistic, Random Forest, HGB trong 72 lượt; API report phục vụ model neural đã chọn.', 'Mở bảng benchmark từng cohort'),
    entry('adaptive_retrieval', 'Truy xuất bổ sung có giới hạn', 'KG/RAG',
        'app/knowledge/adaptive.py', 'AdaptiveRetrieval.run', '/api/report',
        'Tối đa 3 lượt; sufficiency heuristic, không là xác suất đúng.', 'Mờ mắt là gì? → xem alias_rewrite'),
    entry('graph', 'Knowledge Graph có evidence', 'KG/RAG',
        'app/knowledge/retrieval.py', 'KnowledgeBase.graph_evidence', '/api/report',
        'Neo4j khi cấu hình/kết nối; cache SQLite được công bố riêng.', 'Xem graph_backend và nguồn PDF'),
    entry('rag', 'Truy xuất văn bản để giải thích', 'KG/RAG + Explanation',
        'app/knowledge/generation.py', 'EvidenceGenerator.generate', '/api/report',
        'Word/char TF-IDF, LSA32 và graph; FPT hoặc template có nhãn.', 'HbA1c phản ánh điều gì?'),
    entry('output_review', 'Kiểm duyệt và sửa câu trả lời', 'Explanation',
        'app/knowledge/review.py', 'review_and_revise', '/api/report',
        'Kiểm xác định; tối đa 1 sửa extractive; không chứng minh mọi claim y khoa.', 'Xem quality.attempts; chạy test_output_review.py'),
    entry('rules', 'Luật an toàn có ưu tiên', 'Rule-Based',
        'app/agents/rules.py', 'check', '/api/report',
        'Cảnh báo và giới hạn yêu cầu; không chẩn đoán hoặc kê đơn.', 'Mẹ tôi đang bất tỉnh / yêu cầu liều insulin'),
    entry('coordination', 'Điều phối thích ứng trong khung bảy vai trò', 'Coordinator',
        'app/agents/workflow.py', 'ReportWorkflow.run', '/api/report',
        'Outer workflow hữu hạn; retries/review nội bộ, có reason và budget.', 'Thiếu feature dừng trước DL'),
    entry('monitoring', 'Thời gian từng agent và audit metadata', 'Monitoring',
        'app/agents/contracts.py', 'Context.emit', '/api/report',
        'duration_ms đo call; elapsed_ms là mốc tích lũy; audit opt-in.', 'So hai cột thời gian trong trace'),
    entry('rl_simulation', 'Q-learning cách trình bày', 'Policy mở rộng',
        'app/agents/policy.py', 'PresentationPolicy.choose', '/api/chat',
        'Bandit mô phỏng gamma=0; không tham gia report hoặc điều trị.', 'Mở policy-training.json và trace chat'),
    entry('neural_embedding', 'Neural embedding', '-', '', '', '-',
        'Chưa triển khai; LSA trong bài không phải neural embedding.', '-', False),
    entry('langgraph', 'LangGraph / checkpoint / resume', '-', '', '', '-',
        'Chưa triển khai; điều phối hiện tại bằng Python có hợp đồng.', '-', False),
    entry('streaming', 'SSE streaming tiến trình', '-', '', '', '-',
        'Chưa triển khai; API trả report và trace sau khi hoàn tất.', '-', False),
]

AGENTS = [
    {'agent': 'PatientDataAgent', 'reads': ['dataset','features','glucose','unit'],
     'writes': ['validated','feature_count','feature_order'], 'tools': ['validate_features'],
     'decision': 'allow_prediction / stop'},
    {'agent': 'DLPredictionAgent', 'reads': ['validated features','serving artifacts'],
     'writes': ['prediction'], 'tools': ['Predictor.predict'], 'decision': 'inference / dependency_error'},
    {'agent': 'RuleBasedAgent', 'reads': ['question','prediction','glucose','unit'],
     'writes': ['rules'], 'tools': ['check'], 'decision': 'allow_retrieval / safety_override'},
    {'agent': 'KGRAGAgent', 'reads': ['question','public corpus','ontology'],
     'writes': ['evidence','retrieval'], 'tools': ['AdaptiveRetrieval.run','KnowledgeBase.retrieve'],
     'decision': 'accept / rewrite / lexical retry / abstain'},
    {'agent': 'CoordinatorAgent', 'reads': ['request','intermediate outputs'],
     'writes': ['request_id','status','messages','report'], 'tools': ['ReportWorkflow.run'],
     'decision': 'schedule / aggregate / terminate'},
    {'agent': 'ExplanationAgent', 'reads': ['question','prediction','rules','evidence'],
     'writes': ['explanation','quality'], 'tools': ['EvidenceGenerator.generate','review_and_revise'],
     'decision': 'pass / extractive revision / abstain / safety_rule'},
    {'agent': 'MonitoringAgent', 'reads': ['execution metadata'], 'writes': ['audit'],
     'tools': ['MonitoringAgent.run'], 'decision': 'metadata_only / opt-in write / degraded'},
]


def inventory(kb, generator):
    return {'system_version': VERSION, 'features': FEATURES, 'agent_contracts': AGENTS,
        'configured_backends': {'knowledge': kb.inventory()['graph_backend'],
                                'llm': generator.configuration()['configured']},
        'usage_note': 'implemented khác configured và khác executed. Đọc feature_usage của từng report.',
        'budgets': {'retrieval_calls': 3, 'review_revisions': 1, 'core_agents': 7,
                    'outer_messages': 12, 'extra_llm_calls_for_revision': 0}}


def usage(messages, report):
    agents = {m['agent']: m for m in messages}
    retrieval = (report or {}).get('retrieval', {})
    quality = (report or {}).get('quality', {})
    explanation = (report or {}).get('explanation', {})
    evidence = (report or {}).get('retrieved_evidence', [])
    graph = retrieval.get('graph_backend') or next((e.get('graph_backend')
        for e in evidence if e.get('graph_backend')), 'not_used')
    return {'deep_learning': agents.get('DLPredictionAgent', {}).get('status') == 'ok',
        'adaptive_retrieval': bool(retrieval.get('attempts')),
        'retrieval_attempts': len(retrieval.get('attempts', [])),
        'retrieval_retry': len(retrieval.get('attempts', [])) > 1,
        'output_review': bool(quality) and quality.get('status') != 'safety_override',
        'review_revision': quality.get('revision_count', 0),
        'fpt_called': bool(quality.get('provider_attempted')) or explanation.get('generation') == 'fpt_cloud_llm',
        'final_generation': explanation.get('generation', 'not_used'), 'graph_backend': graph,
        'rl_policy': False, 'neural_embedding': False, 'langgraph': False, 'streaming': False}
