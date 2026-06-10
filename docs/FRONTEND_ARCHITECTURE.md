# Frontend Architecture & Flow Documentation

> Branch: `dev/frontend` / `dev/frontend-change-1-disable-token`  
> Stack: React 19, Vite 7, Tailwind CSS 4, Material UI 7  
> Last updated: 2026-05-13

---

## 1. Project Overview

**Project Name:** brunda-frontend (package.json v0.0.0)  
**Type:** AI Co-founder Chat Application  
**Platform:** React 19 SPA  
**Deployment:** Vercel (via `vercel.json` SPA rewrites)  
**Domain:** https://agent.thentrepreneurlab.com (frontend)

---

## 2. Technology Stack

### Core

| Package | Version | Role |
|---------|---------|------|
| React | 19.2.0 | UI framework |
| React DOM | 19.2.0 | DOM rendering |
| Vite | 7.1.7 | Build tool / dev server |
| React Router DOM | 7.9.2 | Client-side routing |

### UI / Styling

| Package | Version | Role |
|---------|---------|------|
| Tailwind CSS | 4.1.13 | Utility-first CSS |
| @tailwindcss/vite | 4.1.13 | Vite integration |
| @mui/material | 7.3.4 | Material Design components |
| @mui/icons-material | 7.3.4 | Material icons |
| @emotion/react | 11.14.0 | MUI styling engine |
| @emotion/styled | 11.14.1 | MUI styling engine |
| material-tailwind | 2.1.10 | MUI + Tailwind hybrid |
| lucide-react | 0.545.0 | Icon set |
| react-feather | 2.0.10 | Icon set |
| material-icons | 1.13.14 | Icon set |

### Content

| Package | Version | Role |
|---------|---------|------|
| react-markdown | 10.1.0 | Markdown rendering |
| remark-gfm | 4.0.1 | GitHub-Flavored Markdown |
| react-toastify | 11.0.5 | Toast notifications |

### Dev Tools

| Package | Version | Role |
|---------|---------|------|
| ESLint | 9.36.0 | Linting |
| @vitejs/plugin-react | 5.0.3 | React HMR |
| @types/react | 19.1.13 | TypeScript types |
| @types/react-dom | 19.1.9 | TypeScript types |

---

## 3. Project Structure

```
src/
├── main.jsx                              # App entry point
├── App.jsx                               # Root component + routing
├── index.css                             # Global styles (Tailwind + Inter font)
│
├── auth/
│   └── AuthProvider.jsx                  # Authentication context + initialization
│
├── services/
│   ├── authService.js                    # Auth logic: SID exchange, JWT refresh, authFetch
│   └── chatService.js                    # Chat API: send messages, load history, token stats
│
├── api/
│   └── chat.js                           # [LEGACY/UNUSED] Alternative chat API client
│
├── components/
│   ├── Navbar.jsx                        # Top navigation bar
│   ├── Sidebar.jsx                       # Left sidebar (16 menu items)
│   ├── EntrepreneurialResponse.jsx       # Structured response renderer
│   ├── ThinkingLoader.jsx                # Animated loading indicator
│   └── tabs/
│       └── ChatWindow.jsx                # Main chat interface (1043 lines)
│
├── pages/
│   └── Dashboard.jsx                     # [UNUSED] Dashboard page
│
└── utils/
    ├── tokenStorage.js                   # localStorage token read/write/clear
    └── responseParser.js                 # [LARGELY UNUSED] Response formatting
```

### Config Files

```
vite.config.js          # Vite config: React plugin, Tailwind plugin, allowed hosts
vercel.json             # Vercel: SPA rewrites (all routes → /index.html)
index.html              # HTML shell: title "Entrepreneurlab Agent", mounts #root
package.json            # Scripts: dev, build, lint, preview
```

---

## 4. Application Entry Point & Initialization

**`src/main.jsx`:**

```jsx
createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <AuthProvider>
      <App />
    </AuthProvider>
  </BrowserRouter>
)
```

Initialization sequence:
1. HTML loads, `index.html` bootstraps Vite
2. React mounts to `#root`
3. `BrowserRouter` provides routing context
4. `AuthProvider` runs `initializeAuth()` — see Authentication section
5. `App` renders layout + routes (blocked by auth loading overlay)

---

## 5. Routing Structure

**`src/App.jsx`:**

