from typing import Dict, List, Mapping

from app.schemas import (
    ExplainabilityFactorContribution,
    ExplainabilityReport,
    ExplainabilityReportInput,
)


DISCLAIMER = "本系統僅提供資料分析與研究用途，不構成個人化投資建議。"


class ExplainabilityReportBuilder:
    """Build an auditable explanation report for a generated research signal."""

    def build(self, report_input: ExplainabilityReportInput) -> ExplainabilityReport:
        factor_weights = self._mapping(report_input.final_prediction.get("explanation", {})).get("factor_weights", {})
        score_calculation = {
            "BullishScore": report_input.final_prediction.get("BullishScore"),
            "RiskScore": report_input.final_prediction.get("RiskScore"),
            "RiskAdjustedScore": report_input.final_prediction.get("RiskAdjustedScore"),
            "probability_up_1d": report_input.final_prediction.get("probability_up_1d"),
            "probability_up_5d": report_input.final_prediction.get("probability_up_5d"),
            "probability_up_20d": report_input.final_prediction.get("probability_up_20d"),
            "factor_weights": factor_weights,
            "risk_weight_multiplier": self._mapping(report_input.final_prediction.get("explanation", {})).get(
                "risk_weight_multiplier",
                1.0,
            ),
        }
        contributions = self._factor_contributions(report_input.factor_scores, factor_weights)
        positive = [item for item in contributions if item.direction == "positive"]
        negative = [item for item in contributions if item.direction == "negative"]
        risk_factors = self._risk_factors(report_input.factor_scores, report_input.final_prediction)

        return ExplainabilityReport(
            signal_id=report_input.signal_id,
            stock_id=report_input.stock_id,
            stock_name=report_input.stock_name,
            generated_at=report_input.generated_at,
            model_version=report_input.model_version,
            scoring_version=report_input.scoring_version,
            data_sources=report_input.data_sources,
            score_calculation=score_calculation,
            positive_factors=sorted(positive, key=lambda item: item.contribution, reverse=True),
            negative_factors=sorted(negative, key=lambda item: item.contribution),
            risk_factors=risk_factors,
            historical_win_rate_summary=report_input.calibration_summary,
            selection_summary=report_input.selection_decision,
            market_regime_summary=report_input.market_regime,
            portfolio_risk_summary=report_input.portfolio_context,
            user_visible_text=self._user_visible_text(report_input, positive, negative, risk_factors),
            disclaimer=DISCLAIMER,
        )

    def _factor_contributions(
        self,
        factor_scores: Mapping[str, Dict[str, object]],
        factor_weights: object,
    ) -> List[ExplainabilityFactorContribution]:
        weights = self._mapping(factor_weights)
        contributions: List[ExplainabilityFactorContribution] = []
        for factor_name, payload in factor_scores.items():
            score = float(payload.get("score", 50.0))
            weight = float(weights.get(factor_name, payload.get("weight", 0.0)))
            contribution = round(score * weight, 6)
            direction = "positive" if score >= 50 else "negative"
            explanation = self._explanation_text(payload, direction)
            data_sources = [str(source) for source in payload.get("data_sources", [])]
            contributions.append(
                ExplainabilityFactorContribution(
                    factor_name=factor_name,
                    score=round(score, 6),
                    weight=round(weight, 6),
                    contribution=contribution,
                    direction=direction,
                    explanation=explanation,
                    data_sources=data_sources,
                )
            )
        return contributions

    def _risk_factors(
        self,
        factor_scores: Mapping[str, Dict[str, object]],
        final_prediction: Mapping[str, object],
    ) -> List[str]:
        risks: List[str] = []
        explanation = self._mapping(final_prediction.get("explanation", {}))
        risks.extend([str(item) for item in explanation.get("top_risk_factors", [])])
        for payload in factor_scores.values():
            risks.extend([str(item) for item in payload.get("risk_factors", [])])
        return sorted(set(risks))

    def _explanation_text(self, payload: Mapping[str, object], direction: str) -> str:
        field = "positive_factors" if direction == "positive" else "negative_factors"
        factors = [str(item) for item in payload.get(field, [])]
        if factors:
            return "; ".join(factors)
        return "Score is above neutral." if direction == "positive" else "Score is below neutral."

    def _user_visible_text(
        self,
        report_input: ExplainabilityReportInput,
        positive: List[ExplainabilityFactorContribution],
        negative: List[ExplainabilityFactorContribution],
        risk_factors: List[str],
    ) -> str:
        probability = report_input.final_prediction.get("probability_up_5d")
        top_positive = ", ".join([item.factor_name for item in sorted(positive, key=lambda item: item.contribution, reverse=True)[:3]]) or "none"
        top_negative = ", ".join([item.factor_name for item in sorted(negative, key=lambda item: item.contribution)[:3]]) or "none"
        risk_text = ", ".join(risk_factors[:3]) or "no elevated risk factor recorded"
        return (
            f"{report_input.stock_id} {report_input.stock_name} 的 5 日研究訊號機率為 {probability}. "
            f"主要加分因子: {top_positive}. 主要扣分因子: {top_negative}. "
            f"目前風險: {risk_text}. {DISCLAIMER}"
        )

    def _mapping(self, value: object) -> Mapping[str, object]:
        return value if isinstance(value, Mapping) else {}
