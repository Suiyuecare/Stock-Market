from typing import List

from app.schemas import NewsEvent
from app.services.scoring.common import ScorePayload, scoring_payload


def calculate_news_score(events: List[NewsEvent]) -> ScorePayload:
    if not events:
        return scoring_payload(score=0.0, confidence=0.3)
    score = max(-1.0, min(1.0, sum(event.impact_score for event in events) / len(events)))
    return scoring_payload(
        score=score,
        positive_factors=[event.title for event in events if event.impact_score > 0],
        negative_factors=[event.title for event in events if event.impact_score < 0],
        confidence=0.5,
    )
