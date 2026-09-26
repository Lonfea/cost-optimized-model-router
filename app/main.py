import time
import uuid

from fastapi import FastAPI, HTTPException, Response
from litellm import acompletion
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from app.config import get_settings
from app.metrics import COST, FAILURES, LATENCY, REQUESTS
from app.routing import choose_route

settings = get_settings()
app = FastAPI(title="Cost-Optimized Model Router", version="0.1.0")


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=30_000)
    tier: str | None = Field(default=None, pattern="^(cheap|premium)$")


class ChatResponse(BaseModel):
    request_id: str
    answer: str
    tier: str
    model: str
    complexity_score: int
    routing_reasons: list[str]
    cost_usd: float
    latency_seconds: float
    fallback_used: bool


async def _call(model: str, prompt: str):
    return await acompletion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )


def _response_cost(response) -> float:
    hidden = getattr(response, "_hidden_params", {}) or {}
    value = hidden.get("response_cost")
    return float(value) if value is not None else 0.0


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "cheap_model": settings.cheap_model,
        "premium_model": settings.premium_model,
    }


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    request_id = str(uuid.uuid4())
    decision = choose_route(
        request.prompt,
        threshold=settings.complexity_threshold,
        requested_tier=request.tier,
    )
    selected = settings.premium_model if decision.tier == "premium" else settings.cheap_model
    fallback_used = False
    started = time.perf_counter()

    try:
        response = await _call(selected, request.prompt)
    except Exception as first_error:
        FAILURES.labels(decision.tier, selected).inc()
        if decision.tier == "cheap":
            fallback_used = True
            selected = settings.premium_model
            try:
                response = await _call(selected, request.prompt)
            except Exception as second_error:
                FAILURES.labels("premium", selected).inc()
                raise HTTPException(status_code=502, detail="Both model tiers failed.") from second_error
        else:
            raise HTTPException(status_code=502, detail="Premium model call failed.") from first_error

    elapsed = time.perf_counter() - started
    final_tier = "premium" if selected == settings.premium_model else "cheap"
    cost = _response_cost(response)

    REQUESTS.labels(final_tier, selected).inc()
    COST.labels(final_tier, selected).inc(cost)
    LATENCY.labels(final_tier, selected).observe(elapsed)

    content = response.choices[0].message.content or ""
    return ChatResponse(
        request_id=request_id,
        answer=content,
        tier=final_tier,
        model=selected,
        complexity_score=decision.score,
        routing_reasons=list(decision.reasons),
        cost_usd=cost,
        latency_seconds=elapsed,
        fallback_used=fallback_used,
    )
