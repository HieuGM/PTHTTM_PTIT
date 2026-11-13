"""Bounded evidence selection; heuristics do not estimate clinical confidence."""
import re
import time
from app.agents.rules import normalize


VERSION = 'adaptive-evidence-2.1.1'
ALIASES = {'duong ba thang': 'hba1c', 'duong 3 thang': 'hba1c',
           'hb a1c': 'hba1c', 'an kieng': 'dinh duong',
           'tap the duc': 'van dong', 'dai duong': 'dai thao duong',
           'mo mat': 'nhin mo', 'duong mau luc doi': 'glucose doi',
           'duong huyet luc doi': 'glucose doi'}
STOP = set('toi ban cho giup giai thich phan anh dieu can nao the nhu khi voi cua '
           'nguoi benh mot cac hay tai sao ve nay duoc'.split())
GENERIC_TOPICS = {'du lieu', 'mo hinh', 'viet nam', 'my', 'gioi han', 'benh',
                  'nguon', 'khai niem', 'dinh nghia', 'train', 'test'}


def rewrite_query(question):
    """Normalize known colloquial aliases; no LLM or new factual assertions."""
    value = normalize(question)
    changed = False
    for source, target in ALIASES.items():
        value, count = re.subn(r'\b'+re.escape(source)+r'\b', target, value)
        changed = changed or bool(count)
    return value if changed else question


def tokens(text):
    return {x for x in re.findall(r'\b\w+\b', normalize(text))
            if len(x) >= 3 and x not in STOP}


class AdaptiveRetrieval:
    version = VERSION
    max_attempts = 3

    def __init__(self, kb):
        self.kb = kb

    def _anchors(self, question):
        concepts = set(self.kb.entity_ids(question))
        if concepts:
            return concepts
        query, matched = normalize(question), set()
        for card in self.kb.cards:
            for topic in card.get('topics', []):
                term = normalize(topic).strip()
                specific = len(term) >= 4 or (len(term) >= 3 and topic.isupper())
                if specific and not term.isdigit() and term not in GENERIC_TOPICS:
                    if re.search(r'\b'+re.escape(term)+r'\b', query):
                        matched.add('card:'+card['id'])
        return matched

    def _supported(self, hits, anchors, query_tokens):
        output, covered, overlaps = [], set(), set()
        known = self.kb.source_index
        for hit in hits[:4]:
            source = known.get(hit.get('id'))
            if not source or not isinstance(hit.get('text'), str) or not hit['text'].strip():
                continue
            if not isinstance(hit.get('url'), str) or not hit['url'].startswith('https://'):
                continue
            if hit['url'] != source.get('url') or hit['text'] != source.get('text'):
                continue
            if any(hit.get(k) != source.get(k) for k in ('document_id', 'page')):
                continue
            common = set(source.get('concept_ids', [])).intersection(anchors)
            if 'card:'+source['id'] in anchors:
                common.add('card:'+source['id'])
            overlap = tokens(hit.get('title', '')+' '+hit['text']).intersection(query_tokens)
            if not common or not overlap:
                continue
            output.append(hit)
            covered.update(common)
            overlaps.update(overlap)
        return output, covered, len(overlaps)

    def run(self, question):
        attempts, best, best_rank = [], None, (-1, -1, -1)

        def result(evidence, reason, selected=None, exhausted=False):
            return {'evidence': evidence, 'retrieval': {'policy_version': VERSION,
                'sufficient': selected is not None, 'reason': reason,
                'selected_attempt': selected, 'best_attempt': best, 'attempts': attempts,
                'graph_backend': next((a['graph_backend'] for a in reversed(attempts)
                    if a.get('graph_backend') not in {None, 'not_queried'}), 'not_used'),
                'max_attempts': self.max_attempts, 'exhausted': exhausted,
                'scope': 'Heuristic anchor/provenance support only; not clinical confidence '
                         'or claim-level verification.'}}

        if not isinstance(question, str) or not question.strip():
            return result([], 'invalid_query')
        canonical = rewrite_query(question)
        try:
            anchors = self._anchors(canonical)
        except (OSError, RuntimeError, ValueError, KeyError, TypeError):
            return result([], 'query_interpretation_error')
        if not anchors:
            return result([], 'no_domain_anchor')
        query_tokens = tokens(canonical)
        plan = [(question, 'hybrid_graph', 'original')]
        if canonical != question:
            plan.append((canonical, 'hybrid_graph', 'alias_rewrite'))
        plan.append((canonical, 'lexical', 'lexical_fallback'))
        for query, method, strategy in plan[:self.max_attempts]:
            started = time.perf_counter()
            error_code = None
            try:
                hits = self.kb.retrieve(query, k=4, method=method)
                supported, covered, overlap = self._supported(hits, anchors, query_tokens)
            except (OSError, RuntimeError, ValueError, KeyError, TypeError) as error:
                hits, supported, covered, overlap = [], [], set(), 0
                error_code = type(error).__name__
            sufficient = bool(supported) and covered == anchors
            reason = ('anchor_support' if sufficient else 'retrieval_error' if error_code
                      else 'insufficient_anchor_support')
            attempt = {'attempt': len(attempts)+1, 'method': method, 'query_strategy': strategy,
                'graph_backend': (getattr(self.kb, 'last_graph_backend', 'unknown')
                    if method == 'hybrid_graph' else 'not_queried'),
                'candidate_count': len(hits), 'supported_count': len(supported),
                'candidate_ids': [h.get('id') for h in hits[:4]],
                'required_anchor_count': len(anchors), 'covered_anchor_count': len(covered),
                'anchor_coverage': len(covered)/len(anchors), 'lexical_overlap': overlap,
                'sufficient': sufficient, 'reason': reason,
                'duration_ms': round((time.perf_counter()-started)*1000, 3)}
            if error_code:
                attempt['error_code'] = error_code
            attempts.append(attempt)
            rank = (len(covered), overlap, len(supported))
            if rank > best_rank:
                best, best_rank = attempt['attempt'], rank
            if sufficient:
                return result(supported[:4], reason, attempt['attempt'])
        return result([], 'attempt_budget_exhausted', exhausted=True)
