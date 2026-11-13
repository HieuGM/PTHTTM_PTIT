"""Unit cases exercise bounded revision and narrow safeguards without a provider call."""
import json
import pytest
from app.agents.reporting import ExplanationAgent
from app.knowledge.generation import EvidenceGenerator
from app.knowledge.review import (DISCLAIMER, REFUSAL, _publish_checked, review_and_revise,
                                  review_output, unsafe_codes)

EVIDENCE = [{'id': 'A', 'title': 'HbA1c education', 'url': 'https://example.org/a',
             'document_id': 'DOC-A', 'page': 2,
             'text': 'HbA1c phản ánh mức đường huyết trung bình trong khoảng ba tháng.'}]


def draft(answer=None, **changes):
    value = {'answer': (answer or EVIDENCE[0]['text']+' [A]')+' '+DISCLAIMER,
        'generation': 'template', 'status': 'llm_not_configured',
        'citations': [{k: EVIDENCE[0][k] for k in ['id', 'title', 'url', 'document_id', 'page']}],
        'model': None, 'usage': None}
    return {**value, **changes}


def test_valid_draft_preserves_generation_status_and_needs_no_revision():
    result = review_and_revise(draft(), EVIDENCE)
    assert result['answer'] == draft()['answer']
    assert result['generation'] == 'template' and result['status'] == 'llm_not_configured'
    assert result['review']['initial_passed'] is True
    assert result['review']['passed'] is True and result['review']['revision_count'] == 0
    assert result['review']['status'] == 'passed'
    assert 'not medical validation' in result['review']['scope']


@pytest.mark.parametrize('unsafe', [
    'Bạn chắc chắn mắc bệnh đái tháo đường. [A]',
    'Bạn không bị tiểu đường. [A]',
    'Bạn nên tiêm insulin 10 đơn vị mỗi tối. [A]',
    'Hãy uống metformin 500 mg. [A]',
    'Inject 5 units insulin. [A]',
])
def test_explicit_diagnosis_or_drug_dose_is_replaced_once(unsafe):
    result = review_and_revise(draft(unsafe), EVIDENCE)
    review = result['review']
    assert not review['initial_passed'] and review['final_passed']
    assert review['revision_count'] == review['max_revisions'] == 1
    assert len(review['attempts']) == 2 and not review['attempts'][0]['passed']
    assert review['status'] == 'revised' and result['status'] == 'revised_extractive'
    assert unsafe not in json.dumps(result, ensure_ascii=False)
    assert not unsafe_codes(result['answer'])
    assert '[A]' in result['answer'] and DISCLAIMER in result['answer']


@pytest.mark.parametrize('text', [
    'Không thể kết luận bạn mắc bệnh đái tháo đường từ điểm này.',
    'Nếu bạn bị tiểu đường, hãy trao đổi với bác sĩ về việc theo dõi.',
    'Không tự tăng liều insulin hoặc uống metformin 500 mg theo ứng dụng.',
    'Không có nghĩa là bạn không bị tiểu đường.',
    'Glucose 126 mg/dL là một giá trị xét nghiệm, không phải liều thuốc.',
])
def test_negated_educational_context_and_glucose_units_are_not_unsafe(text):
    assert unsafe_codes(text) == []


@pytest.mark.parametrize('alteration,issue', [
    ({'answer': 'HbA1c phản ánh đường huyết trung bình. [UNSEEN] '+DISCLAIMER}, 'citation_mismatch'),
    ({'citations': [{'id': 'A', 'url': 'https://example.org/forged'}]}, 'invalid_evidence_provenance'),
    ({'answer': 'Mặt trăng có một triệu con rồng màu tím. [A] '+DISCLAIMER}, 'weak_lexical_support'),
    ({'answer': EVIDENCE[0]['text']+' [A]'}, 'missing_disclaimer'),
])
def test_structural_provenance_and_lexical_problems_trigger_one_revision(alteration, issue):
    original = draft()
    original.update(alteration)
    result = review_and_revise(original, EVIDENCE)
    assert issue in result['review']['initial_issue_codes']
    assert result['review']['passed'] and result['review']['revision_count'] == 1


def test_rejected_provider_metadata_is_honest_and_draft_not_retained():
    original = draft('PRIVATE_REJECTED_DRAFT Bạn mắc tiểu đường. [A]',
        generation='fpt_cloud_llm', status='grounded', model='test-model', usage={'total_tokens': 40})
    result = review_and_revise(original, EVIDENCE)
    assert result['generation'] == 'template' and result['model'] is None
    assert result['usage'] == {'total_tokens': 40}
    assert result['review']['provider_attempted'] is True
    assert result['review']['original_generation'] == 'fpt_cloud_llm'
    assert result['review']['original_provider'] == 'FPT Cloud'
    assert result['review']['original_model'] == 'test-model'
    assert 'PRIVATE_REJECTED_DRAFT' not in json.dumps(result)


