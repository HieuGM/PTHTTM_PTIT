"""Versioned SQLite evidence cache; never stores user health requests."""
from contextlib import closing
import json
import sqlite3


def materialize(path, cards, corpus):
    with closing(sqlite3.connect(path)) as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS cards(id TEXT PRIMARY KEY,title TEXT,content TEXT,url TEXT);
        CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY,title TEXT,url TEXT,source_type TEXT,
          ingestion TEXT,sha256 TEXT,page_count INTEGER,metadata_json TEXT);
        CREATE TABLE IF NOT EXISTS chunks(id TEXT PRIMARY KEY,document_id TEXT,title TEXT,
          content TEXT,url TEXT,page INTEGER,source_type TEXT,text_sha256 TEXT);
        CREATE TABLE IF NOT EXISTS concepts(id TEXT PRIMARY KEY,label TEXT,kind TEXT,aliases_json TEXT);
        CREATE TABLE IF NOT EXISTS mentions(chunk_id TEXT,concept_id TEXT,PRIMARY KEY(chunk_id,concept_id));
        CREATE TABLE IF NOT EXISTS relations(id TEXT PRIMARY KEY,source TEXT,predicate TEXT,target TEXT,
          evidence_chunk_id TEXT,document_id TEXT,url TEXT,page INTEGER,evidence_quote TEXT);
        ''')
        for table in ['cards', 'documents', 'chunks', 'concepts', 'mentions', 'relations']:
            db.execute('DELETE FROM '+table)
        db.executemany('INSERT INTO cards VALUES(?,?,?,?)',
            [(c['id'], c['title'], c['text'], c['url']) for c in cards])
        db.executemany('INSERT INTO documents VALUES(?,?,?,?,?,?,?,?)',
            [(d['id'], d['title'], d['url'], d['type'], d['ingestion'], d.get('sha256'),
              d.get('page_count'), json.dumps(d, ensure_ascii=False)) for d in corpus['documents']])
        db.executemany('INSERT INTO chunks VALUES(?,?,?,?,?,?,?,?)',
            [(c['id'], c['document_id'], c['title'], c['text'], c['url'], c.get('page'),
              c['source_type'], c['text_sha256']) for c in corpus['chunks']])
        graph = corpus['graph']
        db.executemany('INSERT INTO concepts VALUES(?,?,?,?)',
            [(c['id'], c['label'], c['kind'], json.dumps(c['aliases'], ensure_ascii=False)) for c in graph['concepts']])
        db.executemany('INSERT INTO mentions VALUES(?,?)',
            [(r['chunk_id'], r['concept_id']) for r in graph['mentions']])
        db.executemany('INSERT INTO relations VALUES(?,?,?,?,?,?,?,?,?)',
            [(r['id'], r['source'], r['predicate'], r['target'], r['evidence_chunk_id'],
              r['document_id'], r['url'], r.get('page'), r['evidence_quote']) for r in graph['relations']])
        db.commit()


def cached_evidence(path, concepts, limit=100):
    if not concepts:
        return {'chunk_ids': [], 'relations': []}
    placeholders = ','.join('?' for _ in concepts)
    with closing(sqlite3.connect(path)) as db:
        db.row_factory = sqlite3.Row
        relations = [dict(row) for row in db.execute(
            f'SELECT * FROM relations WHERE source IN ({placeholders}) OR target IN ({placeholders})',
            list(concepts)+list(concepts))]
        neighbors = set(concepts)
        for relation in relations:
            neighbors.update([relation['source'], relation['target']])
        placeholders = ','.join('?' for _ in neighbors)
        rows = db.execute(f'SELECT DISTINCT chunk_id FROM mentions WHERE concept_id IN ({placeholders}) ORDER BY chunk_id LIMIT ?',
                          [*sorted(neighbors), limit]).fetchall()
    return {'chunk_ids': [row['chunk_id'] for row in rows], 'relations': relations}
