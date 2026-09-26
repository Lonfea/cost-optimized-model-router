from app.routing import choose_route, score_complexity


def test_simple_prompt_routes_cheap():
    decision = choose_route("Summarize this sentence.", threshold=4)
    assert decision.tier == "cheap"


def test_complex_production_prompt_routes_premium():
    prompt = (
        "Debug this production distributed architecture. Compare the trade-offs, "
        "identify the root cause, and propose a security-conscious migration plan."
    )
    decision = choose_route(prompt, threshold=4)
    assert decision.tier == "premium"
    assert decision.score >= 4


def test_user_can_override_tier():
    decision = choose_route("hello", threshold=4, requested_tier="premium")
    assert decision.tier == "premium"
    assert "user_override" in decision.reasons


def test_code_and_error_raise_complexity():
    score, reasons = score_complexity("Traceback exception")
    assert score >= 2
    assert "code_or_error" in reasons
