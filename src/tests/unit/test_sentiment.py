"""Unit tests for sentiment analysis."""
import pytest
from src.agent.sentiment import analyze_sentiment


class TestSentimentAnalysis:
    def test_neutral_message(self):
        score = analyze_sentiment("How do I reset my password?")
        assert 0.35 <= score <= 0.75, f"Expected neutral score, got {score}"

    def test_very_angry_message(self):
        score = analyze_sentiment("This is UNACCEPTABLE!! I'm switching to Asana!")
        assert score < 0.3, f"Expected negative score, got {score}"

    def test_negative_emoji_only(self):
        # Use unicode escapes to avoid literal emoji in source
        score = analyze_sentiment("\U0001f621\U0001f621\U0001f621")
        assert score < 0.2, f"Expected very negative score for angry emojis, got {score}"

    def test_positive_emoji_only(self):
        score = analyze_sentiment("\U0001f60a\U0001f60a\u2705")
        assert score > 0.7, f"Expected positive score for happy emojis, got {score}"

    def test_very_positive_message(self):
        score = analyze_sentiment("Thank you so much! This is amazing!")
        assert score >= 0.6, f"Expected positive score, got {score}"

    def test_escalation_keywords(self):
        score = analyze_sentiment("I need a refund immediately, this is terrible")
        assert score < 0.3, f"Expected escalation-level score, got {score}"

    def test_empty_message(self):
        score = analyze_sentiment("")
        assert score == 0.5

    def test_whitespace_only(self):
        score = analyze_sentiment("   ")
        assert score == 0.5

    def test_all_caps_anger(self):
        score = analyze_sentiment("THIS PRODUCT IS ABSOLUTELY TERRIBLE AND BROKEN")
        assert score < 0.3

    def test_legal_keywords(self):
        score = analyze_sentiment("I'm going to sue your company for this")
        assert score < 0.3
