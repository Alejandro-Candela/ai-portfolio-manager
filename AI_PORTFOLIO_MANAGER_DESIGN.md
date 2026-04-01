# AI Use Case Portfolio Manager — Diseño de implementación

## Qué es y qué problema resuelve

Una aplicación web multi-tenant sobre Azure AI Foundry que gestiona el ciclo de vida completo de los casos de uso de IA dentro de una organización: desde la captura de la idea hasta la decisión de go/no-go con business case generado.

Applied AI lo necesita en tres contextos simultáneos:

1. **Interno** — gestionar sus propios ~70 casos de uso en backlog
2. **Organizaciones vecinas** — consultoras más pequeñas alemanas con su propia instancia
3. **Clientes enterprise** — como oferta SaaS de consultoría, cada cliente con su tenant

---

## Flujo principal de la aplicación

```
Stakeholder tiene una idea de caso de uso de IA
         │
         ▼
┌─────────────────────────────────────────────┐
│  1. INTAKE — Captura del caso de uso        │
│                                             │
│  Opción A: Formulario web estructurado      │
│  Opción B: Entrevista con agente de voz     │
│            (11Labs + teléfono conectado)     │
│  Opción C: Chat conversacional en dashboard │
│                                             │
│  El agente de intake extrae:                │
│  - Descripción del problema                 │
│  - Stakeholders involucrados               │
│  - Datos disponibles                        │
│  - Resultado esperado                       │
│  - Urgencia percibida                       │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  2. ENRIQUECIMIENTO — Agentes evalúan       │
│                                             │
│  Agente de Seguridad → riesgo de datos,     │
│    compliance (GDPR, ENS), PII expuesta     │
│                                             │
│  Agente de Viabilidad → complejidad técnica,│
│    datos necesarios vs disponibles,         │
│    integraciones requeridas                 │
│                                             │
│  Agente de Costes → estimación de infra,    │
│    licencias, horas de desarrollo,          │
│    coste operativo mensual                  │
│                                             │
│  Agente de Valor → impacto en negocio,      │
│    ahorro estimado, revenue potencial,      │
│    alineación estratégica                   │
│                                             │
│  Cada agente produce un score 1-10 +        │
│  justificación textual                      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  3. SCORING & RANKING — Priorización        │
│                                             │
│  Score compuesto configurable por tenant:   │
│  - Peso de cada dimensión ajustable         │
│  - Fórmula: weighted sum normalizada        │
│  - Ranking automático del backlog completo  │
│  - Detección de dependencias entre casos    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  4. BUSINESS CASE — Generación automática   │
│                                             │
│  El agente Writer genera un documento con:  │
│  - Executive summary                        │
│  - Problema y oportunidad                   │
│  - Solución propuesta                       │
│  - Análisis coste-beneficio                 │
│  - Riesgos y mitigaciones                   │
│  - Timeline estimado                        │
│  - Recomendación go/no-go                   │
│                                             │
│  Revisado por agente Critic antes de        │
│  presentarse al humano (patrón HITL)        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  5. DECISIÓN HUMANA (HITL)                  │
│                                             │
│  Dashboard presenta al decisor:             │
│  - Portfolio visual (bubble chart o matrix) │
│  - Business case generado                   │
│  - Scores por dimensión                     │
│  - Comparación con otros casos del backlog  │
│                                             │
│  Acciones: Aprobar / Rechazar / Pedir más   │
│  info / Re-priorizar / Archivar             │
└─────────────────────────────────────────────┘
```

---

## Arquitectura técnica

