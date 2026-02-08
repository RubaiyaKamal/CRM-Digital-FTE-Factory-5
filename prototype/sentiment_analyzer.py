"""
Sentiment analysis for customer messages.
Uses VADER (Valence Aware Dictionary and sEntiment Reasoner) which is
specifically tuned for social media text and handles emojis, ALL CAPS, etc.
"""
import re
from typing import List, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from models import SentimentAnalysis, Sentiment


class SentimentAnalyzer:
    """Analyzes customer message sentiment for escalation decisions"""

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

        # Escalation keywords that override sentiment
        self.angry_keywords = [
            "unacceptable", "ridiculous", "terrible", "worst",
            "cancel", "switching", "refund", "lawsuit", "lawyer",
            "attorney", "sue", "legal action"
        ]

        # Emoji sentiment mapping
        self.negative_emojis = ["😡", "😠", "🤬", "💔", "👎"]
        self.positive_emojis = ["😊", "😃", "🎉", "👍", "❤️", "✅"]

    def analyze(self, message: str) -> SentimentAnalysis:
        """
        Analyze message sentiment.

        Returns score from 0 (very negative) to 1 (very positive).
        Score <0.3 triggers immediate escalation.
        """
        if not message or not message.strip():
            return SentimentAnalysis(
                score=0.5,
                confidence=0.5,
                label=Sentiment.NEUTRAL,
                detected_emotions=[]
            )

        # Check for emoji-only message
        emoji_sentiment = self._analyze_emoji_only(message)
        if emoji_sentiment:
            return emoji_sentiment

        # VADER analysis (returns compound score from -1 to 1)
        scores = self.analyzer.polarity_scores(message)
        compound = scores['compound']

        # Convert VADER's -1 to 1 scale to our 0 to 1 scale
        normalized_score = (compound + 1) / 2

        # Check for ALL CAPS (indicates shouting/anger)
        if self._is_all_caps(message):
            normalized_score = min(normalized_score * 0.7, 0.3)  # Reduce score significantly

        # Check for angry keywords
        angry_keywords_found = self._find_angry_keywords(message)
        if angry_keywords_found:
            normalized_score = min(normalized_score * 0.5, 0.2)  # Strong negative signal

        # Determine confidence based on text length and clarity
        confidence = self._calculate_confidence(message, scores)

        # Map score to sentiment label
        label = self._score_to_label(normalized_score)

        # Detect specific emotions
        emotions = self._detect_emotions(message, scores, angry_keywords_found)

        return SentimentAnalysis(
            score=normalized_score,
            confidence=confidence,
            label=label,
            detected_emotions=emotions
        )

    def _analyze_emoji_only(self, message: str) -> Optional[SentimentAnalysis]:
        """Handle emoji-only messages"""
        # Remove whitespace
        cleaned = message.strip()

        # Check if message is only emojis (no alphabetic characters)
        if not re.search(r'[a-zA-Z]', cleaned) and len(cleaned) <= 10:
            # Count negative vs positive emojis
            negative_count = sum(1 for emoji in self.negative_emojis if emoji in cleaned)
            positive_count = sum(1 for emoji in self.positive_emojis if emoji in cleaned)

            if negative_count > 0 and positive_count == 0:
                return SentimentAnalysis(
                    score=0.1,  # Very negative
                    confidence=0.9,
                    label=Sentiment.VERY_ANGRY,
                    detected_emotions=["anger", "frustration"]
                )
            elif positive_count > 0 and negative_count == 0:
                return SentimentAnalysis(
                    score=0.9,  # Very positive
                    confidence=0.9,
                    label=Sentiment.VERY_POSITIVE,
                    detected_emotions=["happiness"]
                )

        return None

    def _is_all_caps(self, message: str) -> bool:
        """Check if message is mostly ALL CAPS (excluding punctuation)"""
        # Get only alphabetic characters
        letters = [c for c in message if c.isalpha()]
        if len(letters) < 10:
            return False  # Too short to determine

        uppercase_count = sum(1 for c in letters if c.isupper())
        uppercase_ratio = uppercase_count / len(letters)

        return uppercase_ratio > 0.7  # 70%+ uppercase

    def _find_angry_keywords(self, message: str) -> List[str]:
        """Find angry/escalation keywords in message"""
        message_lower = message.lower()
        found = []

        for keyword in self.angry_keywords:
            if keyword in message_lower:
                found.append(keyword)

        return found

    def _calculate_confidence(self, message: str, scores: dict) -> float:
        """Calculate confidence in sentiment analysis"""
        # Start with base confidence
        confidence = 0.7

        # Longer messages = more confident
        word_count = len(message.split())
        if word_count > 20:
            confidence += 0.15
        elif word_count < 5:
            confidence -= 0.15

        # Clear sentiment (high pos/neg, low neutral) = more confident
        neutrality = scores.get('neu', 0.5)
        if neutrality < 0.3:  # Clear sentiment
            confidence += 0.1
        elif neutrality > 0.7:  # Ambiguous
            confidence -= 0.1

        # Clamp to 0-1 range
        return max(0.0, min(1.0, confidence))

    def _score_to_label(self, score: float) -> Sentiment:
        """Map numeric score to sentiment label"""
        if score >= 0.8:
            return Sentiment.VERY_POSITIVE
        elif score >= 0.6:
            return Sentiment.POSITIVE
        elif score >= 0.4:
            return Sentiment.NEUTRAL
        elif score >= 0.3:
            return Sentiment.CONFUSED
        elif score >= 0.2:
            return Sentiment.FRUSTRATED
        elif score >= 0.1:
            return Sentiment.ANGRY
        else:
            return Sentiment.VERY_ANGRY

    def _detect_emotions(self, message: str, scores: dict, angry_keywords: List[str]) -> List[str]:
        """Detect specific emotions from message"""
        emotions = []

        # Check VADER scores
        if scores['pos'] > 0.5:
            emotions.append("happiness")
        if scores['neg'] > 0.5:
            emotions.append("anger")

        # Check for confusion markers
        confusion_markers = ["confused", "don't understand", "unclear", "what", "how"]
        if any(marker in message.lower() for marker in confusion_markers):
            emotions.append("confusion")

        # Check for frustration markers
        frustration_markers = ["frustrating", "annoying", "still not working", "tried everything"]
        if any(marker in message.lower() for marker in frustration_markers):
            emotions.append("frustration")

        # Angry keywords found
        if angry_keywords:
            emotions.append("anger")

        # Multiple exclamation/question marks
        if message.count('!') > 2 or message.count('?') > 3:
            emotions.append("urgency")

        return emotions


# Test the sentiment analyzer
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()

    test_cases = [
        "How do I reset my password?",  # Neutral
        "This is UNACCEPTABLE!! I'm switching to Asana!",  # Very angry
        "😡😡😡",  # Emoji-only angry
        "Thank you so much! This is amazing!",  # Very positive
        "I've tried EVERYTHING and it STILL doesn't work",  # Frustrated
        "help",  # Vague/neutral
    ]

    print("Sentiment Analysis Test:\n")
    for message in test_cases:
        result = analyzer.analyze(message)
        print(f"Message: {message}")
        print(f"Score: {result.score:.2f} | Label: {result.label.value}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Emotions: {', '.join(result.detected_emotions)}")
        print(f"Escalate: {'YES' if result.score < 0.3 else 'NO'}\n")
