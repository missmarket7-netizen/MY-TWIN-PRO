# MyTwin – Architecture Document

## Hexagonal Architecture (Ports & Adapters)

## Layer Boundaries

| Layer | Can Call | Cannot Call |
|---|---|---|
| **api/routes/** | orchestration/, domain/services/ | repositories/, infrastructure/ (directly) |
| **orchestration/** | domain/services/, twin_state/, memory/, reasoning/ | repositories/, infrastructure/ (directly) |
| **domain/services/** | repositories/ | twin_state/, memory/, reasoning/ |
| **twin_state/** | repositories/ | orchestration/, api/ |
| **memory/** | repositories/ | orchestration/, api/ |
| **reasoning/** | infrastructure/ai/ | repositories/ |
| **repositories/** | infrastructure/database/ | Nothing |
| **infrastructure/** | External services | Nothing |

## Key Rules

1. **Orchestrator is the ONLY coordinator.** Services never call each other directly.
2. **Repositories are the ONLY database access.** No direct Supabase calls from services.
3. **Domain services are PURE logic.** They don't know about HTTP, databases, or UI.
4. **Events are fire-and-forget.** Publishers don't wait for subscribers.

## Directory Structure

- `api/` – HTTP layer (FastAPI routes, dependencies)
- `orchestration/` – Central coordinator
- `domain/` – Business logic (tiers, billing, safety, cost)
- `twin_state/` – Twin personality (identity, relationship, journey, attachment, personality)
- `memory/` – Long-term memory (retrieval, extraction, ranking)
- `reasoning/` – AI providers (council, self-critic, provider router)
- `repositories/` – Data access layer
- `infrastructure/` – External integrations (AI clients, database, cache, voice)
- `events/` – Event bus and handlers
- `background/` – Background task queue
