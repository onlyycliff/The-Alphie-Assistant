# Alphie

> An agentic personal assistant, built in public: LLM reasoning + real-world tool execution, phased toward full voice/device integration.

---

## Overview

Alphie is a personal AI assistant built from scratch, combining an LLM "brain" (Google Gemini) with real tool-execution capabilities — the same core pattern (model reasons → requests a tool → code executes it → result informs the response) that underlies production AI agent systems. The project is being built incrementally, one verified capability at a time, and documented as it goes.

**Why this project exists:** Iron Man's JARVIS was the reason I fell in love with the idea of AI before I knew what AI even was. When I first saw Iron-Man I loved the fact that he had his own artificial assistant. It was able to help him answer and solve any problem he had. During that time though it was just a sought out dream. But ever since watching the new Spiderman Brand New Day movie, I realized that I can actually create something and put it into motion. I'm currently a college sophomore and now I have more hope, passion, and ambition. This can be done and I'm starting by calling her Alphie. I want her to help me with simple questions, "Hey Alphie, turn the lights down to 50%", or, "Hey Alphie, text mom that I ordered groceries". Maybe I'll even give her the ability to control the lock on my room door. The possibilities are endless and that's why this project exists.

---

## Current Status

**Phase:** 1 complete, Phase 2 in progress — Gmail integration done, Calendar/Outlook next

| Phase | Status | Description |
|---|---|---|
| 0 — Foundations | ✅ Done | Python, Git, CLI fundamentals |
| 1 — Brain | ✅ Done | Conversational agent with tool-calling (Gemini API) |
| 2 — Hands | 🔄 In progress | Gmail (read-only) done; Calendar, Outlook, and web-search still to come |
| 3 — Voice | ⬜ Not started | Local speech-to-text / text-to-speech |
| 4 — Phone access | ⬜ Not started | Telegram bot deployment, remote access |
| 5 — Memory & proactivity | ⬜ Not started | Semantic memory (vector DB), scheduled tasks |
| 6 — Expansion | ⬜ Not started | Smart home, dashboard, browser automation |

---

## Architecture

*(Add a diagram here once Phase 2 tools are in — even a simple hand-drawn or Mermaid diagram of: user → chat loop → model → tool dispatch → tool execution → result → model → response)*

**Current components:**
- `alphieassistant.py` — main chat loop, tool declarations, and tool wrapper functions
- `gmail_tool.py` — Gmail OAuth handling (`get_gmail_service`) and unread-email fetching (`get_unread_emails`), kept separate from the main file per single-responsibility
- `.env` — local secrets (Gemini API key), not committed
- `credentials.json` / `token.json` — Gmail OAuth client secret and stored user token, not committed
- Tools implemented: `get_current_time`, `calculation`, `check_unread_emails`

**Gmail integration notes:**
- Auth flow: Google Cloud Console project → OAuth consent screen (testing mode, self as test user) → `credentials.json` → browser consent on first run → `token.json` cached for reuse
- `service` (the authenticated Gmail client) is created once at module level in `alphieassistant.py` and accessed by `check_unread_emails()` via closure, rather than re-authenticating on every tool call
- Scope: `gmail.readonly` only — deliberately least-privilege, since send/reply capability introduces real side-effect risk the project isn't ready to hand an LLM yet

---

## Tech Stack

- **Language:** Python
- **LLM:** Google Gemini API (`google-genai` SDK)
- **Environment management:** `venv`, `python-dotenv`
- **Gmail integration:** Gmail API via `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib` (OAuth2 desktop-app flow)
- *(add each new dependency here as it's introduced — e.g. Google Calendar API, Whisper, ChromaDB, etc.)*

---

## Setup

```powershell
git clone <repo-url>
cd ALPHIE
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_key_here
```

Run:
```powershell
python alphieassistant.py
```

*(Note: add a `requirements.txt` via `pip freeze > requirements.txt` — you don't have one yet, worth doing next.)*

---

## Engineering Decisions Log

A running log of nontrivial technical decisions and the reasoning behind them — this is meant to show *how* you think, not just what you built.

### Aug 2026 — Soft vs. hard tool-call forcing
Considered forcing tool use for math via `interactions.create` + `tool_config`, but this API is only available on the single-shot `interactions.create` endpoint, not the stateful `chats.create` session used for conversation memory. Switching would mean manually rebuilding chat history management. Chose a system-prompt instruction (soft forcing) instead — Gemini's native arithmetic is already reliable for simple cases, and the engineering cost of losing built-in history tracking outweighed the benefit of 100% enforcement for a low-stakes tool. Will revisit hard forcing for higher-stakes tools (e.g. sending emails) where reliability matters more.

### Aug 2026 — Least-privilege scope for Gmail
Built Gmail integration with the `gmail.readonly` scope only, even though full mailbox management (send, modify, delete) was available. The stated use case (checking for collaboration opportunities) only requires reading, and handing an LLM unsupervised send capability introduces real side-effect risk (a misinterpreted instruction could send an email) that the project isn't ready to handle — no confirmation-before-send logic exists yet. Send capability will be considered later as its own explicitly-scoped feature if needed.

### Aug 2026 — Closures over parameter-passing for tool-service access
`check_unread_emails()` (the tool exposed to the model) takes zero arguments, since Gemini's automatic function calling can only supply arguments a model could reasonably generate — it has no way to construct a Gmail `service` object. Instead, `service` is created once at module level in `alphieassistant.py`, and the wrapper function accesses it via closure (Python's enclosing-scope lookup) rather than re-authenticating on every call. This also avoids mixing authentication logic into a function whose job is fetching/formatting data.

### Aug 2026 — Outlook attempted first, blocked by school IT, pivoted to Gmail
Attempted Outlook/Microsoft Graph API integration first, reasoning that school email mattered more than personal collaboration email. Discovered UConn's Azure AD tenant blocks student app registration (`portal.azure.com` → "App registrations" → access denied), meaning OAuth app registration isn't available without IT approval. Sent a request to UConn IT to ask about access, but didn't block further work on it — pivoted to Gmail first since it requires no institutional approval and uses the same underlying OAuth2 + tool-calling pattern. Outlook integration will resume if/when IT grants access.

### Aug 2026 — Return type consistency across tool functions
`get_unread_emails()` originally had inconsistent return types across its code paths (string in two branches, empty list in the error branch). Standardized all paths to return a string, since the caller (eventually the model) needs a predictable type regardless of which branch executed. Also chose to join multiple email summaries into a single newline-separated string rather than returning a raw list, anticipating Phase 3 voice output — a pre-formatted string needs less work from the model to turn into clean spoken/written language.

---

## Roadmap

See phase table above. Full detailed roadmap: `JARVIS_Project_Roadmap.md` *(link or move this into the repo if you want it public)*.

---

## Demo

*(Add a short GIF or terminal recording once Phase 2 tools are working — this matters more than any written description for showing the project is real.)*

---

## License

*(Pick one — MIT is the standard default for portfolio projects unless you have a reason not to.)*