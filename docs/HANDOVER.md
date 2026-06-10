# Project Handover: Entrepreneur Lab AI Co-Founder

**Project:** The Entrepreneur Lab — AI Virtual Co-Founder  
**Handover date:** June 2026  
**Prepared by:** Previous development team

---

## 1. What This Project Is

An AI chatbot application that acts as a virtual co-founder for entrepreneurs. Users log in via the Entrepreneur Lab's Bubble.io platform and are redirected to this app where they can:

- Chat freely with an AI that helps brainstorm ideas, generate roadmaps, and search for resources
- Work through a guided 7-step entrepreneur journey (foundation → launch → growth)
- Download Excel workbook templates for each step
- Get AI-generated logo/image concepts

The application consists of two independent codebases on separate branches in the same git repository.

---

## 2. Repository Structure

```
git repo: ai-bot-handover
├── main branch          → documentation only (this repo)
├── dev/backend          → Django backend (production code)
├── dev/backend-change-1-disable-token  → same + token bypass feature
├── dev/frontend         → React frontend (production code)
└── dev/frontend-change-1-disable-token → same (no actual changes)
```

**Important:** Backend and frontend live on separate branches. You must check out the appropriate branch to work on either.

---

## 3. Technology Summary

| Layer | Technology |
|-------|-----------|
| Backend language | Python 3.12 |
| Backend framework | Django 5.2 + Django REST Framework |
| AI orchestration | LangGraph 0.6 + LangChain 0.3 |
| LLM | OpenAI GPT-4o |
| Image generation | OpenAI DALL-E 3 |
| Vector search (RAG) | Pinecone |
| Web search | DuckDuckGo |
| Business search | Google Places API |
| Database | PostgreSQL (primary + LangGraph state) |
| Cache / pub-sub | Redis |
| WebSocket | Django Channels |
| ASGI server | Uvicorn |
| Frontend framework | React 19 + Vite 7 |
| Frontend styling | Tailwind CSS 4 + Material UI 7 |
| Frontend routing | React Router DOM 7 |
| Frontend deployment | Vercel |
| Auth integration | Bubble.io → JWT |

---

## 4. External Services & Credentials Required

You will need accounts / API keys for all of the following before the app can run.

| Service | What it's used for | Where to get it |
|---------|------------------|----------------|
| **OpenAI** | GPT-4o chat + DALL-E 3 images + embeddings | platform.openai.com |
| **Pinecone** | Vector database for knowledge retrieval (RAG) | pinecone.io |
| **Google Cloud** | Places API (business/professional search) | console.cloud.google.com |
| **Bubble.io** | User authentication (SSO source) | bubble.io — get API key from the Entrepreneur Lab Bubble app |
| **PostgreSQL** | Primary database + LangGraph conversation checkpointing | Self-hosted or managed (Supabase, RDS, etc.) |
| **Redis** | Session caching + WebSocket pub/sub | Self-hosted or managed (Redis Cloud, Upstash) |

---

## 5. Backend Setup

### Prerequisites

- Python **3.12.10** (exact version recommended)
- PostgreSQL running and accessible
- Redis running locally or remotely
- All API keys from Section 4

### Step-by-step

```bash
# 1. Clone repo and switch to backend branch
git clone <repo-url>
cd ai-bot-handover
git checkout dev/backend

# 2. Create a virtual environment
python -m venv venv/backend

# 3. Activate it
source venv/backend/bin/activate        # Linux/Mac
# venv\backend\Scripts\activate         # Windows

# 4. Install dependencies
cd src
python -m pip install --upgrade pip
pip install -r ../requirements.txt

# 5. Create environment file
cp .env.example .env                    # if example exists, otherwise create manually
```

### Environment File (`.env` — place in `src/`)

Create `src/.env` with the following:

