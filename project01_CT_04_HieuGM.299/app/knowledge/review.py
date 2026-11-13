"""Bounded deterministic output review; lexical matching is not semantic truth validation."""
import re
from urllib.parse import urlparse
from app.agents.rules import normalize

DISCLAIMER = ('Thông tin chỉ phục vụ học tập và nghiên cứu, không phải chẩn đoán '
              'hoặc hướng dẫn tự điều chỉnh thuốc.')
REFUSAL = 'Chưa có đủ bằng chứng phù hợp để trả lời câu hỏi này. '+DISCLAIMER
SCOPE = ('Deterministic structure, citation/provenance, narrow safety patterns and lexical '
         'support heuristic; not medical validation or claim-level semantic verification.')
ID = r'[A-Za-z0-9_-]+'
STOP = set('va la cua cho cac mot nhung nay voi duoc co khong trong de khi theo tu '
           've da se can chi tai hoac cung nhu tren thong tin hoc tap nghien cuu phuc '
           'vu phai chan doan huong dan dieu chinh thuoc ban nguoi benh'.split())


def _sentences(text):
    return [x.strip() for x in re.split(r'(?<=[.!?;])\s+|\n+', text) if x.strip()]


def unsafe_codes(text):
    """Flag only explicit patterns; negation/condition guards are intentionally local."""
    issues = set()
    for sentence in _sentences(normalize(text)):
        diagnosis = re.search(r'\b(?:ban|anh|chi|ong|ba|benh nhan nay|you)\s+'
            r'(?:(?:da|chac chan|khong|dang|hoan toan)\s+){0,3}'
            r'(?:bi|mac|co|have|are)\s+(?:benh\s+|a\s+)?'
            r'(?:dai thao duong|tieu duong|diabetes|diabetic)\b', sentence)
        if diagnosis:
            prefix = sentence[:diagnosis.start()]
            guarded = re.search(r'(?:neu|if|khong the|khong duoc|khong khang dinh|'
                r'khong ket luan|khong co nghia|khong xac nhan|cannot|does not mean)'
                r'.{0,65}$', prefix)
            if not guarded:
                issues.add('personal_diagnosis')
        medicine = re.search(r'\b(?:insulin|metformin|glimepiride|gliclazide|'
                             r'glibenclamide|semaglutide|liraglutide|thuoc)\b', sentence)
        dose = re.search(r'\b\d+(?:[.,]\d+)?\s*(?:mg(?!/d[lL])\b|mcg\b|ug\b|'
                         r'ml\b|don vi\b|units?\b|iu\b|vien\b)', sentence)
        action = re.search(r'\b(?:tang|giam|ngung|tiem|uong|dung|take|inject)\b', sentence)
        guarded = re.search(r'\b(?:khong|chua|do not|never)\s+'
            r'(?:(?:nen|duoc|tu|y|hay|the)\s+){0,4}'
            r'(?:tang|giam|ngung|tiem|uong|dung|take|inject|ke don|tinh lieu)\b', sentence)
        directive = action and re.search(r'\b(?:ban nen|ban can|hay|you should|you must)\b', sentence)
        if medicine and (dose or directive) and not guarded:
            issues.add('medication_dosage')
    return sorted(issues)


def _valid_source(item):
    if (not isinstance(item, dict) or not isinstance(item.get('id'), str)
            or not re.fullmatch(ID, item['id'])):
        return False
    try:
        parsed = urlparse(str(item.get('url', '')))
        return bool(parsed.scheme == 'https' and parsed.hostname and not parsed.username
                    and not parsed.password and isinstance(item.get('text'), str))
    except ValueError:
        return False


def review_output(draft, evidence):
    """Return verdict metadata only; never retain a rejected draft in review records."""
    draft = draft if isinstance(draft, dict) else {}
    evidence = evidence if isinstance(evidence, list) else []
    answer = draft.get('answer')
    structure = isinstance(answer, str) and 10 <= len(answer) <= 10000
    answer = answer if isinstance(answer, str) else ''
    citations = draft.get('citations', [])
    citations = citations if isinstance(citations, list) else [None]
    sources = {x['id']: x for x in evidence
               if isinstance(x, dict) and isinstance(x.get('id'), str)}
    inline = re.findall(r'\[('+ID+r')\]', answer)
    cited = [x['id'] if isinstance(x, dict) and isinstance(x.get('id'), str)
             else None for x in citations]
    refusal = draft.get('status') == 'insufficient_evidence' and bool(re.search(
        r'(?:chua|khong) co du bang chung', normalize(answer)))
    aligned = (set(inline) == set(cited) and None not in cited and
               (bool(inline) or refusal) and all(x in sources for x in inline))
    provenance = all(_valid_source(sources.get(x)) and all(
        entry.get(k) == sources[x].get(k) for k in ('url', 'title', 'document_id', 'page')
        if k in entry) for x, entry in zip(cited, citations)) if aligned else False
    provenance = provenance and all(sum(isinstance(x, dict) and x.get('id') == identifier
        for x in evidence) == 1 for identifier in cited)
    normalized = normalize(answer)
    disclaimer = bool(re.search(r'hoc tap|nghien cuu|giao duc|tham khao', normalized) and
                      re.search(r'khong.{0,45}(?:chan doan|ke don|dieu chinh thuoc)', normalized))
    content = re.sub(r'\['+ID+r'\]', '', answer.replace(DISCLAIMER, ''))
    tokens = set(re.findall(r'\b[a-z]{2,}\b', normalize(content)))-STOP
    support = set(re.findall(r'\b[a-z]{2,}\b', normalize(' '.join(
        sources[x].get('text', '') for x in inline if x in sources))))-STOP
    ratio = len(tokens & support)/len(tokens) if tokens else 0.0
    safety = unsafe_codes(answer)
    checks = {'structure': structure, 'citation_alignment': aligned,
        'evidence_provenance': provenance, 'no_new_urls': not bool(re.search(r'https?://', answer)),
        'no_personal_diagnosis': 'personal_diagnosis' not in safety,
        'no_medication_dosage': 'medication_dosage' not in safety,
        'disclaimer': disclaimer, 'lexical_support': refusal or ratio >= .35}
    codes = {'structure':'invalid_structure', 'citation_alignment':'citation_mismatch',
        'evidence_provenance':'invalid_evidence_provenance', 'no_new_urls':'unapproved_url',
        'no_personal_diagnosis':'personal_diagnosis', 'no_medication_dosage':'medication_dosage',
        'disclaimer':'missing_disclaimer', 'lexical_support':'weak_lexical_support'}
    return {'passed': all(checks.values()), 'checks': checks,
        'issue_codes': [codes[k] for k, passed in checks.items() if not passed],
        'lexical_support_ratio': round(ratio, 4)}


