"""Bulking bias and safety rules. Pure functions so they can be unit tested."""

import re

CUT_TERMS = [
    "cut", "cutting", "fat loss", "lose fat", "lose weight", "shred", "shredded",
    "deficit", "lean out", "get lean", "weight loss",
]
BULK_TERMS = [
    "bulk", "bulking", "muscle gain", "build muscle", "hypertrophy", "surplus",
    "progressive overload", "mass", "lean gains", "gain weight", "strength",
]
STEROID_TERMS = [
    "steroid", "anabolic", "trenbolone", "dianabol", "sarm", "clenbuterol",
    "hgh", "human growth hormone", "peds", "ped ", "testosterone dose",
]
HEALTH_TERMS = [
    "injury", "injured", "pain", "doctor", "medication", "diabetes",
    "pregnant", "heart", "blood pressure", "eating disorder",
]

STEROID_REFUSAL = (
    "I can't give advice on steroids, PEDs or other performance drugs. "
    "Please talk to a doctor or a sports medicine specialist before using anything like that. "
    "I can help with food, training and recovery for building muscle."
)
HEALTH_NOTE = "See a doctor if you have an injury, a medical condition or any symptoms that worry you."


def _contains(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(re.search(r"\b" + re.escape(t.strip()) + r"\b", lowered) for t in terms)


def is_steroid_question(question: str) -> bool:
    return _contains(question, STEROID_TERMS)


def is_cutting_question(question: str) -> bool:
    return _contains(question, CUT_TERMS)


def is_health_question(question: str) -> bool:
    return _contains(question, HEALTH_TERMS)


def bulk_bias_boost(text: str) -> float:
    """Small score nudge: bulking-leaning chunks rank above cutting-leaning ones."""
    lowered = text.lower()
    bulk = sum(lowered.count(t) for t in BULK_TERMS)
    cut = sum(lowered.count(t) for t in CUT_TERMS)
    raw = 0.02 * min(bulk, 5) - 0.02 * min(cut, 5)
    return max(-0.1, min(0.1, raw))