@pytest.mark.parametrize('evidence', [[], [{**EVIDENCE[0], 'url': 'https://[invalid'}],
                                      [{**EVIDENCE[0], 'text': 'Tiêm insulin 10 đơn vị.'}],
                                      [EVIDENCE[0], EVIDENCE[0]]])
def test_no_usable_evidence_abstains_within_revision_budget(evidence):
    result = review_and_revise(draft('Bạn mắc tiểu đường. [A]'), evidence)
    assert result['status'] == 'insufficient_evidence' and result['citations'] == []
    assert result['review']['passed'] and result['review']['status'] == 'abstained'
    assert result['review']['revision_count'] == 1
    assert len(result['review']['attempts']) == 2


def test_trusted_safety_path_bypasses_generator_and_evidence_requirements():
    safety = {'level': 'emergency', 'answer': 'Cần hỗ trợ y tế ngay.'}
    result = ExplanationAgent(None).run('', {}, {'safety': safety}, [])
    assert result['generation'] == 'safety_rule' and result['answer'] == safety['answer']
    assert result['review']['status'] == 'safety_override'
    assert result['review']['revision_count'] == 0
    assert result['review']['checks'] == {'safety_override': True}


def test_real_template_generator_runs_exactly_once(monkeypatch):
    monkeypatch.setenv('FPT_API_KEY', '')
    generator = EvidenceGenerator()
    original = generator.generate
    calls = []
    def counted(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)
    monkeypatch.setattr(generator, 'generate', counted)
    result = ExplanationAgent(generator).run('HbA1c là gì?', {}, {}, EVIDENCE)
    assert len(calls) == 1
    assert result['generation'] == 'template' and result['review']['passed']
    assert result['status'] == 'llm_not_configured' and result['review']['revision_count'] == 0
    assert result['review']['provider_attempted'] is False


def test_numeric_glucose_evidence_passes_real_template_without_revision(monkeypatch):
    monkeypatch.setenv('FPT_API_KEY', '')
    evidence = [{**EVIDENCE[0], 'text': 'Glucose 126 mg/dL là một giá trị xét nghiệm trong tài liệu.'}]
    result = ExplanationAgent(EvidenceGenerator()).run('Glucose là gì?', {}, {}, evidence)
    assert result['status'] == 'llm_not_configured'
    assert result['review']['passed'] and result['review']['revision_count'] == 0


def test_refusal_is_valid_without_citations_and_review_has_no_raw_content():
    value = {'answer': 'Chưa có đủ bằng chứng phù hợp. '+DISCLAIMER,
             'status': 'insufficient_evidence', 'citations': []}
    review = review_output(value, [])
    assert review['passed'] and all(review['checks'].values())
    assert 'answer' not in review


@pytest.mark.parametrize('value', [None, [], {'answer': 42, 'citations': [{'id': []}]}])
def test_malformed_provider_draft_abstains_without_type_error(value):
    result = review_and_revise(value, None)
    assert result['status'] == 'insufficient_evidence'
    assert result['review']['passed'] and result['review']['revision_count'] == 1


@pytest.mark.parametrize('fragments', ['Bạn\nbị tiểu đường.',
                                      'Bạn nên uống\nmetformin\n500 mg.'])
def test_rejoining_evidence_fragments_cannot_publish_a_new_unsafe_sentence(fragments):
    evidence = [{**EVIDENCE[0], 'text': fragments}]
    result = review_and_revise({'answer': 'broken', 'citations': [],
        'generation': 'test_candidate', 'status': 'test_candidate'}, evidence)
    assert result['answer'] == REFUSAL and result['citations'] == []
    assert result['status'] == 'insufficient_evidence'
    assert result['review']['passed'] and result['review']['status'] == 'abstained'
    assert result['review']['revision_count'] == 1
    assert len(result['review']['attempts']) == 2
    assert not unsafe_codes(result['answer'])


def test_failed_candidate_at_publication_gate_becomes_trusted_refusal():
    candidate = draft('PRIVATE_REJECTED_DRAFT HbA1c là xét nghiệm. [UNSEEN]')
    failed = review_output(candidate, EVIDENCE)
    assert not failed['passed'] and 'citation_mismatch' in failed['issue_codes']
    published, final, action = _publish_checked(candidate, failed)
    assert action == 'trusted_refusal_after_failed_revision'
    assert published['status'] == 'insufficient_evidence' and published['citations'] == []
    assert published['answer'] == REFUSAL and final['passed']
    assert failed['passed'] is False  # The rejected candidate verdict remains available to history.
    assert 'PRIVATE_REJECTED_DRAFT' not in json.dumps(published)