```bash
# Server
HOST=localhost
PORT=9018

# PostgreSQL
DBNAME=brundadb
DBHOST=localhost
DBPORT=5432
DBUSER=<your_db_user>
DBPASSWORD=<your_db_password>

# OpenAI
OPENAI_API_KEY=<your_openai_key>
OPENAI_CHAT_MODEL=gpt-4o
MODEL_PLATFORM=openai

# Bubble.io (external auth platform)
BUBBLE_API_KEY=<your_bubble_api_key>
BUBBLE_BASE_URL=https://api.bubble.io
BUBBLE_PASSWORD_DEFAULT=1234567890

# Pinecone (vector DB for RAG)
PINECONE_API_KEY=<your_pinecone_key>
PINECONE_INDEX_NAME=<your_index_name>

# Google Places API
GOOGLE_API_KEY=<your_google_api_key>

# URLs (update for your environment)
FRONTEND_URL=http://localhost:5173?sid={}
BACKEND_URL=http://localhost:9018

# Django settings (change SECRET_KEY in production)
DEBUG=True
SECRET_KEY=django-insecure-na5)h(vh)!gt4=%*--=&qgn1%c7qpp-p29ytl&d1^ux!8eli9z
ALLOWED_HOSTS=*

# Token exemptions (comma-separated emails that skip token budget checks)
TOKEN_DISABLE_ACCOUNT=
```

### Database Setup

```bash
# From src/ directory (with virtualenv active)

# Run Django migrations
python manage.py migrate

# LangGraph tables are created automatically on server startup
# (AsyncPostgresSaver.setup() runs during ASGI lifespan)
```

### Start the Backend Server

```bash
# From src/ directory
python run_uvicorn.py
```

Server starts on `http://localhost:9018` (or whatever HOST/PORT you set).

The startup sequence:
1. Loads `.env`
2. Connects to PostgreSQL — creates LangGraph checkpoint tables if they don't exist
3. Compiles both LangGraph agent DAGs
4. Begins accepting HTTP + WebSocket connections

---

## 6. Frontend Setup

### Prerequisites

- Node.js **v22.20.0** (exact version recommended — use nvm)

### Step-by-step

```bash
# Switch to frontend branch
git checkout dev/frontend

# Install dependencies
npm install

# Create environment file
touch .env
```

### Environment File (`.env` — place in root of frontend branch)

```bash
VITE_CHAT_API_BASE_URL=http://localhost:9018
VITE_EXTERNAL_DASHBOARD_URL=https://dashboard.thentrepreneurlab.com/entrepreneur
```

- `VITE_CHAT_API_BASE_URL` — points to your running backend
- `VITE_EXTERNAL_DASHBOARD_URL` — where users are redirected when they click non-chat sidebar links (your Bubble.io dashboard)

### Start the Frontend Dev Server

```bash
npm run dev
```

Frontend runs on `http://localhost:5173`.

### Production Build

```bash
npm run build
# Output: dist/
# Deploy dist/ to Vercel or any static host
```

---

## 7. How Authentication Works

This is the most important flow to understand. The app does **not** have its own login page.

```
1. User logs in on Bubble.io (the Entrepreneur Lab's main platform)

2. Bubble.io calls: POST /api/bubble/auth/?user_id=<id>&email=<email>
   Backend creates/finds the user record, generates a session token (SID),
   and returns a redirect URL: https://agent.thentrepreneurlab.com?sid=<token>

3. User's browser is redirected to the frontend with ?sid= in the URL

4. Frontend detects the SID, exchanges it for JWT tokens:
   GET /api/bubble/auth/?sid=<token>
   → Receives { access: "...", refresh: "..." }
   → Stores both in localStorage

5. All subsequent API calls use:
   Authorization: Bearer <access_token>

6. If a 401 is received, the frontend automatically refreshes via:
   POST /api/bubble/refresh/
```

**For local development / testing:** You can manually create a user in Django admin and generate a JWT token, bypassing the Bubble.io flow. Or use the `TOKEN_DISABLE_ACCOUNT` env var to skip token checks for test emails.

---

## 8. Architecture Overview

### Backend Agent Pipeline

