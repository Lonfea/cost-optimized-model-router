import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RouteDecision:
    tier: str
    score: int
    reasons: tuple[str, ...]


COMPLEX_TERMS = {
    "architecture",
    "debug",
    "root cause",
    "security",
    "threat model",
    "optimize",
    "trade-off",
    "tradeoff",
    "benchmark",
    "evaluate",
    "proof",
    "derive",
    "multi-step",
    "migration",
    "distributed",
    "concurrency",
    "incident",
}


def score_complexity(prompt: str) -> tuple[int, list[str]]:
    text = prompt.lower()
    words = re.findall(r"\w+", text)
    score = 0
    reasons: list[str] = []

    if len(words) >= 120:
        score += 2
        reasons.append("long_prompt")
    elif len(words) >= 50:
        score += 1
        reasons.append("medium_prompt")

    if "traceback" in text or "exception" in text:
        score += 2
        reasons.append("code_or_error")

    matched = [term for term in COMPLEX_TERMS if term in text]
    if matched:
        score += min(3, len(matched))
        reasons.append("complexity_terms")

    step_markers = sum(
        marker in text
        for marker in ("first,", "second,", "then ", "step 1", "step one", "compare ")
    )
    if step_markers >= 2:
        score += 2
        reasons.append("multi_step")

    if any(x in text for x in ("must be correct", "high stakes", "production", "regression")):
        score += 2
        reasons.append("quality_sensitive")

    return score, reasons


def choose_route(prompt: str, threshold: int, requested_tier: str | None = None) -> RouteDecision:
    if requested_tier in {"cheap", "premium"}:
        return RouteDecision(requested_tier, 0, ("user_override",))

    score, reasons = score_complexity(prompt)
    tier = "premium" if score >= threshold else "cheap"
    return RouteDecision(tier=tier, score=score, reasons=tuple(reasons))
