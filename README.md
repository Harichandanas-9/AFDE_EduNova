# EduNova AI

**Your AI Career & Learning Copilot.**

EduNova AI is a production-ready AI platform focused exclusively on **education, learning, quizzes, study planning, resume building, skill analysis, interview preparation, course recommendations, and career growth**. It pairs a modern glassmorphism React frontend with a scalable FastAPI backend, orchestrated by a LangGraph multi-agent workflow and gated by DeepEval-based answer validation.

---

## Highlights

- **LangGraph multi-agent workflow** — Guardrail → Router → Specialised Agent → DeepEval → response, with automatic retries on failed evaluations.
- **9 dedicated agents** — Router, Quiz, Study Planner, Resume Builder, Skill Gap, Recommendation, Chat, Guardrail, DeepEval.
- **Strict educational guardrails** — rule-based denylist + allowlist + restricted system prompts. Politics, NSFW, hacking, medical/financial advice, and other unrelated topics are blocked.
- **LLM abstraction** — pluggable OpenAI / Gemini providers with a deterministic mock fallback so the entire app runs end-to-end with no API keys.
- **DeepEval integration** — answer relevance, faithfulness, and hallucination scoring with automatic retry-on-failure.
- **Scalable FastAPI backend** — async routes, SQLAlchemy ORM, request logging, rate limiting, centralized exceptions, JWT-ready architecture, API versioning, health checks.
- **Modern React frontend** — Vite, Tailwind, Framer Motion, Lucide icons, Recharts, glassmorphism UI, animated sidebar, markdown chat with syntax highlighting, loading skeletons, toast notifications, fully responsive.
- **Render deployment** — single `render.yaml` provisions backend (web service), frontend (static), and Postgres database.

## Theme

Sea Blue · Lavender · White · Light Bluish Green (mint) · Light Pink (blush) — a soft, glassmorphism palette designed for clarity and warmth.

---

## Project structure

```
EduNova BOT/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI factory
│   │   ├── config.py                # Pydantic settings
│   │   ├── agents/                  # LangGraph multi-agent workflow
│   │   │   ├── workflow.py
│   │   │   ├── router_agent.py
│   │   │   ├── guardrail_agent.py
│   │   │   ├── chat_agent.py
│   │   │   ├── quiz_agent.py
│   │   │   ├── study_planner_agent.py
│   │   │   ├── resume_agent.py
│   │   │   ├── skill_gap_agent.py
│   │   │   ├── recommendation_agent.py
│   │   │   └── evaluation_agent.py
│   │   ├── routes/                  # FastAPI routers
│   │   ├── models/                  # SQLAlchemy models
│   │   ├── schemas/                 # Pydantic schemas
│   │   ├── services/llm_service.py  # OpenAI / Gemini / mock
│   │   ├── evaluation/              # DeepEval evaluator
│   │   ├── guardrails/              # Content filter
│   │   ├── middleware/              # Logging, exceptions, rate limit
│   │   ├── database/                # Async SQLAlchemy session
│   │   └── utils/logger.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   ├── components/              # Sidebar, Layout, ChatMessage, GlassCard, Toaster…
│   │   ├── pages/                   # Dashboard, Chat, QuizGenerator, StudyPlanner, ResumeBuilder,
│   │   │                            #   SkillGapAnalyzer, Recommendations, Analytics, Settings
│   │   ├── store/useStore.js        # Zustand
│   │   ├── hooks/useToast.js
│   │   └── utils/api.js
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.example
│
├── render.yaml
├── .gitignore
└── README.md
```

---

## Quick start — local

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
# If that's slow or any package fails to build on your machine,
# use the lean install (LangGraph/DeepEval are optional — the app has fallbacks):
#   pip install -r requirements-minimal.txt
cp .env.example .env       # (Windows) copy .env.example .env

