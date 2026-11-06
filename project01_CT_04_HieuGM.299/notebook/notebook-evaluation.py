"""Retain all authored development cases, compare three actual retrieval methods."""
evaluation_rows = []
for method in ('lexical', 'semantic', 'hybrid_graph'):
    for item in EVALUATION_QUESTIONS:
        hits = system.kb.retrieve(item['question'], k=3, method=method)
        identifiers = [hit['id'] for hit in hits]
        rank = next((i+1 for i, identifier in enumerate(identifiers)
                     if identifier in item['expected_ids']), None)
        evaluation_rows.append({'method':method, 'id':item['id'], 'question':item['question'],
            'answerable':item['answerable'], 'expected_ids':item['expected_ids'],
            'retrieved_ids':identifiers, 'first_relevant_rank':rank,
            'reciprocal_rank':1/rank if rank else 0,
            'all_source_ids_valid':all(identifier in system.kb.source_index for identifier in identifiers)})
evaluation_table = pd.DataFrame(evaluation_rows)
positive = evaluation_table[evaluation_table.answerable].copy()
positive['recall_at_1'] = positive.first_relevant_rank.eq(1)
positive['recall_at_3'] = positive.first_relevant_rank.notna()
display(positive.groupby('method')[['recall_at_1','recall_at_3','reciprocal_rank']].mean())
display(evaluation_table)
(ROOT/'results/notebook-retrieval-evaluation.json').write_text(json.dumps({
    'scope':'Authored development queries, not independent medical validation',
    'cases':evaluation_rows}, ensure_ascii=False, indent=2), encoding='utf-8')

# Eight additional source-specific cases are reported separately, never tuned here.
source_rows = []
for method in ('lexical', 'semantic', 'hybrid_graph'):
    for item in SOURCE_CHECK_QUESTIONS['queries']:
        hits = system.kb.retrieve(item['question'], k=3, method=method)
        rank = next((i+1 for i, hit in enumerate(hits)
            if hit['document_id'] in item['expected_document_ids']), None)
        source_rows.append({**item, 'method':method,
            'retrieved_document_ids':[h['document_id'] for h in hits],
            'first_relevant_rank':rank, 'recall_at_3':rank is not None,
            'reciprocal_rank':1/rank if rank else 0})
source_table = pd.DataFrame(source_rows)
display(source_table.groupby('method')[['recall_at_3','reciprocal_rank']].mean())
display(source_table)
(ROOT/'results/notebook-source-check-evaluation.json').write_text(json.dumps({
    'scope':SOURCE_CHECK_QUESTIONS['scope'], 'cases':source_rows}, ensure_ascii=False, indent=2), encoding='utf-8')
