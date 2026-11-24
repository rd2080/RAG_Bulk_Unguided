from app.chunking import chunk_text
from app.rules import (
    STEROID_REFUSAL,
    bulk_bias_boost,
    is_cutting_question,
    is_steroid_question,
)


def test_cutting_question_detected():
    assert is_cutting_question("How do I cut fat fast?")
    assert is_cutting_question("best way to lose weight")
    assert not is_cutting_question("How do I build muscle on a bulk?")


def test_steroid_question_detected():
    assert is_steroid_question("what dose of dianabol should I take")
    assert not is_steroid_question("how much protein per day")


def test_bulk_text_scores_above_cut_text():
    bulk = "A calorie surplus and progressive overload drive hypertrophy."
    cut = "A calorie deficit helps fat loss and shredded looks."
    assert bulk_bias_boost(bulk) > bulk_bias_boost(cut)


def test_bias_boost_is_capped():
    assert -0.1 <= bulk_bias_boost("cut " * 50) <= 0.1
    assert -0.1 <= bulk_bias_boost("bulk " * 50) <= 0.1


def test_refusal_text_suggests_doctor():
    assert "doctor" in STEROID_REFUSAL


def test_chunking_keeps_text_and_limits_size():
    text = "\n".join(f"Paragraph {i} about protein intake and training." for i in range(200))
    chunks = chunk_text(text, max_chars=300, overlap=50)
    assert chunks
    assert all(len(c) <= 300 for c in chunks)
    assert "Paragraph 0" in chunks[0]
    assert "Paragraph 199" in chunks[-1]