```jsx
<Routes>
  <Route path="/" element={<Navigate to="/ai-co-founder" replace />} />
  <Route path="/ai-assistant" element={<ChatWindow activeTab="ai-assistant" />} />
  <Route path="/ai-co-founder" element={<ChatWindow activeTab="ai-co-founder" />} />
</Routes>
```

### Route Behavior

| Route | Component | Behavior |
|-------|-----------|---------|
| `/` | — | Redirects to `/ai-co-founder` |
| `/ai-co-founder` | `ChatWindow` | Full AI chat interface; 7-step sidebar |
| `/ai-assistant` | `ChatWindow` | Disabled tab — shows "Chat only available in AI Co-founder" |

### Layout Wrapper

```
<App>
  ├── <Navbar />                    ← Top bar: logo, notifications, user
  ├── <div className="flex flex-1">
  │   ├── <Sidebar />               ← Left nav (16 items)
  │   └── <Routes />                ← Main content area
  └── <ToastContainer />            ← Bottom-right toast layer
```

---

## 6. Authentication Flow

**Files:** `src/auth/AuthProvider.jsx`, `src/services/authService.js`, `src/utils/tokenStorage.js`

### Auth Context Shape

```javascript
const AuthContext = createContext({
  token: null,       // JWT access token (string | null)
  loading: true,     // Whether auth is still initializing
  error: null,       // Error message (string | null)
  retry: () => {},   // Clears tokens and reloads page
});
```

### Initialization Flow (`AuthProvider.useEffect`)

```
App mounts
  │
  ▼
AuthProvider detects sid in URL:
  location.search + location.hash parsed for ?sid= or #sid=
  If found → tokenStorage.setSid(sid)
  │
  ▼
authService.initializeAuth()
  │
  ├── [Path A] SID present in storage:
  │     GET /api/bubble/auth/?sid={sid}
  │     Extract: { accessToken, refreshToken }
  │     tokenStorage.setTokens(accessToken, refreshToken, sid)
  │     Return: accessToken
  │
  ├── [Path B] No SID, but existing tokens in localStorage:
  │     tokenStorage.getAccessToken() + getRefreshToken() both exist?
  │     Return: existing accessToken
  │
  └── [Path C] No SID, no tokens:
        If VITE_EXTERNAL_DASHBOARD_URL set:
          window.location.href = VITE_EXTERNAL_DASHBOARD_URL
        Else:
          Throw error "No authentication available"
  │
  ▼
AuthProvider sets: token = accessToken, loading = false
  │
  ▼
App renders normally (loading overlay removed)
```

### Token Storage (localStorage keys)

| Key | Value |
|-----|-------|
| `access_token` | JWT access token |
| `refresh_token` | JWT refresh token |
| `session_id` | SID from Bubble.io redirect |

### Authenticated Fetch (`authService.authFetch`)

All API calls go through this wrapper:

```javascript
// 1. Add Authorization header
headers["Authorization"] = `Bearer ${accessToken}`;

// 2. Make request
response = await fetch(url, { headers, ...options });

// 3. On 401: attempt token refresh (up to 2 times)
if (response.status === 401) {
  authFetch._unauthorizedAttempts += 1;

  if (attempts >= 2) throw new Error("Unauthorized");

  if (!refreshToken) {
    // Re-auth via SID
    const { accessToken, refreshToken } = await authService.authenticateWithSid(sid);
  } else {
    // Refresh via refresh token
    const { accessToken, refreshToken } = await authService.refreshAccessToken(refreshToken);
    // POST /api/bubble/refresh/ → { access, refresh }
  }

  tokenStorage.setTokens(newAccess, newRefresh, sid);
  authFetch._unauthorizedAttempts = 0;
  response = await makeRequest(newToken);  // Retry original request
}
```

### Logout

```javascript
tokenStorage.clearTokens();  // Removes all 3 localStorage keys
window.location.reload();
```

---

## 7. State Management

**Approach:** React Context API (auth) + `useReducer` (chat) — no Redux or Zustand.

### Chat State (`ChatWindow` — `useReducer`)

```javascript
const initialState = {
  chats: [],             // [{ id, name, timestamp }, ...]
  messages: [],          // [{ id, sender, text, type, timestamp, payload, failed }, ...]
  status: "idle",        // "idle" | "loading" | "sending" | "creating" | "error"
  error: null,           // string | null
  currentChatId: null,   // string | null (UUID)
};
```

