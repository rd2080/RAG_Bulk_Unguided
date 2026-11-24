"""Fetch approved URLs, chunk them, embed them and store them in Postgres.

Usage: python -m app.ingest sources.txt
"""

import re
import sys
import urllib.robotparser
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app import db, ollama
from app.chunking import chunk_text

USER_AGENT = "BulkingRAGBot/0.1 (personal learning project)"


def allowed_by_robots(url: str) -> bool:
    parts = urlparse(url)
    rp = urllib.robotparser.RobotFileParser()
    try:
        r = httpx.get(f"{parts.scheme}://{parts.netloc}/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code >= 400:
            return True
        rp.parse(r.text.splitlines())
    except httpx.HTTPError:
        return False
    return rp.can_fetch(USER_AGENT, url)


def fetch_text(url: str) -> str:
    r = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=30, follow_redirects=True)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "sup"]):
        tag.decompose()
    text = soup.get_text("\n")
    text = re.sub(r"\[\d+\]", "", text)  # drop wiki citation markers
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def load_sources(path: str) -> list[str]:
    with open(path) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def ingest(urls: list[str]) -> int:
    conn = db.connect()
    db.init_schema(conn)
    total = 0
    for url in urls:
        if not allowed_by_robots(url):
            print(f"SKIP (robots.txt disallows): {url}")
            continue
        chunks = chunk_text(fetch_text(url))
        if not chunks:
            print(f"SKIP (no text): {url}")
            continue
        vectors = ollama.embed(chunks)
        conn.execute("DELETE FROM chunks WHERE source_url = %s", (url,))
        for i, (content, vec) in enumerate(zip(chunks, vectors)):
            conn.execute(
                "INSERT INTO chunks (source_url, chunk_index, content, embedding) VALUES (%s, %s, %s, %s)",
                (url, i, content, vec),
            )
        print(f"OK {len(chunks)} chunks: {url}")
        total += len(chunks)
    conn.close()
    print(f"Stored {total} chunks in total.")
    return total


if __name__ == "__main__":
    ingest(load_sources(sys.argv[1] if len(sys.argv) > 1 else "sources.txt"))
