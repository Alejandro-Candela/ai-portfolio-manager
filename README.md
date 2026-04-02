# AI Portfolio Manager

A **multi-tenant SaaS application** for managing the full lifecycle of AI use cases within organizations—from intake through agent-based enrichment, scoring, and automated business case generation to human-in-the-loop approval.

Built with **LangGraph + FastAPI + Next.js** on Azure AI Foundry, designed for enterprise scale with row-level security (RLS) multi-tenancy, parallel agentic pipelines, and human approval workflows.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Installation](#installation)
- [Local Development](#local-development)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)
- [Frontend Routes & Components](#frontend-routes--components)
- [Environment Variables](#environment-variables)
- [Development Guidelines](#development-guidelines)
- [Known Limitations & Future Work](#known-limitations--future-work)
- [Contributing](#contributing)

---

## Overview

### Problem Statement

Enterprise organizations struggle to prioritize and evaluate AI initiatives across scattered teams. Ad-hoc intake forms, inconsistent evaluation criteria, and manual business case writing create bottlenecks and missed strategic alignment.

### Solution

**AI Portfolio Manager** automates the entire evaluation and business case workflow:

1. **Conversational Intake**: Capture use case details via chat
2. **Parallel Evaluation**: 4 autonomous agents score dimensions (security, feasibility, cost, value) in parallel
3. **Automated Scoring**: Weighted composite score ranked in portfolio backlog
4. **Business Case Generation**: AI writes draft → critic reviews → human approves/rejects/requests info
5. **Portfolio Dashboard**: Visualize all initiatives in matrix view, pipeline kanban, and trend analytics

### Use Cases

- **Internal backlogs**: Applied AI managing ~70 active AI initiatives
- **Consulting engagement**: Partner firms evaluating client portfolios
- **Enterprise SaaS**: Large organizations with 100+ use cases across departments

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 16)                        │
│  ┌────────────────┬──────────────┬─────────────┬──────────────┐ │
│  │  Portfolio     │   Pipeline   │ Intake Chat │  Cases/      │ │
│  │  Matrix        │   Kanban     │ (CopilotKit)│ Analytics    │ │
│  └────────────────┴──────────────┴─────────────┴──────────────┘ │
│                           ↕ (HTTP + WebSocket)                   │
├─────────────────────────────────────────────────────────────────┤
│                    Backend (FastAPI + LangGraph)                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  JWT Auth (Entra ID)  │  Tenant Isolation (RLS)            │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────┬──────────────┬────────────────────────────┐ │
│  │  Use Cases CRUD │ Evaluators   │ Business Case Generation  │ │
│  │  Routes         │  (Parallel)  │  (Writer → Critic → HITL) │ │
│  └─────────────────┴──────────────┴────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │             Scoring Engine | Ranking | Analytics           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ↕ (Async SQL)                          │
├─────────────────────────────────────────────────────────────────┤
│                  Database (PostgreSQL 16 + RLS)                  │
│  Tables: tenants, users, use_cases, evaluations, business_cases │
│          scoring_configs, audit_log                              │
├─────────────────────────────────────────────────────────────────┤
│           Azure AI Foundry (GPT-4o, o3-mini via LangChain)      │
└─────────────────────────────────────────────────────────────────┘
```

### Key Patterns

#### 1. Multi-Tenancy via PostgreSQL RLS
```python
# Connection middleware sets session variable
await conn.execute("SET app.tenant_id = %s", (tenant_id,))
# All subsequent queries filtered by RLS policy
```

#### 2. Parallel Evaluators via LangGraph Send API
```python
def route_to_evaluators(state):
    return [
        Send("security_eval", {"use_case": state["use_case"]}),
        Send("feasibility_eval", {"use_case": state["use_case"]}),
        Send("cost_eval", {"use_case": state["use_case"]}),
        Send("value_eval", {"use_case": state["use_case"]}),
    ]
```

#### 3. Human-in-the-Loop via LangGraph Interrupt
```python
def human_review_node(state):
    decision = interrupt({
        "business_case": state["draft"],
        "action_required": "approve|reject|request_info"
    })
    return {"human_decision": decision}
```

---

## Tech Stack

### Backend
- **FastAPI** (async web framework)
- **LangGraph 1.0+** (agentic orchestration)
- **LangChain** (LLM abstractions)
- **Azure OpenAI** (GPT-4o, o3-mini)
- **PostgreSQL 16** (relational + RLS)
- **psycopg3** (async driver)
- **SQLAlchemy 2.0** (ORM)
- **Pydantic v2** (validation)
- **PyJWT** (Entra ID tokens)

### Frontend
- **Next.js 16** (React App Router)
- **TypeScript** (strict mode)
- **TailwindCSS** (styling)
- **CopilotKit** (agentic UI)
- **Recharts** (visualization)
- **@hello-pangea/dnd** (drag-and-drop)
- **MSAL.js** (Entra ID auth)

---

## Features

### ✅ Implemented (Sprints 0–3)

- ✅ Multi-tenant CRUD API with JWT auth
- ✅ PostgreSQL schema with RLS foundation
- ✅ Async connection pool with tenant isolation
- ✅ Intake conversational graph (AG-UI streaming)
- ✅ 4 parallel evaluators (fan-out/fan-in)
- ✅ Weighted composite scoring engine
- ✅ Business case writer + critic loop
- ✅ Human-in-the-loop approval (interrupt/resume)
- ✅ Portfolio matrix scatter chart
- ✅ Pipeline kanban drag-and-drop
- ✅ Ranking + analytics dashboard
- ✅ Full test suite (unit + integration)

### 🔄 Planned (Sprints 4–7)

- [ ] Multi-language UI support
- [ ] Azure AI Search RAG integration
- [ ] Voice interviews (11Labs)
- [ ] OpenTelemetry tracing
- [ ] Terraform IaC
- [ ] Production hardening

---

## Installation

### Prerequisites

- Python 3.12+
- Node.js 20+ with `bun`
- Docker & Docker Compose
- Git

### Setup

```bash
git clone https://github.com/your-org/ai-portfolio-manager.git
cd ai-portfolio-manager

uv sync
cd frontend && bun install && cd ..

cp .env.example .env
# Edit .env with Azure credentials
```

---

## Local Development

### Start All Services

```bash
make dev
```

Opens FastAPI on `http://localhost:8000` and Next.js on `http://localhost:3000`.

### Individual Commands

```bash
make db        # PostgreSQL only
make backend   # FastAPI only
make frontend  # Next.js only
make migrate   # Run Alembic migrations
make test      # Run pytest
make lint      # Lint Python and TypeScript
make format    # Auto-format code
make clean     # Remove Docker containers
```

---

## API Documentation

### Use Cases

```
GET /api/use-cases
GET /api/use-cases/{id}
POST /api/use-cases
PATCH /api/use-cases/{id}
DELETE /api/use-cases/{id}
```

### Evaluations

```
POST /api/use-cases/{id}/evaluate          # Trigger 4-agent eval
GET /api/use-cases/{id}/evaluations        # Get scores
```

### Business Cases

```
POST /api/use-cases/{id}/generate-business-case
GET /api/use-cases/{id}/business-case
POST /api/use-cases/{id}/business-case/approve
POST /api/use-cases/{id}/business-case/reject
POST /api/use-cases/{id}/business-case/request-info
```

### Analytics

```
GET /api/use-cases/ranking   # Ranked backlog
GET /api/use-cases/summary   # Portfolio metrics
```

### Intake Chat

```
POST /api/langgraph/intake/invoke   # AG-UI streaming endpoint
```

---

## Frontend Routes

| Route | Component |
|-------|-----------|
| `/` | Redirect to `/portfolio` |
| `/portfolio` | Scatter matrix |
| `/pipeline` | Kanban board |
| `/cases/[id]` | Business case detail + HITL |
| `/intake` | Conversational chat |
| `/analytics` | Ranking table |

---

## Environment Variables

```bash
# Backend
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_DEPLOYMENT=gpt-4o
DATABASE_URL=postgresql+psycopg://...
ENTRA_ID_TENANT_ID=...
ENTRA_ID_CLIENT_ID=...
DEV_AUTH_BYPASS=true  # dev only

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENTRA_ID_CLIENT_ID=...
NEXT_PUBLIC_ENTRA_ID_AUTHORITY=https://login.microsoftonline.com/...

# Docker
POSTGRES_USER=portfoliomgr
POSTGRES_PASSWORD=devpassword
POSTGRES_DB=portfolio_db
```

---

## Development Guidelines

**Python**: PEP 8, type hints, async/await, Pydantic validation  
**TypeScript**: Strict mode, no `any`, functional components  
**Commits**: One change per commit, feature-prefixed messages  
**Testing**: Run `make test` before pushing  
**Linting**: `make lint && make format`

---

## Known Limitations & Future Work

### Sprints 4–7 Roadmap
- **Sprint 4** (Q2): Multi-language, dark mode, notifications
- **Sprint 5** (Q2): RLS enforcement, Azure AI Search RAG, tenant admin
- **Sprint 6** (Q3): Voice interviews, advanced analytics, Slack integration
- **Sprint 7** (Q3–Q4): OpenTelemetry, Terraform IaC, comprehensive tests, security audit

### Current Issues
1. HITL resume requires manual thread_id (will auto-resume in Sprint 7)
2. Evaluator scores may drift without calibration feedback loop
3. Scaling: PostgreSQL replicas needed for >100 concurrent users
4. Voice agent: placeholder routes only

---

## Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feat/your-feature`
3. Make atomic commits
4. Run `make lint && make format && make test`
5. Push and open PR to `main`

**Checklist**:
- [ ] All tests pass
- [ ] Code formatted
- [ ] No linter warnings
- [ ] Database migrations clean
- [ ] Commit messages follow convention
- [ ] `.env` not committed

---

## Support

- **Design Doc**: `docs/AI_PORTFOLIO_MANAGER_DESIGN.md`
- **Bug Reports**: GitHub Issues
- **Questions**: GitHub Discussions

---

**Last Updated**: April 2, 2026  
**Version**: 0.3.0 (Sprints 0–3 Complete)  
**Maintainer**: Alejandro Candela (Applied AI)