### Reducer Actions

| Action | Effect |
|--------|--------|
| `LOAD` | Replace messages from API response |
| `ADD_MESSAGE` | Append message to messages array |
| `SET_STATUS` | Update status field |
| `SET_ERROR` | Set/clear error field |
| `SET_CURRENT_CHAT` | Set currentChatId |
| `ADD_CHAT` | Prepend new chat to chats list |
| `LOAD_CHATS` | Replace chats list |
| `RESET_MESSAGES` | Clear messages + currentChatId |
| `MARK_MESSAGE_FAILED` | Set failed=true on message by id |
| `CLEAR_MESSAGE_FAILED` | Clear failed flag on message by id |

### Component-Level State (`useState`)

| State | Type | Purpose |
|-------|------|---------|
| `draft` | string | Chat input text (synced to localStorage) |
| `uploadingFile` | File | Selected file for upload (UI hidden) |
| `uploadProgress` | number | Upload progress % (simulated animation) |
| `tokenStats` | `{used, total}` | Token budget display |
| `activeStep` | number | Current entrepreneur step (1–7) |
| `isStepsSidebarOpen` | boolean | Mobile steps panel visibility |
| `isSendDisabled` | boolean | Blocks send on 402 token exhaustion |

---

## 8. API Integration

**Base URL:** `import.meta.env.VITE_CHAT_API_BASE_URL`

All calls use `authService.authFetch()` (adds Bearer token, handles 401 refresh).

### Chat Service Methods (`src/services/chatService.js`)

#### `getAllChats()`
```
GET /api/chat/history/
Response: { message: [{ detail: { chat_id, chat_name } }, ...] }
Returns: [{ id, name, timestamp }]
```

#### `createNewChat()`
```
GET /api/chat/new-chat/
Response: { message: { chat_id, chat_name } }
Returns: { chatId, chatName }
```

#### `sendMessage(chatId, userInput, step = null)`
```
POST /api/chat/structured-agent/?chat-id={chatId}
Body: { user_input: string, step: "entrepreneur_step_1" | ... | "entrepreneur_step_7" }
Response: { message: { type, response, data, step, ... } }
Returns: { type, data, step, ...rest }

Error cases:
  402 → Token exhausted. Error body: { notify: "..." } or { notifiy: "..." }
  Other → Generic error with cleaned message
```

#### `getChatMessages(chatId)`
```
GET /api/chat/history/?chat-id={chatId}
Response: { message: [{ user: "..." } | { agent: {...} }, ...] }
Returns: Normalized array of message objects:
  { id, sender: "user"|"ai", text, type, timestamp, payload }
```

#### `getTokenStats()`
```
GET /api/chat/token/
Response: { message: { used, total } } or { used, total }
Returns: { used: number, total: number }
```

#### Template Download (in `EntrepreneurialResponse.jsx`)
```
GET /api/chat/template/{templateName}/
Response: Binary blob (Excel file)
Triggers browser download via <a> click
```

---

## 9. Component Hierarchy & Details

```
App
├── Navbar.jsx
├── Sidebar.jsx
├── ChatWindow.jsx (active tab)
│   ├── Steps Sidebar (7 buttons, collapsible on mobile)
│   ├── Message Area
│   │   ├── [Empty state] "Start a conversation..."
│   │   ├── User Message Bubble (blue, right-aligned)
│   │   ├── AI Message Bubble (gray, left-aligned)
│   │   │   ├── <EntrepreneurialResponse /> (type=entrepreneurial_response)
│   │   │   ├── <img /> + download button (type=image_response)
│   │   │   └── <ReactMarkdown /> (type=general_response, default)
│   │   ├── Failed Message Indicator + Retry button
│   │   └── <ThinkingLoader /> (during "sending")
│   └── Input Area
│       ├── Text input (draft persisted to localStorage)
│       ├── [Hidden] File input
│       └── Send button (disabled when sending/token-exhausted)
└── ToastContainer
```

### Navbar.jsx

- Displays Brunda lab logo (hardcoded)
- Notification bell icon (non-functional, badge hardcoded to "2")
- User profile: hardcoded "Brunda" / "Entrepreneur" (not fetched from API)

### Sidebar.jsx

- 16 navigation menu items with Material UI icons
- Responsive: collapses to hamburger overlay on mobile
- Internal routes: navigate via React Router
- External links: `window.location.href` with `?sid=` appended
- AI Assistant tab: redirects to `VITE_EXTERNAL_DASHBOARD_URL`
- Logout: `tokenStorage.clearTokens()` + `window.location.reload()`

