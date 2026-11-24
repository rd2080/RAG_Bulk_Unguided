import httpx

from app import config


def embed(texts: list[str]) -> list[list[float]]:
    resp = httpx.post(
        f"{config.OLLAMA_URL}/api/embed",
        json={"model": config.EMBED_MODEL, "input": texts},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"]


def chat(system: str, user: str) -> str:
    resp = httpx.post(
        f"{config.OLLAMA_URL}/api/chat",
        json={
            "model": config.CHAT_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "think": False,
            "stream": False,
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"].strip()