```
                    ┌──────────────────────────────┐
                    │  Next.js Dashboard            │
                    │  (AG-UI + CopilotKit)         │
                    │                               │
                    │  • Portfolio Kanban/Matrix     │
                    │  • Chat panel para intake      │
                    │  • Business case viewer        │
                    │  • Admin panel multi-tenant    │
                    └──────────┬───────────────────┘
                               │ REST + WebSocket (AG-UI)
                               ▼
┌──────────────────────────────────────────────────────────┐
│  FastAPI + LangGraph (Orquestación de agentes)           │
│                                                          │
│  Graphs:                                                 │
│  ├── intake_graph        → captura conversacional        │
│  ├── evaluation_graph    → 4 agentes evaluadores         │
│  ├── business_case_graph → writer + critic + HITL        │
│  └── interview_graph     → entrevista de voz a stakeholder│
│                                                          │
│  ┌──────────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │ Azure Content│  │ Tenant      │  │ Azure Functions │  │
│  │ Safety       │  │ Middleware  │  │ (voice webhook) │  │
│  └──────────────┘  └─────────────┘  └────────────────┘  │
└───────────────────────────┬──────────────────────────────┘
          │                 │                    │
          ▼                 ▼                    ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Azure AI     │  │ Azure PostgreSQL │  │ Azure AI Search  │
│ Foundry      │  │ Flexible Server  │  │ (RAG sobre docs  │
│              │  │                  │  │  de cada tenant)  │
│ GPT-4o para  │  │ • use_cases      │  │                  │
│ evaluación   │  │ • evaluations    │  │ Documentos de    │
│              │  │ • business_cases │  │ contexto: políticas│
│ o3-mini para │  │ • tenants        │  │ de seguridad,     │
│ supervisor   │  │ • scoring_config │  │ estándares, docs  │
│              │  │ • audit_log      │  │ técnicos internos │
└──────────────┘  └──────────────────┘  └──────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────┐
│  Azure Monitor + Application Insights + OTel             │
│  LangSmith (trazabilidad completa de agentes)            │
└──────────────────────────────────────────────────────────┘
```

---

## Multi-tenancy

Cada organización (Applied AI, cliente enterprise, organización vecina) recibe un tenant aislado. La estrategia es **schema compartido con row-level security** en PostgreSQL, que es más eficiente que instancias separadas y permite escalar sin multiplicar infraestructura.

```
Tenant: applied-ai-internal
  ├── 70 use cases en backlog
  ├── scoring weights: seguridad=0.3, valor=0.3, viabilidad=0.2, coste=0.2
  ├── AI Search index propio (docs internos)
  └── 3 usuarios decisores

Tenant: german-consulting-partner
  ├── 15 use cases de sus clientes SMB
  ├── scoring weights: coste=0.4, viabilidad=0.3, valor=0.2, seguridad=0.1
  ├── AI Search index propio
  └── 2 usuarios

Tenant: ibex35-bank-client
  ├── 40 use cases
  ├── scoring weights: seguridad=0.5, compliance=0.2, valor=0.2, coste=0.1
  ├── AI Search index propio (regulaciones bancarias)
  └── 5 usuarios decisores + CISO como aprobador final
```

Cada tenant configura:

- Los pesos de scoring según sus prioridades
- Las dimensiones de evaluación (añadir/quitar)
- Los gates de aprobación (quién aprueba qué)
- Los documentos de contexto para RAG (políticas, estándares)
- La identidad visual del dashboard

---

## Dashboard — Vistas principales

### 1. Portfolio Matrix

Vista tipo bubble chart: eje X = valor de negocio, eje Y = viabilidad técnica, tamaño de burbuja = coste estimado, color = nivel de riesgo. Los decisores ven de un vistazo dónde están los quick wins (arriba derecha, burbuja pequeña, color verde).

### 2. Pipeline Kanban

Columnas: Nuevo → En evaluación → Business case generado → En revisión → Aprobado → En implementación → Archivado. Drag and drop para mover. Filtros por departamento, por sponsor, por score mínimo.

### 3. Business Case Viewer

Documento renderizado con el business case auto-generado. Panel lateral con los scores desglosados y la justificación de cada agente. Botones de Aprobar/Rechazar/Pedir más info. Historial de cambios y re-evaluaciones.

### 4. Intake Assistant

Chat embebido donde stakeholders describen su idea conversacionalmente. El agente guía la conversación para extraer toda la información necesaria. También accesible por voz (llamada telefónica vía 11Labs + Azure Functions webhook).

### 5. Analytics

Métricas del portfolio: distribución de scores, tiempo medio de evaluación, tasa de aprobación, distribución por departamento, trending de nuevos casos por mes, comparación entre tenants (para la vista admin de Applied AI).

