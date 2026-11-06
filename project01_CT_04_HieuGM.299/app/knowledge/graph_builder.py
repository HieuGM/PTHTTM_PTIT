"""Build a source-grounded medical concept graph and executable Neo4j seed."""
import hashlib
import json
import re
from pathlib import Path
from app.agents.rules import normalize


def identify(text, concepts):
    value = normalize(text)
    return [c['id'] for c in concepts if any(
        re.search(r'(?<!\w)'+re.escape(normalize(alias))+r'(?!\w)', value)
        for alias in c['aliases'])]


def build_graph(root, documents, chunks):
    concepts = json.loads((Path(root)/'app/knowledge/ontology.json').read_text(encoding='utf-8'))
    mentions, relations = [], []
    for chunk in chunks:
        chunk['concept_ids'] = identify(chunk['title']+' '+chunk['text'], concepts)
        mentions.extend({'chunk_id': chunk['id'], 'concept_id': item} for item in chunk['concept_ids'])
    # Curated relation definitions + source-text predicates. Edges are created only
    # when the actual evidence passage contains all required terms/patterns.
    patterns = [
        ('type1', 'IS_A', 'diabetes', 'WEB01', r'type 1 diabetes'),
        ('type2', 'IS_A', 'diabetes', 'WEB01', r'type 2 diabetes'),
        ('gestational', 'IS_A', 'diabetes', 'WEB01', r'gestational diabetes'),
        ('type1', 'REQUIRES', 'insulin', 'WEB01', r'type 1.*?(?:need|require).*?insulin'),
        ('type2', 'RISK_ASSOCIATION', 'obesity', 'WEB01', r'factors.*?type 2.*?overweight'),
        ('type2', 'RISK_ASSOCIATION', 'inactivity', 'WEB01', r'factors.*?type 2.*?not getting enough exercise'),
        ('type2', 'RISK_ASSOCIATION', 'family_history', 'WEB01', r'factors.*?type 2.*?genetics'),
    ]
    for target in ['thirst', 'urination', 'fatigue', 'blurred_vision', 'weight_loss']:
        patterns.append(('diabetes', 'MAY_HAVE_SYMPTOM', target, 'WEB01', r'symptoms of diabetes include'))
    for target in ['kidney', 'eye', 'neuropathy', 'foot']:
        patterns.append(('diabetes', 'MAY_HAVE_COMPLICATION', target, 'WEB01', r'(?:diabetes.*?damage|people with diabetes.*?risk|diabetes.*?vision|people with diabetes.*?feet)'))
    for target in ['a1c', 'fasting', 'ogtt']:
        patterns.append(('diabetes', 'DIAGNOSED_USING', target, 'WEB05', r'(?:diagnos|diabetes tests)'))
    for subject, predicate, target, document, pattern in patterns:
        candidates = [c for c in chunks if c['document_id'] == document and
            target in c['concept_ids'] and re.search(pattern, normalize(c['text']), re.S)]
        if not candidates:
            continue
        passage = min(candidates, key=lambda item: len(item['text']))
        identity = subject+'|'+predicate+'|'+target
        relations.append({'id': hashlib.sha256(identity.encode()).hexdigest()[:16],
            'source': subject, 'target': target, 'predicate': predicate,
            'evidence_chunk_id': passage['id'], 'document_id': passage['document_id'],
            'url': passage['url'], 'page': passage['page'],
            'evidence_quote': passage['text'],
            'method': 'curated relation rule verified against the cited source passage'})
    return {'concepts': concepts, 'mentions': mentions, 'relations': relations}


def cypher_value(value):
    if isinstance(value, dict):
        return '{'+', '.join(key+': '+cypher_value(v) for key, v in value.items())+'}'
    if isinstance(value, list):
        return '['+', '.join(cypher_value(v) for v in value)+']'
    return json.dumps(value, ensure_ascii=False)


def cypher_seed(corpus):
    statements = [f'CREATE CONSTRAINT {kind.lower()}_id IF NOT EXISTS FOR (n:{kind}) REQUIRE n.id IS UNIQUE'
                  for kind in ['Concept', 'Document', 'Chunk']]
    documents = [{k: d.get(k) for k in ['id', 'title', 'url', 'type', 'sha256', 'page_count', 'ingestion']}
                 for d in corpus['documents']]
    chunks = [{k: c.get(k) for k in ['id', 'document_id', 'title', 'text', 'url', 'page', 'source_type']}
              for c in corpus['chunks']]
    statements += [
        'UNWIND '+cypher_value(documents)+' AS row MERGE (n:Document {id:row.id}) SET n += row',
        'UNWIND '+cypher_value(corpus['graph']['concepts'])+' AS row MERGE (n:Concept {id:row.id}) SET n += row',
        'UNWIND '+cypher_value(chunks)+' AS row MERGE (n:Chunk {id:row.id}) SET n += row '
        'WITH n,row MATCH (d:Document {id:row.document_id}) MERGE (d)-[:HAS_CHUNK]->(n)',
        'UNWIND '+cypher_value(corpus['graph']['mentions'])+' AS row '
        'MATCH (c:Chunk {id:row.chunk_id}),(e:Concept {id:row.concept_id}) MERGE (c)-[:MENTIONS]->(e)',
        'UNWIND '+cypher_value(corpus['graph']['relations'])+' AS row '
        'MATCH (a:Concept {id:row.source}),(b:Concept {id:row.target}),'
        '(c:Chunk {id:row.evidence_chunk_id}) '
        'MERGE (a)-[r:MEDICAL_RELATION {id:row.id}]->(b) '
        'SET r.predicate=row.predicate,r.evidence_chunk_id=row.evidence_chunk_id,'
        'r.document_id=row.document_id,r.url=row.url,r.page=row.page,r.method=row.method '
        'MERGE (c)-[:SUPPORTS]->(a) MERGE (c)-[:SUPPORTS]->(b)']
    return '// DiaCare evidence-grounded KG; regenerated from source corpus.\n'+ ';\n\n'.join(statements)+';\n'