### ChatWindow.jsx (1043 lines — central component)

Core responsibilities:
- All message state management via useReducer
- API calls for chat lifecycle
- Step-based routing (sends step param with each message)
- 3 response type renderers
- Token stats display
- Draft auto-save

### EntrepreneurialResponse.jsx

Renders the full `entrepreneurial_response` payload:

| Section | Data |
|---------|------|
| Idea Summary | title, one_liner, strengths[], risks[] |
| Roadmap | steps[]: step#, title, description, resources[], templates[] |
| Execution Support | automated_content[], design_branding |
| Mentorship | suggested_experts[] |
| Events | events[]: title, date, location, link |
| Funding | funding[]: name, type, ticket_size, stage_focus, contact |

Each template in roadmap has a download button triggering `GET /api/chat/template/{name}/`.

### ThinkingLoader.jsx

Animated loading bubble shown while `status === "sending"`:
- Blue chat bubble
- 3 bouncing dots
- Text: "Co-Founder is thinking..."

---

## 10. AI Chat/Bot UI Flow

### 10.1 Component Mount

```
useEffect runs on mount:
  ├── Load draft from localStorage["chat_draft"]
  └── If activeTab === "ai-co-founder":
      ├── getAllChats() → dispatch LOAD_CHATS
      ├── getTokenStats() → setTokenStats
      └── If chats exist: getChatMessages(chats[0].id) → dispatch LOAD
```

### 10.2 Message Send Flow

```
User types text, clicks Send (or presses Enter)
  │
  ├── Guard: draft.trim() === "" && !uploadingFile → return
  │
  ├── If no currentChatId:
  │     createNewChat() → dispatch ADD_CHAT + SET_CURRENT_CHAT
  │
  ├── Dispatch ADD_MESSAGE (user message, optimistic)
  ├── Clear input, clear file
  ├── Dispatch SET_STATUS("sending")
  │
  ▼
chatService.sendMessage(chatId, content, "entrepreneur_step_{activeStep}")
  │
  ├── Success:
  │     Extract text from response:
  │       If type === "general_response":
  │         text = response.data (string) or response.data.text or stringify
  │       Else:
  │         text = JSON.stringify(response.data)
  │     Dispatch ADD_MESSAGE (AI message, with payload for structured rendering)
  │     getTokenStats() → update token display
  │
  └── Error:
        Dispatch MARK_MESSAGE_FAILED (user message id)
        If 402: setIsSendDisabled(true) + toast with backend message
        Else: toast with cleaned error message
        Dispatch SET_STATUS("idle")
```

### 10.3 Step-Based Conversations

Clicking a step button:
```
1. setActiveStep(step.number)
2. Close mobile sidebar
3. Auto-create chat if needed
4. Send "Hi" with step="entrepreneur_step_{number}"
5. Process response normally
6. Failed sends → "Retry" button
```

Retry handler:
```javascript
const handleRetrySend = async (message) => {
  dispatch(CLEAR_MESSAGE_FAILED(message.id))
  // Re-send original text with same step
  await sendMessage(chatId, message.text, stepParam)
}
```

### 10.4 Response Type Rendering

```javascript
switch (message.type) {
  case "entrepreneurial_response":
    return <EntrepreneurialResponse payload={message.payload} />;

  case "image_response":
    return (
      <>
        <img src={message.payload.logo} />
        <button onClick={downloadImage}>Download</button>
      </>
    );

  case "general_response":
  default:
    return <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>;
}
```

Markdown renderer applies custom component styles:
- `p`, `h1`–`h4`, `ul`, `ol`, `code`, `a`, `blockquote`
- Different text colors for user (white-on-blue) vs AI (dark on gray)

### 10.5 Token Exhaustion Handling

```
402 response received
  │
  ├── isSendDisabled = true (blocks future sends)
  ├── User message marked failed
  └── Toast: message from backend (e.g., "Token consumed, please buy the tokens")

Send button rendered as disabled with AlertTriangle icon
User must purchase tokens externally and reload page
```

---

## 11. Data Schemas

### Chat Object

```javascript
{
  id: string,          // UUID from backend (chat_id)
  name: string,        // "New Chat" or user-set name
  timestamp: string    // ISO 8601
}
```

