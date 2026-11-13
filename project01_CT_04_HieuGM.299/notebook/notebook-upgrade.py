"""Show implemented/configured/executed features and test bounded adaptive decisions."""
from app.capabilities import inventory, VERSION
from app.agents.contracts import Context
from app.knowledge.review import review_and_revise

capabilities = inventory(system.kb, system.generator)
capability_rows = [{**{k: item[k] for k in ('id', 'name', 'agent', 'implemented', 'endpoint', 'scope', 'demo')},
                    'source': item['source']['path']+' :: '+item['source']['symbol']}
                   for item in capabilities['features']]
display(pd.DataFrame(capability_rows))
display({'system_version': VERSION, 'configured_backends': capabilities['configured_backends'],
         'budgets': capabilities['budgets'], 'usage_note': capabilities['usage_note']})
upgrade_checks = []


def upgrade_verified(name, condition):
    assert condition, name
    upgrade_checks.append(name)


UPGRADE_EXAMPLES = {}
for case, question in [('normal', 'HbA1c là gì?'),
                       ('rewrite', 'Mờ mắt là gì?'),
                       ('abstain', 'Ai vô địch bóng đá thế giới?')]:
    item = system.report('pima', FEATURES, question)
    UPGRADE_EXAMPLES[case] = item
    report, used = item['report'], item['feature_usage']
    retrieval, quality = report['retrieval'], report['quality']
    upgrade_verified(case+': bounded retrieval', len(retrieval['attempts']) <= 3)
    upgrade_verified(case+': bounded review', quality['revision_count'] <= 1 and len(quality['attempts']) <= 2)
    upgrade_verified(case+': final review', quality['passed'])
    upgrade_verified(case+': eight outer messages', len(item['messages']) == 8)
    upgrade_verified(case+': independent call timing', all(
        0 <= message['duration_ms'] <= message['elapsed_ms']+.02 for message in item['messages']))
    upgrade_verified(case+': decision trace', len(item['decision_trace']) == len(item['messages']))
    upgrade_verified(case+': explicit unavailable technologies', not any(
        used[name] for name in ('rl_policy', 'neural_embedding', 'langgraph', 'streaming')))
    if not USE_FPT:
        upgrade_verified(case+': no provider called', not used['fpt_called'])
    display(Markdown('**'+case+'** — '+question))
    display({'status': item['status'], 'retrieval': retrieval, 'quality': quality, 'feature_usage': used})
    display(pd.DataFrame(item['decision_trace']))

normal = UPGRADE_EXAMPLES['normal']['report']
rewrite = UPGRADE_EXAMPLES['rewrite']['report']
abstain = UPGRADE_EXAMPLES['abstain']['report']
upgrade_verified('normal: one sufficient retrieval', normal['retrieval']['sufficient'] and
                 len(normal['retrieval']['attempts']) == 1)
upgrade_verified('rewrite: additional retrieval', rewrite['retrieval']['sufficient'] and
                 len(rewrite['retrieval']['attempts']) > 1)
upgrade_verified('rewrite: alias decision recorded', any(
    attempt['query_strategy'] == 'alias_rewrite' for attempt in rewrite['retrieval']['attempts']))
upgrade_verified('abstain: no unrelated evidence', not abstain['retrieval']['sufficient'] and
                 abstain['retrieved_evidence'] == [])
upgrade_verified('abstain: explicit refusal', abstain['explanation']['status'] == 'insufficient_evidence')
if not USE_FPT:
    upgrade_verified('normal: template label retained', normal['explanation']['status'] == 'llm_not_configured')

# These deliberately unsafe drafts are test candidates, never attributed to a live provider.
evidence = normal['retrieved_evidence']
source = evidence[0]
for code, sentence in [('personal_diagnosis', 'Bạn chắc chắn mắc bệnh tiểu đường.'),
                       ('medication_dosage', 'Bạn nên tiêm insulin 10 đơn vị.')]:
    draft = {'answer': sentence+' ['+source['id']+']', 'generation': 'test_candidate',
             'status': 'test_candidate', 'citations': normal['explanation']['citations'], 'model': None}
    checked = review_and_revise(draft, evidence)
    review = checked['review']
    upgrade_verified(code+': initial rejection', not review['initial_passed'] and
                     code in review['initial_issue_codes'])
    upgrade_verified(code+': one revision and final pass', review['revision_count'] == 1 and review['passed'])
    upgrade_verified(code+': revision never invokes provider', not review['provider_attempted'])
    display({'test_candidate': code, 'review': review, 'final_generation': checked['generation']})

# An explicit contract check distinguishes a call duration from its cumulative timestamp.
timing_context = Context('timing-contract-check', started=time.perf_counter()-1)
timing_message = timing_context.emit('ContractCheck', 'ok', {}, duration_ms=2.5)
upgrade_verified('timing: duration is not elapsed', timing_message['duration_ms'] == 2.5 and
                 timing_message['elapsed_ms'] >= 900)
upgrade_summary = {'system_version': VERSION, 'passed': len(upgrade_checks), 'checks': upgrade_checks,
    'examples': {name: {'retrieval_attempts': len(value['report']['retrieval']['attempts']),
                        'feature_usage': value['feature_usage']} for name, value in UPGRADE_EXAMPLES.items()},
    'scope': 'Actual local model/corpus decisions plus labeled unsafe test candidates; no live provider evidence.'}
(ROOT/'results/notebook-upgrade-validation.json').write_text(
    json.dumps(upgrade_summary, ensure_ascii=False, indent=2), encoding='utf-8')
display(upgrade_summary)
