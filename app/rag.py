from app import config, db, ollama
from app.rules import (
    HEALTH_NOTE,
    STEROID_REFUSAL,
    bulk_bias_boost,
    is_cutting_question,
    is_health_question,
    is_steroid_question,
)

BASE_SYSTEM = """You are a bulking coach. Your users want to gain muscle and strength.
Answer using only the numbered context below. If the context does not cover the question, say so.
Favour advice on a calorie surplus, adequate protein, progressive overload and recovery.
Use a number (grams, calories, sets, reps) only if that exact number appears in the context. Otherwise give the advice in plain words with no number.
Keep answers short and practical."""

CUTTING_RULE = """The user asked about cutting or fat loss. Answer honestly, then explain how
the same question looks for someone trying to gain muscle, and say when cutting does not fit their goal."""


def build_system_prompt(question: str) -> str:
    parts = [BASE_SYSTEM]
    if is_cutting_question(question):
        parts.append(CUTTING_RULE)
    return "\n\n".join(parts)


def answer(question: str) -> dict:
    if is_steroid_question(question):
        return {"answer": STEROID_REFUSAL, "sources": []}

    conn = db.connect()
    try:
        query_vec = ollama.embed([question])[0]
        rows = db.search(conn, query_vec, config.TOP_K * 3)
    finally:
        conn.close()

    # re-rank: similarity plus a small bulking bias, then keep the top K
    ranked = sorted(rows, key=lambda r: r[2] + bulk_bias_boost(r[0]), reverse=True)[: config.TOP_K]
    if not ranked:
        return {"answer": "I have no indexed sources yet. Run the ingest script first.", "sources": []}

    context = "\n\n".join(f"[{i + 1}] {content}" for i, (content, _, _) in enumerate(ranked))
    user_msg = f"Context:\n{context}\n\nQuestion: {question}"
    text = ollama.chat(build_system_prompt(question), user_msg)

    if is_health_question(question):
        text = f"{text}\n\n{HEALTH_NOTE}"

    sources = []
    seen = set()
    for _, url, _ in ranked:
        if url not in seen:
            seen.add(url)
            sources.append(url)
    return {"answer": text, "sources": sources}
