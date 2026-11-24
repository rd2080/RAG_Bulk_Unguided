"""Split text into overlapping chunks at paragraph boundaries."""


def chunk_text(text: str, max_chars: int = 800, overlap: int = 120) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(para) > max_chars:
            # hard-split very long paragraphs so no chunk is huge
            for i in range(0, len(para), max_chars - overlap):
                piece = para[i : i + max_chars]
                if current:
                    chunks.append(current)
                    current = ""
                chunks.append(piece)
            continue
        if len(current) + len(para) + 1 <= max_chars:
            current = f"{current}\n{para}" if current else para
        else:
            if current:
                chunks.append(current)
            tail = current[-overlap:] if current else ""
            current = f"{tail}\n{para}".strip() if tail else para
    if current:
        chunks.append(current)
    return chunks