---

```
    portfolio-manager/
        ├── .env.example
        ├── config.yaml.example
        ├── docker-compose.yml
        ├── Makefile
        ├── pyproject.toml
        ├── README.md
        ├── ARCHITECTURE.md
        ├── src/
        │   ├── agents/
        │   │   ├── intake.py           ← grafo LangGraph de captura
        │   │   ├── evaluators/
        │   │   │   ├── security.py     ← agente de riesgo/seguridad
        │   │   │   ├── feasibility.py  ← agente de viabilidad
        │   │   │   ├── cost.py         ← agente de costes
        │   │   │   └── value.py        ← agente de valor de negocio
        │   │   ├── business_case.py    ← writer + critic
        │   │   └── interviewer.py      ← entrevista por voz
        │   ├── scoring/
        │   │   ├── engine.py           ← weighted scoring configurable
        │   │   └── ranking.py          ← priorización del backlog
        │   ├── tenancy/
        │   │   ├── middleware.py        ← tenant resolution por JWT
        │   │   ├── isolation.py         ← row-level security
        │   │   └── config_loader.py     ← scoring weights por tenant
        │   ├── api/
        │   │   ├── main.py             ← FastAPI
        │   │   ├── routes/
        │   │   │   ├── use_cases.py
        │   │   │   ├── evaluations.py
        │   │   │   ├── business_cases.py
        │   │   │   ├── tenants.py
        │   │   │   └── analytics.py
        │   │   └── websocket.py        ← AG-UI streaming
        │   ├── voice/
        │   │   ├── eleven_labs.py       ← integración voz
        │   │   └── phone_webhook.py     ← Azure Functions bridge
        │   ├── config/
        │   │   └── settings.py
        │   └── utils/
        │       └── logging.py
        ├── frontend/
        │   ├── package.json
        │   └── src/
        │       ├── app/
        │       │   ├── portfolio/       ← matrix view
        │       │   ├── pipeline/        ← kanban
        │       │   ├── cases/[id]/      ← business case viewer
        │       │   ├── intake/          ← chat assistant
        │       │   └── analytics/       ← dashboards
        │       └── components/
        │           ├── BubbleChart.tsx
        │           ├── KanbanBoard.tsx
        │           ├── ScoreRadar.tsx   ← radar chart de dimensiones
        │           └── ChatPanel.tsx    ← CopilotKit
        ├── infra/
        │   ├── terraform/              ← Azure provisioning
        │   ├── bicep/                  ← alternativa ARM
        │   └── otel/
        ├── tests/
        │   ├── unit/
        │   ├── integration/
        │   └── conftest.py
        └── prompts/
            ├── intake_system.md
            ├── security_evaluator.md
            ├── feasibility_evaluator.md
            ├── cost_evaluator.md
            ├── value_evaluator.md
            ├── business_case_writer.md
            └── business_case_critic.md
```

---

## Stack tecnológico concreto

| Capa                 | Tecnología                          | Justificación                                             |
| -------------------- | ----------------------------------- | --------------------------------------------------------- |
| Frontend             | Next.js + CopilotKit (AG-UI)        | Microsoft Agentic UI protocol, mismo que azure-enterprise |
| Backend API          | FastAPI                             | Consistente con todos los blueprints                      |
| Orquestación agentes | LangGraph                           | Stateful graphs con checkpointing, HITL nativo            |
| Inference            | Azure AI Foundry (GPT-4o + o3-mini) | Requisito explícito de la transcripción                   |
| Base de datos        | Azure PostgreSQL Flexible           | Row-level security para multi-tenancy                     |
| Vector search        | Azure AI Search                     | RAG sobre documentos de contexto por tenant               |
| Voz                  | 11Labs + Azure Functions            | Ya tienen voice agents con 11Labs                         |
| Observabilidad       | Azure Monitor + OTel + LangSmith    | Trazabilidad completa de decisiones agénticas             |
| Auth                 | Microsoft Entra ID (Azure AD)       | SSO corporativo, RBAC por tenant                          |
| Infra                | Terraform + Azure Container Apps    | Consistente con azure-enterprise                          |
