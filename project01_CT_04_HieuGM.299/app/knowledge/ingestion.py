"""Download genuine source bytes, extract page text, and retain provenance."""
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader


def digest(value):
    return hashlib.sha256(value).hexdigest()


def extract_pages(raw, kind):
    if kind == 'pdf':
        if not raw.startswith(b'%PDF'):
            raise ValueError('Expected PDF signature, received another content type')
        return [(i+1, page.extract_text() or '') for i, page in enumerate(PdfReader(io.BytesIO(raw)).pages)]
    soup = BeautifulSoup(raw, 'html.parser')
    for node in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'noscript']):
        node.decompose()
    # Vinmec's main element also contains unrelated article recommendations.
    body = (soup.select_one('#main-article') or
            soup.select_one('article, main, [role="main"], .sf-detail-body-wrapper') or soup.body or soup)
    for node in body.select('.table-of-contents'):
        node.decompose()
    return [(None, body.get_text('\n', strip=True))]


def web_metadata(raw):
    """Preserve visible publication metadata; never infer a date from crawl time."""
    soup = BeautifulSoup(raw, 'html.parser')
    dates = soup.select_one('.content-date')
    return {'source_updated_label': dates.get_text(' ', strip=True) if dates else None}


def clean_text(text):
    lines = [re.sub(r'\s+', ' ', line).strip() for line in text.replace('\x00', '').splitlines()]
    return '\n'.join(line for line in lines if line)


def text_chunks(text, size=1100, overlap=130):
    """Keep every source character; boundaries prefer sentence/paragraph ends."""
    start = 0
    while start < len(text):
        end = min(start+size, len(text))
        if end < len(text):
            boundary = max(text.rfind('\n', start+size//2, end), text.rfind('. ', start+size//2, end))
            if boundary > start:
                end = boundary+1
        piece = text[start:end].strip()
        if piece:
            yield start, end, piece
        if end == len(text):
            break
        start = max(start+1, end-overlap)


def ingest_sources(root, cache, refresh=False):
    root, cache = Path(root), Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    specifications = json.loads((root/'app/knowledge/sources.json').read_text(encoding='utf-8'))
    documents, chunks, failures = [], [], []
    for source in specifications:
        path = cache / (source['id'] + ('.pdf' if source['type'] == 'pdf' else '.html'))
        provenance_path = path.with_suffix(path.suffix+'.json')
        try:
            if refresh or not path.exists():
                response = requests.get(source['url'], timeout=(10, 90), headers={
                    'User-Agent': 'DiaCare-PTIT-Educational-Research/2.0'})
                response.raise_for_status()
                if len(response.content) > 20_000_000:
                    raise ValueError('Source exceeds 20 MB')
                extract_pages(response.content, source['type'])
                path.write_bytes(response.content)
                provenance_path.write_text(json.dumps({'retrieved_at': datetime.now(timezone.utc).isoformat(),
                    'final_url': response.url, 'http_status': response.status_code,
                    'content_type': response.headers.get('Content-Type')}, ensure_ascii=False), encoding='utf-8')
            raw = path.read_bytes()
            fetched = (json.loads(provenance_path.read_text(encoding='utf-8')) if provenance_path.exists()
                       else {'retrieved_at': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                             'retrieval_date_basis': 'raw cache file timestamp; original HTTP metadata unavailable'})
            pages = [(page, clean_text(text)) for page, text in extract_pages(raw, source['type'])]
            text = '\n'.join(value for _, value in pages)
            if len(text) < 200:
                raise ValueError('Insufficient extractable text')
            document = {**source, **fetched, **(web_metadata(raw) if source['type'] == 'web' else {}),
                'id': source['id'], 'ingestion': 'downloaded',
                'bytes': len(raw), 'sha256': digest(raw), 'text_sha256': digest(text.encode()),
                'page_count': len(pages) if source['type'] == 'pdf' else None,
                'text_chars': len(text)}
            documents.append(document)
            for page, page_text in pages:
                for index, (start, end, content) in enumerate(text_chunks(page_text), 1):
                    identifier = f"{source['id']}-P{page or 0:03d}-C{index:03d}"
                    chunks.append({'id': identifier, 'document_id': source['id'],
                        'title': source['title'], 'text': content, 'url': source['url'],
                        'page': page, 'source_type': source['type'], 'language': source['language'],
                        'char_start': start, 'char_end': end, 'text_sha256': digest(content.encode())})
            print(source['id'], len(raw), len(text), 'source verified', flush=True)
        except (requests.RequestException, ValueError, OSError) as error:
            failures.append({'id': source['id'], 'url': source['url'], 'error': type(error).__name__})
            print(source['id'], 'FAILED', type(error).__name__, flush=True)
    return documents, chunks, failures


def add_curated_cards(root, documents, chunks):
    """Preserve the original 24 authored cards without calling them downloaded text."""
    cards = json.loads((Path(root)/'app/knowledge/cards.json').read_text(encoding='utf-8'))
    by_url = {item['url']: item for item in documents}
    for card in cards:
        if card['url'] not in by_url:
            document = {'id': 'REF'+str(len(by_url)+1).zfill(3), 'title': card['source_title'],
                'url': card['url'], 'type': 'reference', 'language': 'vi',
                'ingestion': 'curated_reference', 'bytes': 0, 'page_count': None,
                'retrieved_at': card['retrieved_at'], 'text_chars': 0}
            documents.append(document)
            by_url[card['url']] = document
        chunks.append({**card, 'document_id': by_url[card['url']]['id'], 'page': None,
            'source_type': 'curated_card', 'language': 'vi', 'char_start': 0,
            'char_end': len(card['text']), 'text_sha256': digest(card['text'].encode())})
    return cards
