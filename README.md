# Alphie

> An agentic personal assistant, built in public: LLM reasoning + real-world tool execution, phased toward full voice/device integration.

---

## Overview

Alphie is a personal AI assistant built from scratch, combining an LLM "brain" (Google Gemini) with real tool-execution capabilities — the same core pattern (model reasons → requests a tool → code executes it → result informs the response) that underlies production AI agent systems. The project is being built incrementally, one verified capability at a time, and documented as it goes.

**Why this project exists:** I wanted to build my own personal assistant. When I first saw Iron-Man I loved the fact that he had his own artificial assistant. It was able to help him answer and solve any problem he had. During that time though it was just a sought out dream. But ever since watching the new Spiderman Brand New Day movie, I realized that I can actually create something and put it into motion. I'm currently a college sophomore and now I have more hope, passion, and ambition. This can be done and I'm starting by calling her Alphie. I want her to help me with simple questions, "Hey Alphie, turn the lights down to 50%", or, "Hey Alphie, text mom that I ordered groceries". Maybe I'll even give her the ability to control the lock on my room door. The possibilities are endless and that's why this project exists.
---

## Current Status

**Phase:** 1 complete, Phase 2 in progress *(update this as you move through phases)*

| Phase | Status | Description |
|---|---|---|
| 0 — Foundations | ✅ Done | Python, Git, CLI fundamentals |
| 1 — Brain | ✅ Done | Conversational agent with tool-calling (Gemini API) |
| 2 — Hands | 🔄 In progress | Calendar, email, and web-search integrations |
| 3 — Voice | ⬜ Not started | Local speech-to-text / text-to-speech |
| 4 — Phone access | ⬜ Not started | Telegram bot deployment, remote access |
| 5 — Memory & proactivity | ⬜ Not started | Semantic memory (vector DB), scheduled tasks |
| 6 — Expansion | ⬜ Not started | Smart home, dashboard, browser automation |

---

## Architecture

*(Add a diagram here once Phase 2 tools are in — even a simple hand-drawn or Mermaid diagram of: user → chat loop → model → tool dispatch → tool execution → result → model → response)*

**Current components:**
- `alphieassistant.py` — main chat loop, tool declarations, and tool functions
- `.env` — local secrets (API keys), not committed
- Tools implemented: `get_current_time`, `calculation`

---

## Tech Stack

- **Language:** Python
- **LLM:** Google Gemini API (`google-genai` SDK)
- **Environment management:** `venv`, `python-dotenv`
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

### [Date] — Soft vs. hard tool-call forcing
Considered forcing tool use for math via `interactions.create` + `tool_config`, but this API is only available on the single-shot `interactions.create` endpoint, not the stateful `chats.create` session used for conversation memory. Switching would mean manually rebuilding chat history management. Chose a system-prompt instruction (soft forcing) instead — Gemini's native arithmetic is already reliable for simple cases, and the engineering cost of losing built-in history tracking outweighed the benefit of 100% enforcement for a low-stakes tool. Will revisit hard forcing for higher-stakes tools (e.g. sending emails) where reliability matters more.

### [Date] — [next decision]
*(Add entries as you make them — the `tool_choice` investigation from this session is a good template for how to write these.)*

---

## Roadmap

See phase table above. Full detailed roadmap: `JARVIS_Project_Roadmap.md` *(link or move this into the repo if you want it public)*.

---

## Demo

*(Add a short GIF or terminal recording once Phase 2 tools are working — this matters more than any written description for showing the project is real.)*

---

## License

*(Pick one — MIT is the standard default for portfolio projects unless you have a reason not to.)*
