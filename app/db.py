import psycopg
from pgvector.psycopg import register_vector

from app import config


def connect() -> psycopg.Connection:
    if not config.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set. Put your Neon connection string in .env.")
    conn = psycopg.connect(config.DATABASE_URL, autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def init_schema(conn: psycopg.Connection) -> None:
    with open("sql/schema.sql") as f:
        conn.execute(f.read())


def search(conn: psycopg.Connection, embedding: list[float], limit: int) -> list[tuple]:
    rows = conn.execute(
        """
        SELECT content, source_url, 1 - (embedding <=> %s::vector) AS similarity
        FROM chunks
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (embedding, embedding, limit),
    ).fetchall()
    return rows
