"""SQLite KB and lexical retrieval; index built from versioned authored cards."""
import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from app.agents.rules import normalize


class KnowledgeBase:
    def __init__(self, root):
        self.root = Path(root)
        self.cards = json.loads((self.root / "app/knowledge/cards.json").read_text(encoding="utf-8"))
        if isinstance(self.cards, dict):
            self.cards = self.cards.get("cards", [])
        self.vectorizer = TfidfVectorizer(preprocessor=normalize, ngram_range=(1, 2), sublinear_tf=True,
                                         token_pattern=r"(?u)\b\w+\b")
        self.matrix = self.vectorizer.fit_transform([c["title"] + " " + " ".join(c["topics"]) + " " + c["text"] for c in self.cards])
        directory = Path(os.getenv("APP_DATA_DIR", str(self.root / "runtime")))
        directory.mkdir(parents=True, exist_ok=True)
        self.db_path = directory / "knowledge.sqlite3"
        with closing(sqlite3.connect(self.db_path)) as db:
            db.execute("CREATE TABLE IF NOT EXISTS cards(id TEXT PRIMARY KEY, title TEXT, content TEXT, url TEXT)")
            db.execute("DELETE FROM cards")
            db.executemany("INSERT INTO cards VALUES (?,?,?,?)", [(c["id"], c["title"], c["text"], c["url"]) for c in self.cards])
            db.commit()

    def retrieve(self, question, k=3):
        query = self.vectorizer.transform([question])
        scores = (self.matrix @ query.T).toarray().ravel()
        order = np.argsort(-scores)[:k]
        return [{**self.cards[i], "score": round(float(scores[i]), 5)} for i in order if scores[i] >= .09]

    def inventory(self):
        with closing(sqlite3.connect(self.db_path)) as db:
            n = db.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
        return {"cards": n, "storage": "SQLite", "retriever": "TF-IDF unigram + bigram", "language": "vi"}
