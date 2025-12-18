# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Polaris is a multi-agent crisis response simulation system. Users submit geopolitical event descriptions, and the system models reactions from multiple world-leader archetype agents using RAG-enhanced LLM reasoning with vector similarity search on historical events.

## Tech Stack

- **Backend**: Python + FastAPI (async)
- **Database**: PostgreSQL with pgvector extension (1536-dim embeddings)
- **Frontend**: React
- **Validation**: Pydantic models for all API I/O

## Architecture

```
React UI → FastAPI REST → Agent Coordinator
                              ├─ embed(event)
                              ├─ vector_search(seed_data)
                              └─ spawn N leader agents concurrently
                                    └─ LLM prompt w/ leader traits + RAG context
                         → PostgreSQL + pgvector
```

## Database Schema

Four tables: `events` (text + embedding), `leader_profiles` (traits 0-10: aggression, diplomacy, risk_tolerance, domestic_pressure, escalation_threshold), `simulations`, `leader_sim_results` (escalation_score, reaction, rationale).

## API Endpoints

- `POST /api/simulate` - Submit event text, returns simulation results with per-leader scores
- `GET /api/history` - Past simulations
- `GET /api/leaders` - Leader profiles

## Key Constraints

- All I/O must be async
- LLM responses must be structured JSON with: leader, escalation_score, reaction, rationale, similar_events
- Leaders are archetypes (Revisionist Expansionist, Status-quo Diplomat, Crisis Populist, Isolationist Stabilizer) - not real individuals
- Seed data: 10-20 historical events embedded at startup, plus static leader profiles