def _extractive(evidence):
    evidence = evidence if isinstance(evidence, list) else []
    sources, paragraphs = [], []
    seen = set()
    for item in evidence:
        if not _valid_source(item) or item['id'] in seen or sum(
                isinstance(x, dict) and x.get('id') == item['id'] for x in evidence) != 1:
            continue
        seen.add(item['id'])
        safe = [segment for segment in _sentences(item['text'])
                if not unsafe_codes(segment) and not re.search(r'https?://|\['+ID+r'\]', segment)]
        if not safe:
            continue
        excerpt = ' '.join(safe)[:1800].strip()
        if (len(excerpt) < 10 or unsafe_codes(excerpt) or
                not (set(re.findall(r'\b[a-z]{2,}\b', normalize(excerpt)))-STOP)):
            continue
        paragraphs.append(excerpt+f" [{item['id']}]")
        sources.append({k: item.get(k) for k in ('id', 'title', 'url', 'document_id', 'page')})
        if len(paragraphs) == 2:
            break
    return {'answer': '\n\n'.join(paragraphs+[DISCLAIMER]) if paragraphs else REFUSAL,
        'citations': sources, 'generation': 'template', 'model': None,
        'status': 'revised_extractive' if paragraphs else 'insufficient_evidence'}


def _publish_checked(result, verdict):
    """A failed candidate never crosses the publication boundary."""
    if verdict['passed']:
        return result, verdict, 'none'
    published = {**result, 'answer': REFUSAL, 'citations': [], 'generation': 'template',
                 'status': 'insufficient_evidence', 'model': None}
    return published, review_output(published, []), 'trusted_refusal_after_failed_revision'


def review_and_revise(draft, evidence):
    """One review, at most one deterministic revision; never call a provider here."""
    draft = draft if isinstance(draft, dict) else {}
    result = {k: draft[k] for k in ('answer', 'citations', 'generation', 'status', 'model',
              'error', 'usage', 'citation_validation') if k in draft}
    initial = review_output(result, evidence)
    attempts = [{'attempt': 0, **initial}]
    revision_count = 0
    if not initial['passed']:
        revision_count = 1
        result.update(_extractive(evidence))
        final = review_output(result, evidence)
        attempts.append({'attempt': 1, **final})
    result, final, terminal_action = _publish_checked(result, attempts[-1])
    generation = draft.get('generation', 'unknown')
    attempted = generation == 'fpt_cloud_llm' or draft.get('status') == 'llm_unavailable'
    result['review'] = {'passed': final['passed'], 'final_passed': final['passed'],
        'initial_passed': initial['passed'], 'checks': final['checks'],
        'issue_codes': final['issue_codes'], 'initial_issue_codes': initial['issue_codes'],
        'revision_count': revision_count, 'max_revisions': 1, 'scope': SCOPE,
        'terminal_action': terminal_action,
        'terminal_verdict': final if terminal_action != 'none' else None,
        'status': ('abstained' if result.get('status') == 'insufficient_evidence' else
                   'revised' if revision_count else 'passed'), 'attempts': attempts,
        'original_generation': generation, 'original_provider': 'FPT Cloud' if attempted else None,
        'original_model': draft.get('model'), 'provider_attempted': attempted}
    return result


def safety_review():
    return {'passed': True, 'final_passed': True, 'initial_passed': True,
        'checks': {'safety_override': True}, 'issue_codes': [], 'initial_issue_codes': [],
        'revision_count': 0, 'max_revisions': 1, 'status': 'safety_override',
        'scope': 'Trusted Rule Agent safety output; evidence requirements intentionally bypassed.',
        'attempts': [{'attempt': 0, 'passed': True, 'issue_codes': [], 'safety_override': True}],
        'original_generation': 'safety_rule', 'original_provider': None,
        'original_model': None, 'provider_attempted': False}
