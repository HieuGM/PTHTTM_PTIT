"""Initialize actual Neo4j from the reproducible, source-grounded corpus."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.knowledge.neo4j_backend import Neo4jGraph
from dotenv import load_dotenv

load_dotenv(ROOT/'.env', override=False)
graph = Neo4jGraph()
try:
    corpus = json.loads((ROOT/'app/knowledge/corpus.json').read_text(encoding='utf-8'))
    counts = graph.initialize(corpus)
    examples = graph.evidence(['a1c', 'type2'])
    result = {'backend': graph.backend, 'status': graph.status, 'counts': counts,
        'example_concepts': ['a1c', 'type2'], 'retrieved_chunks': len(examples['chunk_ids']),
        'retrieved_relations': len(examples['relations']), 'database': graph.database}
    (ROOT/'results/neo4j-verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))
finally:
    graph.close()
