# Backend Architecture & Flow Documentation

> Branch: `dev/backend` / `dev/backend-change-1-disable-token`  
> Stack: Django 5.2.6, Python 3.12.3, LangGraph, OpenAI GPT-4o  
> Last updated: 2026-05-13

---

## 1. Project Overview

**Project:** AI Bot for The Entrepreneur Lab — Virtual Co-Founder  
**Entry Point:** Uvicorn ASGI server (`src/run.py`)  
**Type:** Async REST API + WebSocket real-time agent tracking  
**Domain:** Entrepreneurship coaching via multi-agent LangGraph pipeline

---

## 2. Technology Stack & Dependencies

### Python Packages (requirements.txt)

| Package | Version | Role |
|---------|---------|------|
| Django | 5.2.6 | Web framework |
| djangorestframework | 3.16.1 | REST API |
| channels | 4.3.1 | WebSocket support |
| daphne | 4.2.1 | ASGI server |
| adrf | 0.1.9 | Async Django REST Framework |
| langchain | 0.3.27 | LLM orchestration |
| langgraph | 0.6.7 | Agent DAG framework |
| langchain-openai | 0.3.33 | OpenAI integration |
| langgraph-checkpoint-postgres | 2.0.23 | Graph state persistence |
| psycopg2-binary | 2.9.10 | PostgreSQL driver |
| psycopg_pool | 3.2.6 | Async PostgreSQL connection pool |
| django-cors-headers | 4.9.0 | CORS handling |
| uvicorn[standard] | 0.35.0 | ASGI server |
| redis | 6.4.0 | Sync Redis client |
| channels-redis | 4.3.0 | WebSocket channel layer |
| django-redis | 6.0.0 | Django cache via Redis |
| djangorestframework-simplejwt | 5.5.1 | JWT authentication |
| colorlog | 6.9.0 | Colored console logging |
| aiofiles | 25.1.0 | Async file I/O |
| aiohttp | 3.13.0 | Async HTTP client |
| django-ratelimit | 4.1.0 | Rate limiting middleware |
| pinecone | 7.3.0 | Vector DB for RAG |
| json_repair | 0.52.0 | Malformed JSON repair |
| duckduckgo_search | 8.1.1 | Web search tool |
| langchain-community | 0.3.31 | LangChain community tools |
| python-dotenv | 1.1.1 | Environment variable loading |

### External Services

| Service | Purpose |
|---------|---------|
| OpenAI GPT-4o | Chat reasoning, routing, structured output |
| OpenAI DALL-E 3 | Logo/image generation |
| OpenAI text-embedding-3-large | Vector embeddings for RAG |
| Pinecone | Vector database (RAG knowledge retrieval) |
| Google Places API | Business/professional search |
| PostgreSQL | Primary DB + LangGraph checkpoint storage |
| Redis | Pub/Sub (WebSocket) + Django cache (sessions) |
| Bubble.io | User management / external auth integration |

---

## 3. Directory Structure