There are two AI agent pipelines, both built with LangGraph:

**Pipeline 1 — Freeform Chat** (`POST /api/chat/agent/`)

```
User message
    ↓
Router Agent (GPT-4o classifies intent)
    ↓
┌───────────────────────────────────┐
│                                   │
Ideation Agent                  Roadmap Agent
(brainstorming, Q&A,           (structured multi-step
market research,               roadmap generation)
freelancer search)                  ↓
    ↓                      Enrich with Pinecone resources
Overview Agent                      ↓
(polish response)         ─────────────────────────────
    ↓                              OR
    └─────────────────── Image Generation Agent (DALL-E 3)
```

**Pipeline 2 — Structured 7-Step Journey** (`POST /api/chat/structured-agent/`)

```
User message + step number (1-7)
    ↓
Routes to the matching step node
    ↓
Step-specific AI prompt (objectives, templates, resources for that step)
    ↓
React agent with access to: Pinecone, market search, freelancer search, Google Places
```

### LangGraph Conversation State

Every conversation turn is checkpointed to PostgreSQL. This means:
- Conversations persist across server restarts
- Full history is always available for context
- The `chat_id` (UUID) is the key — it maps to a LangGraph `thread_id`

### Real-Time WebSocket Updates

While the backend processes a request, it publishes step-by-step progress events to Redis, which the WebSocket consumer forwards to connected clients. The frontend does **not** currently connect to this WebSocket — it's available for future use.

### Frontend State

Single-page app. All chat state is managed in `ChatWindow.jsx` via `useReducer`. No global state library. Auth tokens live in `localStorage`.

---

## 9. Key API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/bubble/auth/` | POST | Bubble.io calls this — creates SID token, returns redirect URL |
| `/api/bubble/auth/` | GET | Frontend calls with `?sid=` — returns JWT tokens |
| `/api/bubble/refresh/` | POST | Refresh expired JWT access token |
| `/api/chat/new-chat/` | GET | Create a new chat session |
| `/api/chat/history/` | GET | List all chats for current user |
| `/api/chat/history/?chat-id=` | GET | Get message history for a specific chat |
| `/api/chat/agent/?chat-id=` | POST | Send message to freeform agent |
| `/api/chat/structured-agent/?chat-id=` | POST | Send message to 7-step agent |
| `/api/chat/token/` | GET | Get token budget stats (used / total) |
| `/api/chat/template/<filename>/` | GET | Download Excel template file |
| `/ws/static/<chat_id>/` | WS | Real-time agent progress events |

---

## 10. The 7 Entrepreneur Steps

The structured journey maps step numbers to these topics:

| Step | Topic |
|------|-------|
| 1 | Foundation & Personal Finance |
| 2 | Business Idea Validation |
| 3 | Legal Compliance & Financial Modeling |
| 4 | MVP Planning |
| 5 | Business Setup & Branding |
| 6 | Launch Strategy |
| 7 | Operations & Growth Management |

Each step has:
- A dedicated AI system prompt with objectives and guidance
- Excel workbook templates (stored in `src/media/templates/step-N/`)
- A Pinecone query to enrich responses with relevant resources

---

## 11. Token Budget System

Each user has a token budget stored in the `ai_tokenusage` database table:
- `token_count` — allocated tokens (default: 60,000)
- `token_used` — cumulative tokens consumed

Every GPT-4o call tracks actual token usage (via a `TrackedModel` wrapper). After each request, the total is added to `token_used`.

When a user exhausts their budget, the API returns HTTP `402`. The frontend disables the send button and shows a notification.

To bypass token checks for specific accounts (useful for testing or admin accounts), add emails to the `TOKEN_DISABLE_ACCOUNT` environment variable:
```
TOKEN_DISABLE_ACCOUNT=admin@example.com,test@example.com
```

---

## 12. Pinecone / RAG Setup

The Pinecone vector database stores knowledge resources (articles, guides, tools) that the AI retrieves when responding to users.

