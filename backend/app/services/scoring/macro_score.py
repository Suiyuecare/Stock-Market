from app.services.scoring.common import ScorePayload, scoring_payload


def calculate_macro_score() -> ScorePayload:
    return scoring_payload(score=0.05, positive_factors=["macro placeholder neutral-positive"], confidence=0.35)