### Message Object

```javascript
{
  id: string,                    // Unique (timestamp-based)
  sender: "user" | "ai",
  text: string,                  // Display text
  type?: string,                 // "entrepreneurial_response" | "image_response" | "general_response"
  timestamp: string,             // Formatted date string
  file?: File,                   // Attached file (if any)
  failed?: boolean,              // True if send failed
  payload?: object               // Full structured response data
}
```

### Entrepreneurial Response Payload

```javascript
{
  type: "entrepreneurial_response",
  data: {
    idea_summary: {
      title: string,
      one_liner: string,
      strengths: string[],
      risks: string[]
    },
    roadmap: [{
      step: number,
      title: string,
      description: string,
      resources: string[],
      templates: [{ template_name: string, description: string }]
    }],
    execution_support: {
      automated_content: [{ type, title, draft }],
      design_branding: {
        name_ideas: string[],
        logo_concepts: string[]
      }
    },
    mentorship: {
      suggested_experts: [{ name, expertise, contact }]
    },
    events: [{ title, date, location?, link? }],
    funding: [{ name, type, ticket_size?, amount?, stage_focus?, contact? }]
  }
}
```

### Token Stats Object

```javascript
{ used: number, total: number }
```

---

## 12. Key User Journeys

### Journey 1: First Login

```
Bubble.io redirects user to frontend URL with ?sid=<token>
  │
  ▼
AuthProvider extracts sid from URL
  → Calls GET /api/bubble/auth/?sid=<token>
  → Receives { access, refresh }
  → Stores both in localStorage
  │
  ▼
AuthProvider sets loading = false
  │
  ▼
ChatWindow renders:
  → Loads all previous chats
  → Gets token stats
  → Auto-loads most recent chat history
```

### Journey 2: Returning User

```
Page loads
  │
  ▼
AuthProvider: sid not in URL, but access_token + refresh_token in localStorage
  → Reuses existing tokens
  → No API call needed
  │
  ▼
ChatWindow renders normally
```

### Journey 3: Exploring Entrepreneur Steps

```
User clicks "Step 3: Business and Legal Foundation"
  │
  ├── activeStep = 3
  ├── Mobile sidebar closes
  ├── Auto-create chat if none exists
  │
  ▼
sendMessage(chatId, "Hi", "entrepreneur_step_3")
  │
  ▼
Backend processes step context (step_3_prompt + LangGraph tools)
  │
  ▼
Response: entrepreneurial_response with legal/compliance guidance
  │
  ▼
<EntrepreneurialResponse /> renders:
  - Objectives for step 3
  - Roadmap items
  - Downloadable legal compliance template
  - Resources and mentorship
```

### Journey 4: Downloading a Template

```
EntrepreneurialResponse renders template button
  │
  ▼
handleTemplateDownload("legal-compliance-checklist.xlsx")
  │
  ▼
authFetch GET /api/chat/template/legal-compliance-checklist.xlsx/
  → Response: binary blob
  │
  ▼
window.URL.createObjectURL(blob)
  → Trigger <a> click with download attribute
  → File downloads to user's computer
  │
  ▼
window.URL.revokeObjectURL() cleanup
```

### Journey 5: Token Exhaustion Recovery

```
Send message → 402 response
  │
  ├── isSendDisabled = true
  ├── Toast notification: "Token consumed, please buy the tokens"
  └── Send button replaced with disabled AlertTriangle button

[User purchases tokens externally]

User manually reloads page
  → Token stats refresh
  → isSendDisabled resets to false
  → Conversation continues
```

---

## 13. Environment Variables

```bash
VITE_CHAT_API_BASE_URL=https://backend.thentrepreneurlab.com
VITE_EXTERNAL_DASHBOARD_URL=https://app.bubble.io/...   # Redirect for external tabs
```

No `.env.example` in repo. Variables injected at Vite build time via `import.meta.env.*`.

---

## 14. Styling & Theming

### Colors

| Element | Color |
|---------|-------|
| Navbar background | `#27368F` (dark blue) |
| User message bubbles | `#0066ff` (bright blue) |
| AI message bubbles | `#f4f7fa` (light gray) |
| Error state | `#ef2f15` (red) |
| Send button | Blue |

### Typography

- Primary font: Inter (loaded via Google Fonts in `index.css`)
- Fallback: Arial, Roboto

### Responsive Design