```
src/
├── backend/                          # Django project config
│   ├── settings.py                   # Django settings + all API keys
│   ├── urls.py                       # Root URL routing
│   ├── asgi.py                       # ASGI application + protocol router
│   ├── wsgi.py                       # WSGI (not used - ASGI only)
│   └── lg.py                         # LangGraph lifespan middleware
│
├── ai/                               # Main AI agent Django app
│   ├── models.py                     # AgentChatIDModel, TokenUsage
│   ├── urls.py                       # AI endpoint URL patterns
│   ├── views/
│   │   ├── agent.py                  # POST /api/chat/agent/ (freeform)
│   │   ├── structured_agent.py       # POST /api/chat/structured-agent/ (7-step)
│   │   ├── chat_session.py           # Chat history + new chat management
│   │   └── template.py               # Template file download endpoint
│   ├── agents/
│   │   ├── enterpreneur_agent.py     # Freeform agent orchestrator
│   │   └── entrepreneur_structure_agent.py # 7-step structured agent
│   ├── graphs/
│   │   ├── enterpreneur_graph.py     # LangGraph DAG (freeform: router → agents)
│   │   └── enterpreneur_structured_graph.py # 7-step LangGraph DAG
│   ├── llm/
│   │   └── openai.py                 # LLM init, tracked model wrapper, tool setup
│   ├── prompts/
│   │   ├── entrepreneur_router_prompt.py    # Routing decision prompt
│   │   ├── entrepreneur_roadmap_prompt.py   # Roadmap generation prompt
│   │   ├── entrepreneur_ideation_prompt.py  # Brainstorming/ideation prompt
│   │   ├── enterpreneur_overview_agent.py   # Response improvement prompt
│   │   └── steps/
│   │       ├── step_1_prompt.py             # Foundation & Personal Finance
│   │       ├── step_2_prompt.py             # Business Idea Validation
│   │       ├── step_3_prompt.py             # Legal Compliance
│   │       ├── step_4_prompt.py             # MVP Planning
│   │       ├── step_5_prompt.py             # Business Setup & Branding
│   │       ├── step_6_prompt.py             # Launch Strategy
│   │       ├── step_7_prompt.py             # Operations & Growth
│   │       └── enrich_with_resources_prompt.py  # Resource enrichment
│   ├── tools/
│   │   ├── enterpreneur_search.py    # Bubble API: freelancers, entrepreneurs
│   │   ├── google_place_search.py    # Google Places search
│   │   ├── web_search.py             # Market research (DuckDuckGo + scraping)
│   │   ├── image_generation.py       # DALL-E 3 image generation
│   │   ├── pinecone.py               # Pinecone RAG query
│   │   └── common.py                 # Shared tool utilities
│   ├── consumers/
│   │   └── agent_state/
│   │       ├── sync.py               # Sync WebSocket consumer (Redis pub/sub)
│   │       └── async.py              # Async WebSocket consumer (legacy/unused)
│   ├── routing.py                    # WebSocket URL patterns
│   ├── state.py                      # LangGraph TypedDict state schemas
│   ├── serializers/
│   │   └── agent.py                  # DRF serializers for request validation
│   ├── tokens.py                     # In-memory token usage counter
│   ├── publisher.py                  # Redis pub/sub event publishing
│   ├── redis.py                      # Redis client initialization
│   ├── admin.py                      # Django admin registration
│   └── migrations/                   # Django DB migrations
│
├── bubbleio/                         # Bubble.io integration Django app
│   ├── models.py                     # BubbleUserModel (custom user)
│   ├── urls.py                       # /api/bubble/auth/, /api/bubble/refresh/
│   ├── views.py                      # BubbleDataView, BubbleRefreshTokenView
│   ├── serializers.py                # Request validation
│   └── migrations/
│
├── services/
│   ├── clients.py                    # OpenAI + Pinecone client initialization
│   ├── pinecone.py                   # Pinecone query & upsert wrappers
│   ├── google/
│   │   └── place.py                  # Google Places API client
│   ├── langgraph/
│   │   └── db.py                     # AsyncPostgresSaver factory
│   ├── template_workbook.py          # Template YAML loader
│   └── template.yaml                 # Step templates & resource definitions
│
├── utils/
│   ├── base64.py                     # Encode/decode/validate SID tokens
│   ├── exceptions.py                 # SIDTimeOutException
│   ├── json.py                       # JSON repair wrapper
│   ├── messsage.py                   # LangGraph message extractor
│   └── executor.py                   # Empty (legacy placeholder)
│
├── graph_compiler.py                 # Pre-compiles LangGraph DAGs at startup
├── manage.py                         # Django management CLI
├── run.py                            # Uvicorn entry point
├── run_unicorn.py                    # Duplicate of run.py (legacy)
│
└── media/
    └── templates/
        ├── step-1/                   # Excel workbooks for Step 1
        ├── step-2/                   # Excel workbooks for Step 2
        ├── ...
        └── step-7/                   # Excel workbooks for Step 7

scripts/
├── fetch_freelancers.py              # Batch import freelancers from Bubble
├── fetch_user.py                     # User data retrieval script
└── generate_data_embedding.py        # Generate + upsert Pinecone embeddings
```

---

## 4. Database Schema

### PostgreSQL Models

#### `bubbleio_bubbleusermodel` — Custom User Authentication

```python
class BubbleUserModel(AbstractBaseUser):
    bubble_user_id    = CharField(unique=True)       # Bubble.io user ID
    bubble_user_email = EmailField(unique=True)      # User email
    is_staff          = BooleanField(default=False)
    is_active         = BooleanField(default=True)
    date_joined       = DateTimeField(auto_now_add=True)
    # Inherited: password, last_login
```

#### `ai_agentchatidmodel` — Chat Session Management

```python
class AgentChatIDModel(models.Model):
    bubble_user = ForeignKey(BubbleUserModel, on_delete=SET_NULL, null=True)
    chat_id     = CharField(unique=True)   # UUID v4
    chat_name   = CharField(max_length=60, default="New Chat")
    deleted     = BooleanField(default=False)
    created_at  = DateTimeField(auto_now_add=True)
    updated_at  = DateTimeField(auto_now=True)
```

#### `ai_tokenusage` — Token Budget Tracking

```python
class TokenUsage(models.Model):
    bubble_user = ForeignKey(BubbleUserModel, on_delete=SET_NULL, null=True)
    token_count = IntegerField(default=60000)  # Allocated token budget
    token_used  = IntegerField(default=0)      # Consumed tokens (cumulative)
```

### LangGraph Checkpoint Tables (auto-created by `AsyncPostgresSaver.setup()`)

| Table | Purpose |
|-------|---------|
| `langgraph_checkpoint` | Serialized state snapshot at each node |
| `langgraph_checkpoint_blobs` | Large binary data in state |
| `langgraph_writes` | State mutations per node execution |

These tables are keyed by `thread_id` (= `chat_id`) allowing full conversation replay and continuation.

---

## 5. Authentication & Authorization

### Full JWT Flow via Bubble.io SSO