uvicorn app.main:app --reload
```

The API will be live at <http://localhost:8000>. Interactive docs: <http://localhost:8000/docs>.

By default the backend uses **SQLite** and the **mock LLM provider**, so it runs with zero external dependencies. To switch to OpenAI / Gemini, set `LLM_PROVIDER` and the relevant API key in `.env`.

### Frontend (React + Vite)

```bash
cd frontend
npm install
cp .env.example .env       # (Windows) copy .env.example .env
npm run dev
```

Open <http://localhost:5173>. The Vite dev server proxies `/api/*` to the backend automatically.

---

## Environment variables

### Backend (`backend/.env`)

| Variable | Default | Notes |
|---|---|---|
| `APP_NAME` | `EduNova AI` | |
| `ENVIRONMENT` | `development` | `production` on Render |
| `DEBUG` | `true` | |
| `SECRET_KEY` | *change me* | Used by JWT-ready architecture |
| `CORS_ORIGINS` | localhost dev origins | JSON array string |
| `DATABASE_URL` | `sqlite+aiosqlite:///./edunova.db` | Use a Postgres URL in prod |
| `LLM_PROVIDER` | `mock` | `openai` \| `gemini` \| `mock` |
| `OPENAI_API_KEY` | – | required if `LLM_PROVIDER=openai` |
| `OPENAI_MODEL` | `gpt-4o-mini` | |
| `GEMINI_API_KEY` | – | required if `LLM_PROVIDER=gemini` |
| `GEMINI_MODEL` | `gemini-1.5-flash` | |
| `DEEPEVAL_ENABLED` | `true` | |
| `DEEPEVAL_THRESHOLD` | `0.6` | |
| `DEEPEVAL_MAX_RETRIES` | `2` | |
| `RATE_LIMIT_REQUESTS` | `60` | per IP per window |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | |
| `LOG_LEVEL` | `INFO` | |

### Frontend (`frontend/.env`)

| Variable | Default | Notes |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | Override in prod to point at your Render backend |

---

## API surface

All routes are prefixed with `/api/v1`.

| Method | Path | Purpose |
|---|---|---|
| GET  | `/health` | Liveness check |
| POST | `/chat` | Chat through the LangGraph workflow |
| GET  | `/chat/history/{session_id}` | Replay a chat session |
| POST | `/quiz/generate` | Generate a quiz |
| POST | `/quiz/submit` | Submit answers, score, get feedback + adaptive difficulty |
| GET  | `/quiz/recent` | Recent quizzes |
| GET  | `/quiz/results/recent` | Recent quiz results |
| POST | `/study-plan` | Build an N-week study plan |
| GET  | `/study-plan/{id}` | Retrieve a plan |
| POST | `/resume/build` | AI-generated ATS-friendly resume |
| GET  | `/resume/{id}/markdown` | Resume as markdown |
| POST | `/skill-gap` | Skill gap analysis with readiness % |
| POST | `/recommendations` | Curated learning resources |

OpenAPI / Swagger UI: `/docs` · ReDoc: `/redoc`.

---

## LangGraph workflow

```
            ┌────────────────┐
user input  │ Guardrail Agent├──► blocked → END
            └────────┬───────┘
                     ▼
              ┌──────────────┐
              │ Router Agent │
              └──────┬───────┘
                     ▼
   ┌────────┬────────┴─────────┬────────┬────────┬────────┐
   ▼        ▼                  ▼        ▼        ▼        ▼
  chat    quiz          study_planner resume skill_gap recommendation
   └────────┴───────┬──────────┴────────┴────────┴────────┘
                    ▼
            ┌──────────────────┐
            │ DeepEval node    │
            └────────┬─────────┘
                     │
       eval_passed ──┤── retries < max → re-run specialist
                     ▼
                    END
```

If `langgraph` is not installed at runtime, a built-in sequential runner with identical semantics is used so the API never breaks.

---

## Guardrails

`app/guardrails/content_filter.py` rejects:

- Politics, NSFW, violence, hacking/malware, illegal drugs
- Medical / financial / legal advice
- Self-harm
- Off-topic chit-chat

…and returns the canonical message:

> "I'm designed specifically for educational and career-related assistance."

A second layer is enforced inside each agent's system prompt.

---

## DeepEval

`app/evaluation/deepeval_evaluator.py` wraps `deepeval` with a heuristic fallback. The workflow re-invokes the specialist agent up to `DEEPEVAL_MAX_RETRIES` times if `score < DEEPEVAL_THRESHOLD`.

---

## Deploy to Render

1. Push the repo to GitHub.
2. In Render, click **New → Blueprint** and point at the repo. Render reads `render.yaml` and provisions:
   - `edunova-backend` (Python web service)
   - `edunova-frontend` (Vite static site, SPA rewrite for client routing)
   - `edunova-db` (Postgres)
3. In the backend service, set the runtime secret `OPENAI_API_KEY` (and/or `GEMINI_API_KEY`) under **Environment**.
4. (Optional) Update `CORS_ORIGINS` and the frontend `VITE_API_BASE_URL` to your real Render URLs.

Backend startup command (matches `render.yaml`):

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Frontend build:

```bash
npm install && npm run build
```

---

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, Framer Motion, Lucide React, Recharts, React Router, Zustand, Axios, React-Markdown |
| Backend  | FastAPI, SQLAlchemy 2 (async), Pydantic v2, Uvicorn |
| Database | PostgreSQL (prod) / SQLite (dev) |
| AI       | LangGraph, LangChain, OpenAI, Gemini, DeepEval |
| Deploy   | Render (web service + static site + Postgres) |

---

## License

Made with ❤️ for learners.
