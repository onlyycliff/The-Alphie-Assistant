# Alphie

> An agentic personal assistant, built in public: LLM reasoning + real-world tool execution, phased toward full voice/device integration.

---

## Overview

Alphie is a personal AI assistant built from scratch, combining an LLM "brain" (Google Gemini) with real tool-execution capabilities — the same core pattern (model reasons → requests a tool → code executes it → result informs the response) that underlies production AI agent systems. The project is being built incrementally, one verified capability at a time, and documented as it goes.

**Why this project exists:** Iron Man's JARVIS was the reason I fell in love with the idea of AI before I knew what AI even was. When I first saw Iron-Man I loved the fact that he had his own artificial assistant. It was able to help him answer and solve any problem he had. During that time though it was just a sought out dream. But ever since watching the new Spiderman Brand New Day movie, I realized that I can actually create something and put it into motion. I'm currently a college sophomore and now I have more hope, passion, and ambition. This can be done and I'm starting by calling her Alphie. I want her to help me with simple questions, "Hey Alphie, turn the lights down to 50%", or, "Hey Alphie, text mom that I ordered groceries". Maybe I'll even give her the ability to control the lock on my room door. The possibilities are endless and that's why this project exists.

---

## Current Status

**Phase:** 2 complete, Phase 3 in progress — Gmail, Calendar (read-only), and Google Search grounding done; push-to-talk voice recording done; Whisper transcription and text-to-speech next

| Phase | Status | Description |
|---|---|---|
| 0 — Foundations | ✅ Done | Python, Git, CLI fundamentals |
| 1 — Brain | ✅ Done | Conversational agent with tool-calling (Gemini API) |
| 2 — Hands | ✅ Done | Gmail (read-only), Calendar (read-only), and opt-in Google Search grounding. Outlook pending UConn IT approval, tracked separately |
| 3 — Voice | 🔄 In progress | Push-to-talk recording (pynput + sounddevice) done; Whisper transcription and Piper text-to-speech next |
| 4 — Phone access | ⬜ Not started | Telegram bot deployment, remote access |
| 5 — Memory & proactivity | ⬜ Not started | Semantic memory (vector DB), scheduled tasks |
| 6 — Expansion | ⬜ Not started | Smart home, dashboard, browser automation |

---

## Architecture

*(Add a diagram here — even a simple hand-drawn or Mermaid diagram of: user → chat loop → model → tool dispatch → tool execution → result → model → response)*

**Current components:**
- `alphieassistant.py` — main chat loop, tool declarations, and tool wrapper functions
- `gmail_tool.py` — Gmail OAuth handling (`get_gmail_service`) and unread-email fetching (`get_unread_emails`), kept separate from the main file per single-responsibility
- `gcalendar_tool.py` — Calendar OAuth handling (`get_calendar_service`) and upcoming-event fetching (`get_upcoming_events`), same structural pattern as `gmail_tool.py`
- `.env` — local secrets (Gemini API key, `USE_SEARCH_GROUNDING` toggle), not committed
- `credentials.json` / `token.json` / `gcalendar_token.json` — Google OAuth client secret and per-service stored tokens, not committed
- `output.wav` — generated voice recording, regenerated on every push-to-talk use, not committed
- `requirements.txt` — pinned dependency snapshot via `pip freeze`
- Tools implemented: `get_current_time`, `calculation`, `check_unread_emails`, `check_upcoming_events`, opt-in Google Search grounding

**Gmail integration notes:**
- Auth flow: Google Cloud Console project → OAuth consent screen (testing mode, self as test user) → `credentials.json` → browser consent on first run → `token.json` cached for reuse
- `service` (the authenticated Gmail client) is created once at module level in `alphieassistant.py` and accessed by `check_unread_emails()` via closure, rather than re-authenticating on every tool call
- Scope: `gmail.readonly` only — deliberately least-privilege, since send/reply capability introduces real side-effect risk the project isn't ready to hand an LLM yet

**Calendar integration notes:**
- Reuses the same Google Cloud project and OAuth consent screen as Gmail, with its own scope (`calendar.readonly`) and its own token file (`gcalendar_token.json`) — kept separate from Gmail's `token.json` deliberately, since sharing one token file across two scopes would silently overwrite one service's access with the other's
- Same closure pattern as Gmail: `calendar_service` created once at module level, accessed by `check_upcoming_events()` without re-authenticating per call
- Scope: `calendar.readonly` only — write access (creating/deleting events) intentionally deferred until a confirmation-before-write safety layer exists
- Known duplication: `get_calendar_service()` and `get_gmail_service()` share nearly identical OAuth boilerplate. Deliberate tradeoff for now — a shared `google_auth.py` refactor is planned as its own separate branch/PR rather than bundled into either feature

