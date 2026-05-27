"""
DeepEval integration with a heuristic fallback.

If the `deepeval` library is installed and an LLM API key is configured we use
its `AnswerRelevancyMetric` and `HallucinationMetric`. Otherwise we use a
lightweight heuristic that scores relevance and faithfulness based on token
overlap, length, and red-flag patterns. Either way the public API is the same.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("edunova.eval")


@dataclass
class EvaluationResult:
    score: float                # 0..1 overall
    relevance: float
    faithfulness: float
    hallucination_risk: float
    passed: bool
    reasons: List[str]

    def to_dict(self) -> dict:
        return {
            "score": round(self.score, 3),
            "relevance": round(self.relevance, 3),
            "faithfulness": round(self.faithfulness, 3),
            "hallucination_risk": round(self.hallucination_risk, 3),
            "passed": self.passed,
            "reasons": self.reasons,
        }


_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "is", "are", "was",
    "were", "be", "been", "for", "on", "with", "as", "by", "this", "that",
    "it", "at", "from", "your", "you", "i", "me", "my", "we", "our",
    "they", "them", "their", "his", "her", "she", "he",
}


def _tokenize(text: str) -> List[str]:
    return [w for w in re.findall(r"[a-z0-9\+\#\.\-]+", text.lower()) if w not in _STOPWORDS and len(w) > 1]


def _relevance_score(question: str, answer: str) -> float:
    """Token-overlap relevance score: how many question tokens appear in answer."""
    q_tokens = set(_tokenize(question))
    a_tokens = set(_tokenize(answer))
    if not q_tokens:
        return 1.0 if a_tokens else 0.0
    overlap = len(q_tokens & a_tokens)
    return min(1.0, 0.4 + 0.6 * (overlap / len(q_tokens)))


def _faithfulness_score(answer: str) -> float:
    """Penalize obvious red-flag phrasing that suggests hallucination."""
    if not answer.strip():
        return 0.0
    text = answer.lower()
    penalties = 0
    for flag in (
        "i don't know but",
        "let me make up",
        "i'll invent",
        "this is fake",
        "as an ai i cannot",
    ):
        if flag in text:
            penalties += 1
    base = 1.0 - 0.2 * penalties
    # Very short answers are less trustworthy on complex prompts
    if len(answer) < 40:
        base -= 0.15
    return max(0.0, min(1.0, base))


class DeepEvalEvaluator:
    """Evaluates LLM responses, with optional DeepEval backend."""

    def __init__(self):
        self.enabled = settings.DEEPEVAL_ENABLED
        self.threshold = settings.DEEPEVAL_THRESHOLD
        self.max_retries = settings.DEEPEVAL_MAX_RETRIES
        self._deepeval_available = self._check_deepeval()

    def _check_deepeval(self) -> bool:
        try:
            import deepeval  # noqa: F401
            return True
        except Exception:
            logger.info("deepeval not installed — using heuristic evaluator.")
            return False

    async def evaluate(
        self,
        question: str,
        answer: str,
        context: Optional[List[str]] = None,
    ) -> EvaluationResult:
        """Run evaluation; never raises — always returns an EvaluationResult."""
        if not self.enabled:
            return EvaluationResult(1.0, 1.0, 1.0, 0.0, True, ["evaluation disabled"])

        if self._deepeval_available and settings.OPENAI_API_KEY:
            try:
                return await self._evaluate_with_deepeval(question, answer, context or [])
            except Exception as e:
                logger.warning("DeepEval failed (%s), using heuristic fallback.", e)

        return self._evaluate_heuristic(question, answer, context or [])

    async def _evaluate_with_deepeval(
        self, question: str, answer: str, context: List[str]
    ) -> EvaluationResult:
        from deepeval import evaluate
        from deepeval.metrics import AnswerRelevancyMetric, HallucinationMetric
        from deepeval.test_case import LLMTestCase

        test_case = LLMTestCase(
            input=question,
            actual_output=answer,
            context=context or [answer],
        )
        relevancy = AnswerRelevancyMetric(threshold=self.threshold)
        relevancy.measure(test_case)
        relevance_score = float(getattr(relevancy, "score", 0.0) or 0.0)

        hallucination_risk = 0.0
        try:
            hallucination = HallucinationMetric(threshold=self.threshold)
            hallucination.measure(test_case)
            hallucination_risk = float(getattr(hallucination, "score", 0.0) or 0.0)
        except Exception:
            pass

        faithfulness = 1.0 - hallucination_risk
        overall = (relevance_score + faithfulness) / 2
        passed = overall >= self.threshold

        return EvaluationResult(
            score=overall,
            relevance=relevance_score,
            faithfulness=faithfulness,
            hallucination_risk=hallucination_risk,
            passed=passed,
            reasons=[f"deepeval relevance={relevance_score:.2f}", f"hallucination_risk={hallucination_risk:.2f}"],
        )

    def _evaluate_heuristic(
        self, question: str, answer: str, context: List[str]
    ) -> EvaluationResult:
        relevance = _relevance_score(question, answer)
        faithfulness = _faithfulness_score(answer)
        hallucination_risk = max(0.0, 1.0 - faithfulness)
        overall = 0.55 * relevance + 0.45 * faithfulness
        passed = overall >= self.threshold

        reasons = [
            f"relevance={relevance:.2f}",
            f"faithfulness={faithfulness:.2f}",
            "passed" if passed else "below threshold",
        ]
        return EvaluationResult(
            score=overall,
            relevance=relevance,
            faithfulness=faithfulness,
            hallucination_risk=hallucination_risk,
            passed=passed,
            reasons=reasons,
        )


# Module-level singleton
evaluator = DeepEvalEvaluator()
