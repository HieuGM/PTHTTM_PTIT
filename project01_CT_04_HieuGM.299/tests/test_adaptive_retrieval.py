"""Real-corpus support and bounded retry/failure behavior of report retrieval."""
import json
import pytest
from app.agents.roles import KnowledgeAgent
from app.knowledge.adaptive import AdaptiveRetrieval, rewrite_query


def test_real_corpus_hba1c_stops_at_one_and_keeps_provenance(coordinator):
    result = KnowledgeAgent(coordinator.kb).run('HbA1c phản ánh điều gì?')
    policy = result['retrieval']
    assert policy['sufficient'] and policy['selected_attempt'] == 1
    assert len(policy['attempts']) == 1
    assert policy['policy_version'] == 'adaptive-evidence-2.1.1'
    assert 1 <= len(result['evidence']) <= 4
    for hit in result['evidence']:
        original = coordinator.kb.source_index[hit['id']]
        assert hit['text'] == original['text'] and hit['url'] == original['url']
        assert hit.get('page') == original.get('page')


def test_real_corpus_sufficient_first_round_is_not_forced_to_retry(coordinator):
    question = 'Xét nghiệm đường ba tháng phản ánh điều gì?'
    result = KnowledgeAgent(coordinator.kb).run(question)
    policy = result['retrieval']
    assert policy['sufficient'] and policy['selected_attempt'] == 1
    assert len(policy['attempts']) == 1
    assert result['evidence']
    encoded = json.dumps(policy, ensure_ascii=False)
    assert question not in encoded and rewrite_query(question) not in encoded
    assert all('query' not in a and 'question' not in a for a in policy['attempts'])


def test_real_corpus_retries_only_when_alias_anchor_is_missing(coordinator):
    result = AdaptiveRetrieval(coordinator.kb).run('Mờ mắt là gì?')
    policy = result['retrieval']
    assert policy['selected_attempt'] == 2
    assert policy['attempts'][0]['covered_anchor_count'] == 0
    assert policy['attempts'][0]['supported_count'] == 0
    assert policy['attempts'][1]['covered_anchor_count'] == 1
    assert policy['attempts'][1]['query_strategy'] == 'alias_rewrite'
    assert any(hit['id'] == 'KB05' for hit in result['evidence'])


@pytest.mark.parametrize('question', ['CDC BRFSS được thu thập ở đâu?',
    'Giải thích bài toán hospital.', 'Trước xét nghiệm đường máu lúc đói cần nhịn ăn bao lâu?'])
def test_curated_topics_and_fasting_alias_remain_answerable(coordinator, question):
    result = AdaptiveRetrieval(coordinator.kb).run(question)
    assert result['retrieval']['sufficient'] and result['evidence']


@pytest.mark.parametrize('question', ['Ai vô địch World Cup bóng đá?',
                                     'Việt Nam có vô địch World Cup bóng đá không?',
                                     'Viết chương trình Python sắp xếp mảng.'])
def test_real_corpus_unrelated_questions_abstain(coordinator, question):
    result = KnowledgeAgent(coordinator.kb).run(question)
    assert result['evidence'] == []
    assert result['retrieval']['sufficient'] is False
    assert result['retrieval']['reason'] == 'no_domain_anchor'


def test_empty_retrieval_has_hard_three_call_budget(coordinator, monkeypatch):
    calls = []
    def empty(query, **kwargs):
        calls.append(kwargs)
        return []
    monkeypatch.setattr(coordinator.kb, 'retrieve', empty)
    result = AdaptiveRetrieval(coordinator.kb).run('HbA1c và ăn kiêng cần hiểu thế nào?')
    assert len(calls) == 3
    assert all(c['k'] == 4 for c in calls)
    assert [c['method'] for c in calls] == ['hybrid_graph', 'hybrid_graph', 'lexical']
    assert result['evidence'] == [] and result['retrieval']['exhausted']


def test_errors_are_bounded_and_do_not_leak_exception_text(coordinator, monkeypatch):
    calls = []
    def unavailable(query, **kwargs):
        calls.append(query)
        raise OSError('PRIVATE_QUESTION_OR_PROVIDER_DETAIL')
    monkeypatch.setattr(coordinator.kb, 'retrieve', unavailable)
    result = AdaptiveRetrieval(coordinator.kb).run('HbA1c và ăn kiêng là gì?')
    assert len(calls) == 3 and result['evidence'] == []
    assert all(a['error_code'] == 'OSError' for a in result['retrieval']['attempts'])
    assert 'PRIVATE_QUESTION_OR_PROVIDER_DETAIL' not in json.dumps(result)


def test_tampered_provenance_never_becomes_evidence(coordinator, monkeypatch):
    source = next(x for x in coordinator.kb.items if 'a1c' in x.get('concept_ids', []))
    forged = {**source, 'url': 'https://forged.example.invalid', 'score': 999}
    monkeypatch.setattr(coordinator.kb, 'retrieve', lambda *args, **kwargs: [forged])
    result = AdaptiveRetrieval(coordinator.kb).run('HbA1c phản ánh điều gì?')
    assert result['evidence'] == [] and not result['retrieval']['sufficient']


def test_lexical_fallback_can_recover_without_score_comparison(coordinator, monkeypatch):
    source = next(x for x in coordinator.kb.items if x['id'] == 'KB08')
    calls = []
    def recover(query, **kwargs):
        calls.append(kwargs['method'])
        return [] if kwargs['method'] == 'hybrid_graph' else [{**source, 'score': .00001}]
    monkeypatch.setattr(coordinator.kb, 'retrieve', recover)
    result = AdaptiveRetrieval(coordinator.kb).run('HbA1c phản ánh điều gì?')
    assert calls == ['hybrid_graph', 'lexical']
    assert result['retrieval']['selected_attempt'] == 2 and result['retrieval']['sufficient']
    assert result['evidence'][0]['score'] == .00001


def test_alias_retry_occurs_only_after_genuinely_empty_first_round(coordinator, monkeypatch):
    retrieve, calls = coordinator.kb.retrieve, []
    def recover(query, **kwargs):
        calls.append(query)
        return [] if len(calls) == 1 else retrieve(query, **kwargs)
    monkeypatch.setattr(coordinator.kb, 'retrieve', recover)
    result = AdaptiveRetrieval(coordinator.kb).run('Xét nghiệm đường ba tháng phản ánh điều gì?')
    assert len(calls) == 2 and result['retrieval']['selected_attempt'] == 2
    assert result['retrieval']['attempts'][0]['supported_count'] == 0
    assert result['retrieval']['attempts'][1]['query_strategy'] == 'alias_rewrite'


@pytest.mark.parametrize('value', ['', None, 42])
def test_invalid_query_is_not_sent_to_retriever(coordinator, value):
    result = AdaptiveRetrieval(coordinator.kb).run(value)
    assert result['evidence'] == [] and result['retrieval']['attempts'] == []