- Mobile-first approach using Tailwind breakpoints (`sm`, `md`, `lg`)
- Sidebar: collapses to hamburger overlay on mobile
- Steps panel: collapsible on mobile (`isStepsSidebarOpen`)
- Desktop: both sidebars always visible

---

## 15. Build & Deployment

### Development

```bash
npm run dev      # Vite dev server with HMR
```

Vite config allows host `unjudged-westwardly-trisha.ngrok-free.dev` for ngrok tunneling.

### Production Build

```bash
npm run build    # Outputs to dist/
npm run preview  # Serve dist/ locally
```

### Vercel Deployment (`vercel.json`)

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

All server routes return `index.html` — React Router handles client-side routing.

---

## 16. Real-Time / WebSocket

**Status: Not implemented on the frontend.**

The backend has WebSocket endpoints (`/ws/static/<chat_id>/`) for real-time agent progress events, but the frontend has no WebSocket client. All communication is request/response via REST API.

Agent progress during generation is not visible to the user — only the final response arrives.

---

## 17. Error Handling & UX States

### Error Cleaning

```javascript
function cleanErrorMessage(message) {
  return message
    .replace(/\b\d{3}\b/g, "")          // Remove HTTP status codes
    .replace(/^(Error|Failed|Status):/i, "") // Remove technical prefixes
    .trim() || "An error occurred. Please try again.";
}
```

### Loading States

| Status | UI Effect |
|--------|-----------|
| `"idle"` | Normal, send enabled |
| `"loading"` | Fetching chat history |
| `"sending"` | `<ThinkingLoader />` shown, send disabled |
| `"creating"` | New chat being created |
| `"error"` | Error message displayed |

### Auth Loading

```jsx
{loading && (
  <div className="fixed inset-0 bg-white/80 flex items-center justify-center">
    <Spinner />
    <p>Signing you in...</p>
  </div>
)}
```

---

## 18. Legacy Code & Known Issues

### Unused Files

| File | Status |
|------|--------|
| `src/api/chat.js` | Legacy chat API client — uses `/api/chat/agent/` (not `/api/chat/structured-agent/`). Has retry logic. Not imported anywhere. |
| `src/pages/Dashboard.jsx` | Defined but no route points to it. |
| `src/utils/responseParser.js` | Parsing utility — not actively used. |

### Commented-Out Code

- File upload UI in `ChatWindow.jsx` (lines ~993–1025): full UI section hidden with CSS `hidden` class, not removed
- StrictMode in `main.jsx`: commented out

### Inconsistencies

| Issue | Detail |
|-------|--------|
| Two chat API implementations | `chatService.js` (active, structured-agent) vs `chat.js` (unused, agent) |
| Response field typos from backend | `messsage`, `notifiy` — frontend handles both spellings |
| Hardcoded user profile | Navbar shows "Brunda" / "Entrepreneur" — not fetched from auth context |
| Hardcoded notification badge | Bell shows "2" regardless of actual state |
| Image upload incomplete | UI hidden, no backend upload endpoint wired |

---

## 19. Branch Differences: `dev/frontend` vs `dev/frontend-change-1-disable-token`

**No code differences.** Both branches are at the same commits:
- `c4e73c7`, `9e51278`, `56e196c`

The branch name suggests it was created to correspond to the backend's token-disable feature, but no frontend changes were made.

---

## 20. Performance Notes

### Current Characteristics

- React 19 (automatic batching, concurrent features)
- No code splitting or lazy loading
- No message virtualization (all messages rendered at once)
- No memoization (`React.memo`, `useMemo`, `useCallback` not used)
- Draft auto-saved to localStorage (no network call)

### Potential Bottlenecks

- Very long chat histories will render all messages simultaneously
- All components load eagerly — no lazy() / Suspense
- Multiple icon libraries loaded (lucide-react + react-feather + @mui/icons-material)

---

## 21. Security Considerations

| Concern | Current State |
|---------|--------------|
| Token storage | `localStorage` — accessible to XSS attacks |
| Token refresh | Max 2 retries, then throws error |
| HTTPS enforcement | Not enforced in Vite config (relies on host/CDN) |
| CSRF protection | No CSRF token handling (API uses JWT Bearer, which avoids CSRF) |
| SID in URL | Exposed in browser history — short-lived (5min backend TTL) |
| Redirect | External dashboard redirect disabled in current code (commented) |