#### Step 1 — SID Token Generation (`POST /api/bubble/auth/`)

Bubble.io calls this when a user logs in to their platform:

```
Bubble.io → POST /api/bubble/auth/?user_id=<id>&email=<email>
```

Backend processing:
1. Generate UUID `sid_key`
2. Build payload: `{ bubble_user_id, bubble_user_email, expire_at: now + 5min }`
3. Base64-encode payload → `sid_value`
4. Store in Redis: `cache.set(sid_key, sid_value, timeout=72000)` (20 hours TTL)
5. Get-or-create `BubbleUserModel` record
6. Return: `{ "redirect_url": "https://agent.thentrepreneurlab.com?sid={sid_key}" }`

#### Step 2 — JWT Token Exchange (`GET /api/bubble/auth/`)

Frontend receives the redirect URL, extracts `sid`, calls:

```
Frontend → GET /api/bubble/auth/?sid={sid_key}
```

Backend processing:
1. Retrieve `sid_value = cache.get(sid_key)` from Redis
2. Decode base64 → extract payload
3. Validate `expire_at` timestamp (raises `SIDTimeOutException` if expired)
4. Fetch `BubbleUserModel` by `bubble_user_id` + `bubble_user_email`
5. Generate JWT: `refresh_token = RefreshToken.for_user(user)`
6. Return: `{ "messsage": { "refresh": "...", "access": "..." } }`
   - Note: Typo "messsage" (3 s's) is in the actual response field

#### Step 3 — Token Refresh (`POST /api/bubble/refresh/`)

```
Frontend → POST /api/bubble/refresh/ with body: { "refresh": "..." }
Backend  → Returns { "message": { "access": "..." } }
```

Uses `djangorestframework-simplejwt` internals.

### Permission Classes

All AI/chat endpoints use `IsAuthenticated` (JWT Bearer token required).  
Bubble auth endpoints: open (no auth).

### WebSocket Authentication

Django Channels `AuthMiddlewareStack` wraps the WebSocket router, validating JWT on connection.

---

## 6. API Endpoints

### AI / Chat Endpoints

```
POST /api/chat/agent/?chat-id=<uuid>
  Body:     { "user_input": "string" }
  Response: { "message": { ...freeform agent response... } }
  Auth:     JWT required
  Notes:    Checks token budget. Returns 402 if exhausted.

POST /api/chat/structured-agent/?chat-id=<uuid>
  Body:     { "user_input": "string", "step": "entrepreneur_step_1" }
  Response: { "message": { "step": "...", "response": "..." } }
  Auth:     JWT required
  Notes:    Routes to one of 7 step-specific nodes.

GET /api/chat/token/
  Response: { "total_token": 60000, "token_used": 1234, "skip_token_usage": false }
  Auth:     JWT required

GET /api/chat/new-chat/
  Response: { "message": { "chat_id": "uuid", "chat_name": "New Chat" } }
  Auth:     JWT required
  Notes:    Creates AgentChatIDModel record.

GET /api/chat/history/
  Response: { "message": [{ "detail": { "chat_id", "chat_name" } }, ...] }
  Auth:     JWT required
  Notes:    Returns all non-deleted chats for the authenticated user.

GET /api/chat/history/?chat-id=<uuid>
  Response: { "message": [{ "user": "..." }, { "agent": {...} }, ...] }
  Auth:     JWT required
  Notes:    Fetches from LangGraph checkpoint state (PostgreSQL).

GET /api/chat/template/<filename>/
  Response: Binary stream (Excel .xlsx file)
  Auth:     JWT required
  Notes:    Streams file from /src/media/templates/.
```

### Bubble.io Integration Endpoints

```
POST /api/bubble/auth/?user_id=<id>&email=<email>
  Response: { "redirect_url": "https://agent.thentrepreneurlab.com?sid=..." }
  Auth:     None

GET /api/bubble/auth/?sid=<sid_key>
  Response: { "messsage": { "refresh": "...", "access": "..." } }
  Auth:     None
  Notes:    "messsage" typo is intentional in actual code.

POST /api/bubble/refresh/
  Body:     { "refresh": "..." }
  Response: { "message": { "access": "..." } }
  Auth:     None
```

### WebSocket Endpoints

```
WS /ws/static/<session_id>/
  Consumer: SyncRouteTrackerConsumerStatic
  Purpose:  Real-time agent step updates for a fixed session ID
  Protocol: JSON messages pushed from Redis pub/sub
  Channel:  route_updates:<session_id>

WS /ws/dynamic/
  Consumer: SyncRouteTrackerConsumerDynamic
  Purpose:  Client specifies session ID dynamically after connect
  Protocol: First message sets session_id; subsequent messages are updates
```

---

## 7. Core AI Agent Architecture

### High-Level System Design

```
User HTTP Request
      │
      ▼
  AgentView / StructuredAgentView
      │
      ├── Validate JWT, token budget, chat_id
      │
      ▼
  Agent Function (async)
      │
      ▼
  LangGraph DAG  ◄──── PostgreSQL Checkpoints (per node)
      │                (state persists across requests)
      │
      ├── user_query_node
      │
      ├── entrepreneur_router_agent
      │        │
      │   [conditional branch]
      │        │
      │   ┌────┴────────────────────────┐
      │   │                             │
      ▼   ▼                             ▼
  ideation_agent                  roadmap_agent
      │                                │
      ▼                                ▼
  overview_agent              enrich_with_resources
      │                                │
      └──────────┬──────────────────────┘
                 │
            image_generation_agent
                 │
                 ▼
            Final JSON Response
                 │
                 ▼
        HTTP Response to Client

Real-Time Side Channel:
  Each node publishes events → Redis pub/sub → WebSocket → Client
```

### Freeform Agent (`entrepreneur_agent()`)

**File:** `src/ai/agents/enterpreneur_agent.py`

```python
async def entrepreneur_agent(user_input: str, chat_id: str):
    message_state = {
        "messages": [],
        "user_query": user_input,
        "chat_id": chat_id
    }

    async for mode, chunk in graphs.entrepreneur_graph.astream(
        message_state,
        {"configurable": {"thread_id": chat_id}},
        stream_mode=["updates"]
    ):
        # Extract response from the node that fired last
        if "entrepreneur_overview_agent" in chunk:
            response = chunk["entrepreneur_overview_agent"]["messages"][0]["content"]
        elif "entrepreneur_roadmap_agent" in chunk:
            response = chunk["..."]["messages"][0]["content"]
        # ... etc.

    # Clean LLM markdown artifacts and parse JSON
    response = response.replace("```json", "").replace("```", "")
    return json.loads(response)
```

---

## 8. LangGraph DAG: Freeform Agent (`enterpreneur_graph.py`)

### Nodes

| Node | Description |
|------|-------------|
| `user_query_node` | Adds user's message to state (START) |
| `entrepreneur_router_agent` | Classifies intent → chooses downstream node |
| `entrepneur_conditional_node` | Edge function reading router output |
| `entrepreneur_ideation_agent` | React agent: brainstorming + all tools |
| `entrepreneur_roadmap_agent` | Structured roadmap generation |
| `enrich_roadmap_with_resources` | Per-step Pinecone query + resource append |
| `entrepreneur_overview_agent` | Polish / improve final response |
| `image_generation_agent` | DALL-E 3 logo generation |

### Edge Graph

```
START
  └─► user_query_node
          └─► entrepreneur_router_agent
                  └─► [conditional]
                          ├─► entrepreneur_ideation_agent
                          │         └─► entrepreneur_overview_agent ─► END
                          ├─► entrepreneur_roadmap_agent
                          │         └─► enrich_roadmap_with_resources ─► END
                          └─► image_generation_agent ─► END
```

### Router Output Schema

```json
{
  "intent": "user wants a startup roadmap",
  "recommended_agent": "entrepreneur_roadmap_agent",
  "recommended_node": "entrepreneur_roadmap_agent",
  "reasoning": "User explicitly asked for a plan",
  "next_action": "Generate 7-step roadmap"
}
```

---

## 9. LangGraph DAG: Structured 7-Step Agent (`enterpreneur_structured_graph.py`)

### Nodes

| Node | Step |
|------|------|
| `user_query_node` | Adds user message to state |
| `entrepreneur_conditional_node` | Routes based on `step` parameter |
| `entrepreneur_step_1` | Foundation & Personal Finance |
| `entrepreneur_step_2` | Business Idea Validation |
| `entrepreneur_step_3` | Legal Compliance & Financial Modeling |
| `entrepreneur_step_4` | MVP Planning |
| `entrepreneur_step_5` | Business Setup & Branding |
| `entrepreneur_step_6` | Launch Strategy |
| `entrepreneur_step_7` | Operations & Growth Management |

### Edge Graph

```
START
  └─► user_query_node
          └─► entrepreneur_conditional_node
                  ├─► entrepreneur_step_1 ─► END
                  ├─► entrepreneur_step_2 ─► END
                  ├─► entrepreneur_step_3 ─► END
                  ├─► entrepreneur_step_4 ─► END
                  ├─► entrepreneur_step_5 ─► END
                  ├─► entrepreneur_step_6 ─► END
                  └─► entrepreneur_step_7 ─► END
```

Each step node:
1. Loads the step-specific system prompt (objectives, outcomes, templates)
2. Prepends conversation history from LangGraph checkpoint
3. Calls `ideation_llm_chat` (React agent with all tools)
4. Returns structured response with guidance for that step

---

## 10. LangChain Tools

### Tool 1: Bubble Entrepreneur Search

```python
@tool
async def get_bubble_entreprenurs():
    """Fetch list of entrepreneurs from The Entrepreneur Lab internal database"""
    # GET /entrepreneur from Bubble API
    # Returns: Array of entrepreneur profiles
```

### Tool 2: Bubble Freelancer Search

```python
@tool
async def get_bubble_freelancers_v2(email: Optional[str] = None):
    """Search internal database of freelancers/professionals"""
    # GET /freelancer from Bubble API (optional email filter)
    # Falls back to external search if no matches
```

### Tool 3: Market Research (DuckDuckGo)

```python
@tool
async def market_research_tool(query: str):
    """Real-time market analysis using DuckDuckGo + HTML scraping"""
    # 1. Generate 3 search queries (market size, trends, competitors)
    # 2. Execute DuckDuckGo searches
    # 3. Fetch top pages (max 1/category, 400 chars/page, early stop at 3 results)
    # Returns: { "query": str, "categories": {...}, "total_results": int }
```

Performance notes: Intentionally limited (3 queries max, 1 page/category, 400 char limit) to reduce latency and cost.

### Tool 4: Google Places Search

```python
@tool
async def search_place_and_rating_v2(place: str):
    """Search for businesses/professionals using Google Places API"""
    # 1. POST /places/places:searchText
    # 2. GET /places/{place_id} for details
    # Returns: { displayName, formattedAddress, rating, userRatingCount, reviews, websiteUri }
```

### Tool 5: Pinecone RAG Query

```python
@tool
async def query_pinecone_tool(question: str):
    """Retrieve resources from vector DB"""
    # 1. Embed with text-embedding-3-large
    # 2. Query Pinecone (top_k=5)
    # Returns: [{ "text": "..." }, ...]
```

### Tool 6: Image Generation (DALL-E 3)

```python
async def image_gen(prompt: str):
    """Generate logo/image using DALL-E 3"""
    # POST https://api.openai.com/v1/images/generations
    # Returns: { "type": "image_response", "logo": "<url>" }
```

---

## 11. LLM Configuration & Token Tracking

### LLM Setup (`src/ai/llm/openai.py`)

```python
# Standard chat model
openai_llm_chat = init_chat_model(f"openai:{OPENAI_CHAT_MODEL}", stream_usage=True)

# Token-tracking wrapper
class TrackedModel(ChatOpenAI):
    async def ainvoke(self, input, **kwargs):
        result = await super().ainvoke(input, **kwargs)
        tokens = result.response_metadata["token_usage"]["total_tokens"]
        await total_tokens.add(tokens)  # Global in-memory counter
        return result

tracked_llm = TrackedModel(model=OPENAI_CHAT_MODEL, ...)

# Ideation agent: React agent with all tools
ideation_llm_chat = create_react_agent(
    tracked_llm,
    tools=[
        get_bubble_freelancers_v2,
        market_research_tool,
        search_place_and_rating_v2,
        query_pinecone_tool,
        get_bubble_entreprenurs,
    ],
)
```

### In-Memory Token Counter (`src/ai/tokens.py`)

```python
class TokenCounter:
    def __init__(self):
        self._count = 0

    async def add(self, value): self._count += value
    async def get(self): return self._count
    async def reset(self): self._count = 0

total_tokens = TokenCounter()  # Module-level singleton
```

After each request completes: `token.token_used += await total_tokens.get()`, then `await token.asave()`.

---

## 12. LLM Prompts

### Router Prompt

Decides between 3 downstream agents:
- `entrepreneur_ideation_agent` — brainstorming, open-ended questions, validation
- `entrepreneur_roadmap_agent` — structured multi-step plan
- `image_generation_agent` — logo or visual creation

Output must be strict JSON (using `json_repair` for safety):
```json
{
  "intent": "...",
  "recommended_agent": "...",
  "recommended_node": "...",
  "reasoning": "...",
  "next_action": "..."
}
```

### Roadmap Prompt

Generates the full entrepreneurial response:
```json
{
  "type": "entrepreneurial_response",
  "data": {
    "idea_summary": {
      "title": "...",
      "one_liner": "...",
      "strengths": ["..."],
      "risks": ["..."]
    },
    "roadmap": [
      {
        "step": 1,
        "title": "...",
        "description": "...",
        "resources": ["..."]
      }
    ],
    "execution_support": {
      "automated_content": ["..."],
      "design_branding": {
        "name_ideas": ["..."],
        "logo_concepts": ["..."]
      }
    },
    "mentorship": { "suggested_experts": ["..."] },
    "events": ["..."],
    "funding": ["..."]
  }
}
```

### Ideation Prompt

Brainstorming guidance, must return:
```json
{ "type": "general_response", "data": "Markdown or plain text response" }
```

### Step Prompts (1–7)

Each step prompt provides:
- **Objectives** — what this step achieves
- **Expected outcomes** — deliverables
- **Templates** — references to Excel files from `template.yaml`
- **Resources** — external reading, tools, platforms
- **Actions** — concrete steps to take

Example Step 1 focus: Entrepreneurial mindset, personal finance readiness, skill assessment.

### Enrich Resources Prompt

For each roadmap step after generation:
1. Queries Pinecone with step title/description as query
2. Appends relevant resources: `[{ "title": "...", "url": "..." }]`

---

## 13. State Schemas

### Freeform State (`src/ai/state.py`)

```python
class State(TypedDict):
    messages:        Annotated[list, add_messages]  # Full conversation (user + AI)
    user_query:      str                            # Raw user input
    router_response: dict                           # Router agent classification
    final_response:  str                            # Last node's output
    chat_id:         str                            # LangGraph thread_id
```

### Structured State (`src/ai/state.py`)

```python
class StateStructured(TypedDict):
    messages:       Annotated[list, add_messages]
    user_query:     str
    step:           str                             # "entrepreneur_step_1" ... "7"
    final_response: str
    chat_id:        str
```

---

## 14. State Persistence & Checkpointing

### AsyncPostgresSaver (`src/services/langgraph/db.py`)

```python
# Created at startup via LangGraph lifespan:
pool = AsyncConnectionPool(f"postgresql://{user}:{pwd}@{host}:{port}/{db}")
Saver.saver = AsyncPostgresSaver(pool)
await Saver.saver.setup()  # Creates langgraph_* tables

# Used in graph compilation:
graph.compile(checkpointer=Saver.saver)
```

Every time a node executes, LangGraph serializes the full state and saves a checkpoint to PostgreSQL keyed by `thread_id` (= `chat_id`). This enables:
- Resuming conversations mid-flow after server restart
- Full history replay via `graph.get_state()`
- Consistent multi-turn chat context

---

## 15. Data Flows for Major Features

### Flow 1: Freeform Chat Request

```
Client
  │  POST /api/chat/agent/?chat-id=<uuid>
  │  Body: { "user_input": "Create a tech startup idea" }
  ▼
AgentView.post()
  ├── Validate JWT
  ├── Get TokenUsage record
  ├── Check token budget (skip if email in TOKEN_DISABLE_ACCOUNT)
  ├── Validate chat_id in AgentChatIDModel
  └── Call entrepreneur_agent(user_input, chat_id)
          │
          ▼
    entrepreneur_graph.astream()   [PostgreSQL checkpoint per node]
          │
          ├── user_query_node:
          │     Add user message to state["messages"]
          │
          ├── entrepreneur_router_agent:
          │     Build prompt: system_prompt + message history
          │     openai_llm_chat.ainvoke() → GPT-4o
          │     Parse JSON → state["router_response"]
          │     Publish WebSocket event: "Router analyzing..."
          │
          ├── [conditional edge: reads recommended_node]
          │
          ├── [Branch A] entrepreneur_roadmap_agent:
          │     Build roadmap prompt + history
          │     openai_llm_chat.ainvoke()
          │     Return structured roadmap JSON
          │     → enrich_roadmap_with_resources:
          │           For each step: query_pinecone_tool(step.title)
          │           Append resources to each step
          │     Publish WebSocket events throughout
          │
          ├── [Branch B] entrepreneur_ideation_agent (React):
          │     ideation_llm_chat.ainvoke()
          │     LLM auto-selects tools: market_research, places, pinecone, bubble
          │     Tools execute concurrently
          │     LLM formats final JSON response
          │     → entrepreneur_overview_agent:
          │           Improve clarity, preserve structure
          │
          └── [Branch C] image_generation_agent:
                image_gen(user_input)
                DALL-E 3 API call
                Return { "type": "image_response", "logo": "<url>" }
          │
          ▼
    Extract final response from last node's chunk
    json_repair → json.loads → dict
          │
          ▼
AgentView
  ├── Update token.token_used += await total_tokens.get()
  └── Return: { "message": <dict> }
```

### Flow 2: Structured 7-Step Chat

```
Client
  │  POST /api/chat/structured-agent/?chat-id=<uuid>
  │  Body: { "user_input": "Help me with legal setup", "step": "entrepreneur_step_3" }
  ▼
StructuredAgentView.post()
  └── Call entrepreneur_structured_agent(user_input, chat_id, step)
          │
          ▼
    entrepreneur_structured_graph.astream()
          │
          ├── user_query_node
          ├── entrepreneur_conditional_node → routes to step_3
          └── entrepreneur_step_3:
                Load step_3_prompt (objectives, templates, resources)
                Get conversation history from checkpoint
                ideation_llm_chat.ainvoke(step_prompt + history + user_input)
                React agent may call tools as needed
                Return step guidance response
          │
          ▼
    { "message": { "step": "entrepreneur_step_3", "response": "..." } }
```

### Flow 3: WebSocket Real-Time Agent Tracking

```
Client connects: WS /ws/static/<chat_id>/
  │
  ▼
SyncRouteTrackerConsumerStatic.connect()
  ├── Accept WebSocket connection
  ├── Create Redis pubsub: redis_client.pubsub()
  ├── Subscribe to: route_updates:<chat_id>
  └── Start listen_to_redis() thread

  [Separate HTTP request starts graph execution]

Each node in graph calls publisher.log_route_event():
  │  Publishes: { "timestamp": "...", "agent": "router_agent", "action": "...", "details": "..." }
  │  To Redis channel: route_updates:<chat_id>
  ▼
listen_to_redis() receives message
  └── Forwards JSON to WebSocket client

Client receives real-time step updates:
  - "Router Agent: Analyzing user query..."
  - "Routing to: Roadmap Agent"
  - "Roadmap Agent: Building structured plan..."
  - "Enriching resources via Pinecone..."
  - "Done"
```

### Flow 4: Chat History Retrieval

```
Client: GET /api/chat/history/?chat-id=<uuid>
  ▼
AgentChatHistory.get()
  ├── Fetch checkpoint: Saver.saver.aget(config={"configurable": {"thread_id": chat_id}})
  ├── Extract state["messages"] from checkpoint
  └── Format: [{ "user": "...", "agent": {...} }, ...]
  │
  ▼
{ "message": [{ "user": "..." }, { "agent": {...} }, ...] }

Client: GET /api/chat/history/ (no chat-id)
  ├── AgentChatIDModel.objects.filter(bubble_user=request.user, deleted=False)
  └── Returns list of { chat_id, chat_name } metadata
```

### Flow 5: Bubble.io SSO

```
Bubble.io platform detects login
  │
  ▼
POST /api/bubble/auth/?user_id=<id>&email=<email>
  ├── Generate sid_key = UUID
  ├── Encode: { bubble_user_id, bubble_user_email, expire_at } → base64 → sid_value
  ├── cache.set(sid_key, sid_value, timeout=72000)
  ├── BubbleUserModel.get_or_create(bubble_user_id=id, bubble_user_email=email)
  └── Return: { "redirect_url": "https://agent.thentrepreneurlab.com?sid=<sid_key>" }
  │
  ▼
[Browser redirected to frontend with ?sid=...]
  │
  ▼
Frontend: GET /api/bubble/auth/?sid=<sid_key>
  ├── sid_value = cache.get(sid_key)
  ├── data = base64.decode(sid_value)
  ├── Validate data["expire_at"] < now → 400 if expired
  ├── Fetch BubbleUserModel
  ├── refresh_token = RefreshToken.for_user(user)
  └── Return: { "messsage": { "refresh": "...", "access": "..." } }
```

---

## 16. Redis Architecture

| Database | Client | Purpose |
|----------|--------|---------|
| Redis DB 1 | django-redis (sync) | Django cache — SID token storage (72000s TTL) |
| Redis DB 3 | redis-py (sync) | WebSocket pub/sub — route update events |
| Redis DB 4 | redis-py (async) | Async WebSocket pub/sub (alternative consumer) |

### Channel Naming

```python
f"route_updates:{chat_id}"  # One channel per active chat session
```

---

## 17. Middleware Stack

### HTTP Middleware (Django)

```
SecurityMiddleware
SessionMiddleware
CorsMiddleware (CORS_ALLOW_ALL_ORIGINS = True)
CommonMiddleware
CsrfViewMiddleware
AuthenticationMiddleware
MessageMiddleware
XFrameOptionsMiddleware
```

### ASGI Protocol Router (`backend/asgi.py`)

```python
ProtocolTypeRouter({
    "http":      django_application,
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    "lifespan":  LifespanMiddleware(django_application),
})
```

### Lifespan Middleware (`backend/lg.py`)

```
Startup:
  1. initialize_checkpointer()
     → Create AsyncConnectionPool (PostgreSQL)
     → Initialize AsyncPostgresSaver
     → Run .setup() (create langgraph_* tables)
  2. compile_graphs()
     → Build entrepreneur_graph DAG
     → Build entrepreneur_structured_graph DAG
     → Compile both with checkpointer

Shutdown:
  1. await Saver.pool.close()
```

---

## 18. Server Startup Sequence

```
python src/run.py
  │
  ▼
uvicorn.run("backend.asgi:application", host="localhost", port=9018, lifespan="on")
  │
  ▼
ASGI app loads → LifespanMiddleware fires startup event
  ├── AsyncConnectionPool → PostgreSQL
  ├── AsyncPostgresSaver.setup() → create langgraph tables
  ├── Compile entrepreneur_graph (with checkpoint persistence)
  └── Compile entrepreneur_structured_graph (with checkpoint persistence)
  │
  ▼
Server ready
  ├── HTTP → Django views
  └── WebSocket → Django Channels consumers (via Redis channel layer)
```

---

## 19. Logging Configuration

```python
# Log directory: src/logs/
Handlers:
  bubbleio_app_file  → logs/bubbleio_app.log  (RotatingFileHandler, 10MB)
  ai_app_file        → logs/ai_app.log         (RotatingFileHandler, 10MB)
  console            → ColorLog (color-coded by level)

Loggers:
  "bubbleio" → DEBUG+, console + bubbleio_app_file
  "ai"       → DEBUG+, console + ai_app_file
```

Console format example:
```
⟦ ai INFO 2025-05-13 12:34:56 enterpreneur_agent.py:45 ⟧ User query: Create a startup
⟦ ai DEBUG ... graphs.py:89 ⟧ Router response: {"recommended_node": "entrepreneur_roadmap_agent"}
```

---

## 20. Error Handling Patterns

### HTTP Error Responses

| Scenario | Status | Response |
|----------|--------|---------|
| Token budget exhausted | 402 | `{"notifiy": "Token consumed, please buy the tokens"}` — note typo |
| Invalid request body | 400 | `{"error": serializer.errors}` |
| SID expired | 400 | `{"error": "Autentication session expired..."}` — note typo |
| Server/LLM error | 500 | `{"error": str(e)}` |

### JSON Repair

LLM output is not always valid JSON:
```python
from json_repair import repair_json

raw = llm_response.replace("```json", "").replace("```", "")
repaired = repair_json(raw)
data = json.loads(repaired)
```

---

## 21. Environment Variables

```bash
# PostgreSQL
DBNAME=<db_name>
DBHOST=<db_host>
DBPORT=5432
DBUSER=<db_user>
DBPASSWORD=<db_password>

# OpenAI
OPENAI_API_KEY=<api_key>
OPENAI_CHAT_MODEL=gpt-4o

# Bubble.io
BUBBLE_API_KEY=<api_key>
BUBBLE_BASE_URL=https://api.bubble.io
BUBBLE_PASSWORD_DEFAULT=<internal_default_password>

# Pinecone
PINECONE_API_KEY=<api_key>
PINECONE_INDEX_NAME=<index_name>

# Google Places
GOOGLE_API_KEY=<api_key>

# Application
FRONTEND_URL=https://agent.thentrepreneurlab.com?sid={}
BACKEND_URL=https://backend.thentrepreneurlab.com
HOST=localhost
PORT=9018

# Token exemptions (comma-separated emails)
TOKEN_DISABLE_ACCOUNT=testuser@example.com,admin@example.com
```

---

## 22. Branch Differences: `dev/backend` vs `dev/backend-change-1-disable-token`

| Change | Description |
|--------|-------------|
| `.env.example` | Added — example environment configuration file |
| `src/ai/views/agent.py` | Added token skip logic: checks if user email in `TOKEN_DISABLE_ACCOUNT` |
| `src/ai/views/structured_agent.py` | Same token skip logic |
| `src/backend/settings.py` | Added `TOKEN_DISABLE_ACCOUNT = os.getenv("TOKEN_DISABLE_ACCOUNT").split(",")` |

Token skip logic:
```python
skip_token_usage = request.user.bubble_user_email in settings.TOKEN_DISABLE_ACCOUNT
if not skip_token_usage:
    if not await token.token_available():
        return Response({"notifiy": "Token consumed..."}, status=402)
```

**Purpose:** Allow specific accounts (testers, admins) to bypass token budget checks.

---

## 23. Known Issues & Legacy Code

### Typos in Production Code

| Location | Typo | Correct |
|----------|------|---------|
| Bubble auth response | `"messsage"` | `"message"` |
| Bubble auth error | `"Autentication"` | `"Authentication"` |
| Token 402 response | `"notifiy"` | `"notify"` |

### Legacy Files

| File | Status |
|------|--------|
| `src/ai/consumers/agent_state/async.py` | Async Redis consumer — may be unused (sync version is active) |
| `src/utils/executor.py` | Empty file — placeholder/unused |
| `src/run_unicorn.py` | Duplicate of `run.py` — legacy |
| Old prompt versions in git history | Cofounder_ideation_agent_prompt_v2, v3 |

### Commented-Out Code

- Alternative prompt versions in graph files
- Old logging configuration in `settings.py`
- Debug print statements in various nodes

---

## 24. Template System

Excel workbook templates stored at `src/media/templates/step-{N}/`:

| Step | Focus Area |
|------|-----------|
| Step 1 | Entrepreneurial Readiness Assessment, Personal Finance Contract |
| Step 2 | Business Idea Evaluation, Market Validation |
| Step 3 | Legal Compliance Checklist, Financial Modeling |
| Step 4 | MVP Feature Prioritization, Technical Roadmap |
| Step 5 | Brand Identity, Business Registration Checklist |
| Step 6 | Launch Checklist, Marketing Plan |
| Step 7 | Operations SOP, KPI Dashboard |

Downloaded by clients via `GET /api/chat/template/<filename>/` (streams binary).

Template metadata loaded from `src/services/template.yaml` and injected into step prompts at LLM call time.

---

## 25. Technology Decision Summary

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Web Framework | Django + DRF | Batteries included, mature async (ASGI) support |
| Agent Framework | LangGraph | DAG-based state machine, per-node checkpointing |
| LLM | OpenAI GPT-4o | Best structured output, function calling, tool use |
| Vector DB | Pinecone | Managed, no ops overhead |
| State Persistence | PostgreSQL + LangGraph | Resumable conversations, full history replay |
| Session Cache | Redis (DB 1) | Fast TTL-based SID token store |
| Real-Time | WebSocket + Redis Pub/Sub | Push progress events during long agent runs |
| Auth | Bubble.io SSO → JWT | External identity provider, JWT for API access |
| ASGI Runtime | Uvicorn | Single-process async server, optimal for I/O-heavy LLM workloads |
