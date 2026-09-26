from prometheus_client import Counter, Histogram

REQUESTS = Counter(
    "ai_router_requests_total",
    "Requests handled by routing tier and model.",
    ["tier", "model"],
)
COST = Counter(
    "ai_router_request_cost_usd_total",
    "Estimated LLM spend in USD.",
    ["tier", "model"],
)
LATENCY = Histogram(
    "ai_router_latency_seconds",
    "End-to-end model latency in seconds.",
    ["tier", "model"],
)
FAILURES = Counter(
    "ai_router_failures_total",
    "Failed model calls.",
    ["tier", "model"],
)
