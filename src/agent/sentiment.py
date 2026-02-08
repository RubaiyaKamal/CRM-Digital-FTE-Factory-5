"""
Lightweight sentiment analysis (VADER-based, ported from prototype).
"""
from __future__ import annotations

import re
from typing import List

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

# Unicode code-point representations to avoid literal emojis in source code
_NEGATIVE_EMOJIS = {"\U0001f621", "\U0001f620", "\U0001f92c", "\U0001f494", "\U0001f44e"}
_POSITIVE_EMOJIS = {"\U0001f60a", "\U0001f603", "\U0001f389", "\U0001f44d", "\u2764\ufe0f", "\u2705"}
_ANGRY_KW = [
    "unacceptable", "ridiculous", "terrible", "worst",
    "cancel", "switching", "refund", "lawsuit", "lawyer",
    "attorney", "sue", "legal action",
]


def analyze_sentiment(message: str) -> float:
    """
    Return a sentiment score in [0, 1] where 0 = very negative, 1 = very positive.
    Score < 0.3 triggers escalation.
    """
    if not message or not message.strip():
        return 0.5

    cleaned = message.strip()

    # Emoji-only check
    if not re.search(r"[a-zA-Z]", cleaned) and len(cleaned) <= 10:
        neg = sum(1 for e in _NEGATIVE_EMOJIS if e in cleaned)
        pos = sum(1 for e in _POSITIVE_EMOJIS if e in cleaned)
        if neg > 0 and pos == 0:
            return 0.1
        if pos > 0 and neg == 0:
            return 0.9

    scores = _analyzer.polarity_scores(message)
    score = (scores["compound"] + 1) / 2

    # ALL CAPS modifier
    letters = [c for c in message if c.isalpha()]
    if len(letters) >= 10:
        uppercase_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        if uppercase_ratio > 0.7:
            score = min(score * 0.7, 0.3)

    # Angry keyword modifier
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in _ANGRY_KW):
        score = min(score * 0.5, 0.2)

    return max(0.0, min(1.0, score))
