"""Actual parameterized Neo4j graph queries, with explicit portable-cache status."""
import os


class Neo4jGraph:
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', '').strip()
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', '')
        self.database = os.getenv('NEO4J_DATABASE', 'neo4j')
        self.driver = None
        self.status = 'not_configured'
        if self.uri and self.password:
            try:
                from neo4j import GraphDatabase
                self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password),
                    connection_timeout=4, connection_acquisition_timeout=4, max_connection_pool_size=4)
                self.driver.verify_connectivity()
                self.status = 'connected'
            except Exception as error:
                self.status = 'unavailable:'+type(error).__name__
                if self.driver:
                    self.driver.close()
                self.driver = None

    @property
    def backend(self):
        return 'neo4j' if self.driver is not None else 'sqlite_cache'

    def evidence(self, concepts, limit=100):
        if self.driver is None:
            return None
        try:
            with self.driver.session(database=self.database, default_access_mode='READ') as session:
                relations = [dict(row) for row in session.run('''
                    MATCH (a:Concept)-[r:MEDICAL_RELATION]->(b:Concept)
                    WHERE a.id IN $ids OR b.id IN $ids
                    RETURN a.id AS source,b.id AS target,r.id AS id,r.predicate AS predicate,
                      r.evidence_chunk_id AS evidence_chunk_id,r.document_id AS document_id,
                      r.url AS url,r.page AS page
                    ORDER BY id LIMIT $limit''', ids=list(concepts), limit=limit)]
                neighbors = set(concepts)
                for relation in relations:
                    neighbors.update([relation['source'], relation['target']])
                chunks = [row['id'] for row in session.run('''
                    MATCH (c:Chunk)-[:MENTIONS]->(e:Concept)
                    WHERE e.id IN $ids RETURN DISTINCT c.id AS id ORDER BY id LIMIT $limit
                    ''', ids=sorted(neighbors), limit=limit)]
            self.status = 'connected'
            return {'chunk_ids': chunks, 'relations': relations}
        except Exception as error:
            self.status = 'query_failed:'+type(error).__name__
            return None

    def initialize(self, corpus):
        if self.driver is None:
            raise RuntimeError('Neo4j unavailable: '+self.status)
        from .graph_builder import cypher_seed
        # Quote-aware statement splitter keeps source semicolons inside strings.
        script = cypher_seed(corpus)
        statements, current, quoted, escape = [], [], False, False
        for line in script.splitlines(keepends=True):
            if line.startswith('//'):
                continue
            for char in line:
                if char == '"' and not escape:
                    quoted = not quoted
                if char == ';' and not quoted:
                    statements.append(''.join(current))
                    current = []
                else:
                    current.append(char)
                escape = char == '\\' and not escape
        with self.driver.session(database=self.database) as session:
            for statement in statements:
                if statement.strip():
                    session.run(statement).consume()
            counts = dict(session.run('''MATCH (n) WITH count(n) AS nodes
                OPTIONAL MATCH ()-[r]->() RETURN nodes,count(r) AS edges''').single())
        return counts

    def close(self):
        if self.driver:
            self.driver.close()
