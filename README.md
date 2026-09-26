# Cost-Optimized Model Router

A production-oriented LLM gateway that classifies request complexity, routes simple work to a low-cost model, escalates harder work to a stronger model, and exposes cost, latency, error, and routing metrics through Prometheus.

## Architecture

Client -> FastAPI -> complexity classifier -> cheap or premium tier -> LiteLLM -> response + telemetry.

## What this proves

- custom model routing rather than hard-coding one model;
- explicit cost versus quality trade-offs;
- provider-agnostic calls through LiteLLM;
- spend and latency telemetry;
- deterministic tests for routing decisions;
- premium fallback if the cheap tier fails.

## Complexity signals

The router scores requests using transparent signals:
- prompt length;
- stack traces and errors;
- architecture, security, benchmark, migration, and distributed-systems language;
- multi-step reasoning markers;
- production or regression sensitivity;
- optional user override.

A later version can add a learned classifier and compare routing quality against a labelled benchmark.

## Configuration

The default tiers are configurable with environment variables:

- CHEAP_MODEL: openai/gpt-6-luna
- PREMIUM_MODEL: openai/gpt-6-sol
- COMPLEXITY_THRESHOLD: 4

No model name is hard-wired into the routing algorithm.

## Run

    cd ai-engineering-lab/model-router
    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    cp .env.example .env
    uvicorn app.main:app --reload

## API

POST /chat returns the selected tier, model, complexity score, routing reasons, latency, cost estimate, and whether fallback was used.

GET /metrics exposes Prometheus counters and histograms for requests, spend, latency, and failures.

## Engineering roadmap

- learned routing classifier;
- per-user budgets and policies;
- semantic caching;
- provider-health scoring;
- quality versus cost Pareto evaluation;
- dashboard and alerts.