To populate Pinecone with data, use the script in the `scripts/` directory on the main branch:
```bash
python scripts/generate_data_embedding.py
```

This uses the `text-embedding-3-large` model to embed documents and upsert them to your Pinecone index.

---

## 13. Known Issues & Gotchas

### Typos in API Responses (do not "fix" without updating frontend too)

These typos are in the live API and the frontend handles them explicitly:

| Field | Typo | Found in |
|-------|------|---------|
| `messsage` | Three s's | Bubble auth GET response |
| `notifiy` | Misspelled | Token 402 error response |
| `Autentication` | Missing 'h' | SID expiry error message |

### `run_uvicorn.py` vs `run.py`

Both files do the same thing. `run_uvicorn.py` is the active one referenced in the README. `run.py` is a legacy duplicate.

### CORS is wide open

`CORS_ALLOW_ALL_ORIGINS = True` in settings. Restrict to your frontend domain before going to production:
```python
CORS_ALLOWED_ORIGINS = ["https://agent.thentrepreneurlab.com"]
```

### `SECRET_KEY` is hardcoded

The Django `SECRET_KEY` in `.env.example` is a known/exposed key. Generate a new one for any deployment:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Frontend WebSocket not connected

The backend has WebSocket endpoints (`/ws/static/<id>/`) that publish real-time agent progress. The frontend currently does not connect to them — only the final response is shown. Wiring this up would improve UX significantly.

### File upload is incomplete

The frontend has a file upload UI that is hidden (CSS `hidden` class). There is no corresponding backend endpoint to handle uploads. It's a stub for a future feature.

### No message pagination

The frontend loads the entire chat history into memory at once. For very long conversations this may become slow.

### Hardcoded UI elements

The Navbar shows a hardcoded user name ("Brunda") and a hardcoded notification badge ("2"). These are not fetched from any API.

---

## 14. Detailed Technical Documentation

Full technical reference documents are in the `docs/` folder on the `main` branch:

| Document | Contents |
|----------|---------|
| `docs/BACKEND_ARCHITECTURE.md` | Complete backend reference: all models, endpoints, LangGraph DAGs, data flows, prompts, Redis config, startup sequence |
| `docs/FRONTEND_ARCHITECTURE.md` | Complete frontend reference: component tree, auth flow, state management, API integration, all user journeys |

---

## 15. Deployment Notes

### Backend

- The server is ASGI-based. Use Uvicorn directly or behind Nginx.
- Requires `lifespan="on"` for LangGraph initialization to run.
- Set `DEBUG=False` and a real `SECRET_KEY` in production.
- Lock down `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`.

### Frontend

- Build with `npm run build`, deploy `dist/` to Vercel or any static host.
- All routes must fall back to `index.html` (already configured in `vercel.json`).
- Set `VITE_CHAT_API_BASE_URL` to your production backend URL at build time.

### Infrastructure checklist

- [ ] PostgreSQL database created and credentials set in `.env`
- [ ] Redis instance running and accessible
- [ ] OpenAI API key with GPT-4o and DALL-E 3 access
- [ ] Pinecone index created and populated
- [ ] Google Places API enabled in GCP
- [ ] Bubble.io API key configured
- [ ] `SECRET_KEY` replaced with a fresh generated key
- [ ] `DEBUG=False` in production
- [ ] `CORS_ALLOWED_ORIGINS` restricted to frontend domain
- [ ] `FRONTEND_URL` set to the real frontend URL (with `?sid={}` placeholder)
- [ ] `BACKEND_URL` set to the real backend URL

---

## 16. Getting Help

For detailed architecture questions, refer to the technical docs in `docs/`. For anything not covered there, the codebase is well-organized — start from:

- Backend: `src/ai/agents/` (agent logic), `src/ai/graphs/` (LangGraph DAGs), `src/ai/views/` (API endpoints)
- Frontend: `src/services/chatService.js` (API calls), `src/components/tabs/ChatWindow.jsx` (main UI), `src/auth/AuthProvider.jsx` (auth flow)
