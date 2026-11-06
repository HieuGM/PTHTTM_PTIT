"""Document + medical KG retrieval, with explicit Neo4j/cache provenance."""
import json
import os
from pathlib import Path
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize as unit_rows
from app.agents.rules import normalize
from .graph_builder import identify
from .neo4j_backend import Neo4jGraph
from .store import materialize, cached_evidence


class KnowledgeBase:
    def __init__(self, root):
        self.root = Path(root)
        folder = self.root/'app/knowledge'
        self.cards = json.loads((folder/'cards.json').read_text(encoding='utf-8'))
        self.corpus = json.loads((folder/'corpus.json').read_text(encoding='utf-8'))
        self.items = self.corpus['chunks']
        self.source_index = {item['id']: item for item in self.items}
        self.concepts = self.corpus['graph']['concepts']
        self.concept_index = {item['id']: item for item in self.concepts}
        directory = Path(os.getenv('APP_DATA_DIR', str(self.root/'runtime')))
        directory.mkdir(parents=True, exist_ok=True)
        self.db_path = directory/'knowledge.sqlite3'
        materialize(self.db_path, self.cards, self.corpus)
        self.neo4j = Neo4jGraph()
        self.last_graph_backend = self.neo4j.backend
        documents = [self.index_text(item) for item in self.items]
        self.vectorizer = TfidfVectorizer(preprocessor=normalize, ngram_range=(1, 2),
            sublinear_tf=True, token_pattern=r'(?u)\b\w+\b', max_features=14000)
        self.matrix = self.vectorizer.fit_transform(documents)
        self.char_vectorizer = TfidfVectorizer(preprocessor=normalize, analyzer='char_wb',
            ngram_range=(3, 5), sublinear_tf=True, max_features=16000)
        self.char_matrix = self.char_vectorizer.fit_transform(documents)
        self.svd = TruncatedSVD(n_components=min(32, len(self.items)-1, self.matrix.shape[1]-1), random_state=42)
        self.latent = unit_rows(self.svd.fit_transform(self.matrix))

    def index_text(self, item):
        tags = ' '.join(' '.join(self.concept_index[c]['aliases']) for c in item.get('concept_ids', []))
        return item['title']+' '+item['text']+' '+tags

    def entity_ids(self, question):
        identifiers = identify(question, self.concepts)
        specific = [item for item in identifiers if item not in {'diabetes', 'glucose'}]
        return specific or identifiers

    def graph_evidence(self, identifiers, limit=150):
        result = self.neo4j.evidence(identifiers, limit=limit)
        if result is not None:
            self.last_graph_backend = 'neo4j'
            return {**result, 'backend': 'neo4j'}
        self.last_graph_backend = 'sqlite_cache'
        return {**cached_evidence(self.db_path, identifiers, limit), 'backend': 'sqlite_cache'}

    def retrieve(self, question, k=3, method='hybrid_graph'):
        if method not in {'lexical', 'semantic', 'hybrid_graph'}:
            raise ValueError('method must be lexical, semantic or hybrid_graph')
        k = max(1, min(int(k), 10))
        entities = self.entity_ids(question)
        expanded = question+' '+' '.join(' '.join(self.concept_index[e]['aliases']) for e in entities)
        query = self.vectorizer.transform([expanded])
        word = (self.matrix @ query.T).toarray().ravel()
        char = (self.char_matrix @ self.char_vectorizer.transform([expanded]).T).toarray().ravel()
        semantic = np.maximum((self.latent @ unit_rows(self.svd.transform(query)).T).ravel(), 0)
        graph = {'chunk_ids': [], 'relations': [], 'backend': self.last_graph_backend}
        if method == 'lexical':
            scores = word
        elif method == 'semantic':
            scores = semantic
        else:
            graph = self.graph_evidence(entities)
            candidates = set(graph['chunk_ids'])
            scores = .5*word+.25*char+.25*semantic
            for i, item in enumerate(self.items):
                if item['id'] in candidates and word[i] > .015:
                    scores[i] += .055
                if set(item.get('concept_ids', [])).intersection(entities):
                    scores[i] += .025
        for i, item in enumerate(self.items):
            if item['source_type'] == 'curated_card' and word[i] > .03:
                scores[i] += .045
        output = []
        for i in np.argsort(-scores, kind='stable'):
            if len(output) >= k or scores[i] < .09:
                break
            if word[i] < .015 and char[i] < .03:
                continue
            item = self.items[i]
            paths = [r for r in graph['relations'] if r.get('evidence_chunk_id') == item['id'] or
                     r.get('source') in item.get('concept_ids', []) and r.get('target') in entities]
            output.append({**item, 'score': round(float(scores[i]), 6), 'retrieval_method': method,
                'graph_backend': graph['backend'], 'matched_entities': entities, 'graph_paths': paths[:6]})
        return output

    def inventory(self):
        graph = self.corpus['graph']
        downloaded = [d for d in self.corpus['documents'] if d['ingestion'] == 'downloaded']
        return {'cards': len(self.cards), 'documents': len(downloaded),
            'reference_documents': len(self.corpus['documents'])-len(downloaded),
            'chunks': len(self.items), 'concepts': len(graph['concepts']), 'relations': len(graph['relations']),
            'mentions': len(graph['mentions']), 'storage': 'SQLite evidence cache', 'language': 'vi/en',
            'retriever': 'word TF-IDF + character TF-IDF + LSA32 + graph evidence',
            'semantic_method': 'latent semantic analysis; not a neural embedding model',
            'graph_backend': self.last_graph_backend, 'graph_status': self.neo4j.status,
            'corpus_version': self.corpus['version'],
            'pdf_pages': sum(d.get('page_count') or 0 for d in downloaded)}

    def graph_data(self, limit=500):
        graph = self.corpus['graph']
        return {'nodes': [{**c, 'type': c['kind']} for c in graph['concepts']][:limit],
            'edges': [{**r, 'label': r['predicate']} for r in graph['relations']][:limit],
            'backend': self.last_graph_backend, 'status': self.neo4j.status, 'stats': self.inventory(),
            'visualization_origin': 'packaged source-grounded corpus snapshot; live Neo4j used for retrieval when configured',
            'relation_semantics': 'source-grounded educational evidence, not diagnosis'}

    def close(self):
        self.neo4j.close()