**Google Search grounding notes:**
- Built using `types.Tool(google_search=types.GoogleSearch())`, matching the "legacy" `chats.create`/`generate_content` API surface (not Google's newer `interactions.create` API, which isn't a drop-in swap since it doesn't manage conversation history the same way)
- Gated behind an opt-in `.env` flag (`USE_SEARCH_GROUNDING`), off by default — the free tier's grounding-specific quota is far stricter than general chat quota (hit `429` after a handful of grounded requests with chat RPM/RPD nowhere near maxed), so it's kept opt-in rather than always available to the model's judgment
- `.env` booleans are read as strings and explicitly compared (`os.getenv(...) == "True"`), not used as a bare truthy check — a bare `if os.getenv(...)` would treat the literal text `"False"` as truthy, since any non-empty string is truthy in Python

**Voice recording notes (Phase 3, push-to-talk):**
- `pynput.keyboard.Listener` detects `on_press`/`on_release` for a dedicated push-to-talk key, chosen deliberately over continuous/always-on listening — a hard physical boundary (no key held, no audio captured) is a simpler, stronger privacy guarantee than software wake-word detection, especially relevant given Alphie's access to email and calendar
- A module-level `is_recording` boolean guards against key-repeat: holding a key fires `on_press` repeatedly (OS-level behavior, not a bug), so the guard ensures only the first press starts a recording
- Uses `sounddevice.InputStream`, not `sd.rec()` — `sd.rec()` requires a fixed duration known in advance, which doesn't fit push-to-talk where duration depends on how long the key is held
- The stream's callback fires continuously with small audio chunks; each is appended (`.copy()`'d, to avoid buffer-reuse corruption) to a list rather than written to disk per-call. On release, chunks are concatenated (`numpy.concatenate`) into one array and written to `output.wav` once
- Relies on the OS's default input device rather than hardcoding one in code — deliberate tradeoff, since physical mics get swapped often; device selection is handled at the OS level instead

---

## Tech Stack

- **Language:** Python
- **LLM:** Google Gemini API (`google-genai` SDK)
- **Environment management:** `venv`, `python-dotenv`
- **Gmail integration:** Gmail API via `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib` (OAuth2 desktop-app flow)
- **Calendar integration:** Google Calendar API, same auth libraries as Gmail, separate scope and token file
- **Search grounding:** Google Search grounding via `google-genai`'s built-in `types.Tool`/`types.GoogleSearch`, opt-in
- **Voice input:** `pynput` (push-to-talk key detection), `sounddevice` (microphone capture), `wavio`/`numpy` (writing accumulated audio to `.wav`)
- **Voice output (planned):** Piper TTS (`piper-tts`, `OHF-Voice/piper1-gpl` fork — the original `rhasspy/piper` repo is archived, this fork is the actively maintained successor, GPL-3.0)
- *(add each new dependency here as it's introduced — e.g. Whisper, ChromaDB, etc.)*

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
USE_SEARCH_GROUNDING=False
```

Run:
```powershell
python alphieassistant.py
```

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

### Aug 2026 — Deprecated datetime method broke a downstream format assumption
While building `get_upcoming_events()`, fixed a `datetime.utcnow()` deprecation warning by switching to the timezone-aware `datetime.now(datetime.timezone.utc)`. This introduced a real bug: the old code manually appended `"Z"` to the timestamp string, which was correct for `.utcnow()` (a timezone-naive method with no offset of its own), but the timezone-aware replacement's `.isoformat()` already includes a `+00:00` offset — so the manual `"Z"` produced a malformed double-timezone timestamp (`...+00:00Z`), which the Calendar API rejected with a 400 error. Root cause took two steps to trace (an unrelated 403 from a not-yet-fully-enabled API had to be ruled out first). Lesson: fixing a deprecation warning can silently break an assumption elsewhere in the same code that depended on the old method's specific output shape — check what depends on a line before changing it, not just whether the line itself still runs.

### Aug 2026 — Google Search grounding kept opt-in due to strict free-tier quota
Built and confirmed working Google Search grounding, but discovered its quota is separate from and much stricter than general chat quota — hit `429 RESOURCE_EXHAUSTED` after a handful of grounded requests despite chat RPM/RPD being nowhere near their own limits. Rather than remove the feature, gated it behind an opt-in `.env` flag so it's never active by default — this prevents the model from silently spending a scarce daily allotment on searches it decides to run on its own judgment, while keeping the working code available for deliberate use.

### Aug 2026 — sounddevice.InputStream chosen over sd.rec() for push-to-talk
`sd.rec()` requires a fixed recording duration set in advance, which doesn't fit push-to-talk — the actual duration depends on how long the key is held, unknown ahead of time. `sounddevice.InputStream` instead runs a continuous callback that fires repeatedly with small audio chunks for as long as the stream is open, manually started on key-press and stopped on key-release. Chunks are accumulated in a list and only concatenated/written to disk once, after the stream stops, rather than writing on every callback firing (which would otherwise overwrite the output file dozens of times per second with only the most recent fragment).

### Aug 2026 — Guard flag against key-repeat for push-to-talk
Holding a key down fires `pynput`'s `on_press` callback repeatedly (OS-level key-repeat behavior), which would otherwise start a new, overlapping recording stream on every repeated firing while the key is held. Fixed with a module-level `is_recording` boolean checked in `on_press` (`if key.char == 'q' and not is_recording:`) — a standard debouncing pattern for event-driven code, not specific to `pynput`, and one that will likely recur in future event-driven pieces of this project.

---

## Roadmap

See phase table above. Full detailed roadmap: `JARVIS_Project_Roadmap.md` *(link or move this into the repo if you want it public)*.

---

## Demo

*(Add a short GIF or terminal recording once voice is working end-to-end — this matters more than any written description for showing the project is real.)*

---

## License

*(Pick one — MIT is the standard default for portfolio projects unless you have a reason not to. Note: if Piper TTS (GPL-3.0) ends up bundled/distributed rather than just used locally, check GPL compatibility before choosing a license.)*