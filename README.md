---
title: UniDesk AI
emoji: 🎓
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
---

# 🎓 UniDesk AI — Intelligent University IT Helpdesk Agent
> An AI-powered triage agent that handles 80% of university IT support requests autonomously — classifying issues, resolving common problems with step-by-step guides, and routing complex tickets to the right specialist team.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_3.1_Flash_Lite-AI-orange?logo=google&logoColor=white)

---

## 📋 Case Study Write-Up

### Why This Problem?

As a university student, I've experienced the pain firsthand — submitting IT tickets that sit unanswered for days while simple issues like WiFi troubleshooting or password resets get stuck in the same queue as critical system outages. University IT helpdesks handle **500+ tickets per week**, and roughly **60% are routine issues** (password resets, WiFi problems, software installations) that follow predictable resolution patterns. This is a textbook case of a workflow that's repetitive, data-heavy, and still done manually.

I discovered this was worth solving when I realized that the classification and initial triage step — which takes a human agent 3–5 minutes per ticket — could be handled by AI in seconds with high accuracy. The payoff: students get faster resolutions, and IT staff can focus on complex problems that actually need human expertise.

### Who Is the User?

**Primary:** University IT helpdesk staff who receive hundreds of requests and need intelligent pre-triage to prioritize their workload.

**Secondary:** Students and faculty who want fast IT support without waiting in a queue — especially for common issues that have known solutions.

### Architecture: How the Agent Works

```
User describes issue in natural language
        │
        ▼
┌─────────────────────────┐
│   AI Triage Engine      │  ← Gemini 2.0 Flash with structured JSON output
│   (Autonomous Decisions)│
│                         │
│  1. Classify category   │  → Network, Account, Software, Hardware, etc.
│  2. Assess urgency      │  → P1 Critical → P4 Low
│  3. Evaluate action     │  → Self-resolve? Clarify? Ticket? Escalate?
└────────┬────────────────┘
         │
    ┌────┴────┬──────────────┬────────────────┐
    ▼         ▼              ▼                ▼
 SELF-     CLARIFY      CREATE TICKET     ESCALATE
 RESOLVE   (ask 1-2     (route to the     (page human
 (provide  targeted     right specialist   immediately
 step-by-  questions)   team with full     for security/
 step                   context + SLA)     critical)
 guide)
```

**Autonomous decisions (the 80%):**
- Classifying issues into 8 categories with confidence scoring
- Assessing urgency (P1–P4) based on impact and scope
- Self-resolving routine issues with curated knowledge base guides
- Gathering missing information through targeted clarifying questions
- Creating pre-triaged tickets routed to the correct specialist team

**Escalated to humans (the 20%):**
- Security incidents (hacking, phishing, data breach)
- System-wide outages affecting multiple users
- User explicitly requests a human agent
- Agent cannot confidently classify after 2 attempts
- Issues involving sensitive data or emotional distress

### What I Learned

- **Structured JSON output from LLMs is powerful but fragile.** I built a 4-level fallback parser because even with explicit instructions, Gemini occasionally wraps JSON in code fences or adds preamble text. Robust parsing is non-negotiable for production agents.
- **The system prompt IS the product.** 80% of the agent's intelligence lives in the system prompt — the decision framework, escalation triggers, and few-shot examples. Engineering the prompt was harder than engineering the code.
- **Graceful failure > perfect accuracy.** A triage bot that confidently misroutes a security incident is worse than one that says "I'm not sure, let me escalate this." I designed escalation triggers to be aggressive on safety.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- A free [Google Gemini API key](https://aistudio.google.com/)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR-USERNAME/unidesk-ai.git
cd unidesk-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your API key
# Edit the .env file and replace 'your_api_key_here' with your actual key
echo GOOGLE_API_KEY=your_actual_key_here > .env

# 4. Run the server
python app.py
```

Open **http://localhost:8000** in your browser.

---

## 🏗️ Technical Architecture

### Core Technologies
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python + FastAPI | Async API server with auto-docs |
| **Database** | SQLite + sqlite3 | Persistent storage for tickets and statistics |
| **AI Engine** | Google Gemini 3.1 Flash Lite | Natural language understanding + structured JSON output |
| **Knowledge Base** | Python module | Curated step-by-step IT solution guides |
| **Frontend** | Tailwind CSS + Marked.js + DOMPurify | Real-time chat interface with triage visualization and Live Dashboard |

### Project Structure
```
├── app.py                 # FastAPI server — routes, session mgmt, auto-ticket creation
├── triage_engine.py       # AI brain — Gemini chat sessions, JSON parsing, fallbacks
├── config.py              # Categories, urgency levels, routing rules, system prompt
├── knowledge_base.py      # 8 curated solution guides for common IT issues
├── ticket_manager.py      # SQLite ticket CRUD + dashboard statistics
├── requirements.txt       # Python dependencies
├── .env                   # API key (gitignored)
├── static/                # Reserved for future static assets
└── templates/
    └── index.html         # Stitch-designed Tailwind chat UI, Dashboard, and Tickets Viewer
└── data/
    └── triage.db          # Persistent SQLite database (auto-generated)
```

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Chat interface |
| `POST` | `/api/chat` | Send message → AI triage response |
| `POST` | `/api/reset` | Reset chat session |
| `GET` | `/api/tickets` | List triaged tickets (filterable) |
| `GET` | `/api/tickets/{id}` | Get ticket details |
| `PATCH` | `/api/tickets/{id}` | Update ticket status |
| `GET` | `/api/stats` | Dashboard statistics |
| `GET` | `/api/config` | Frontend configuration |

### Failure Handling

| Scenario | Agent Behavior |
|----------|---------------|
| Vague/messy input | Asks 1–2 targeted clarifying questions |
| Gibberish/spam | Politely requests rephrasing |
| Multiple issues in one message | Addresses the most urgent, acknowledges others |
| Out-of-scope request | States boundaries, suggests alternatives |
| API/LLM failure | Falls back to error message, doesn't crash |
| Low confidence classification | Escalates to human after 2 attempts |

---

## 📊 Issue Categories & Urgency Levels

### Categories
| Category | Icon | Routed To |
|----------|------|-----------|
| Network & WiFi | 🌐 | Network Operations |
| Account & Access | 🔑 | Identity & Access Management |
| Software & Apps | 💻 | Application Support |
| Hardware & Devices | 🖥️ | Field Operations |
| Email & Comms | 📧 | Communication Systems |
| LMS & Academic | 📚 | Academic IT Support |
| Security | 🛡️ | Security Operations (IMMEDIATE) |
| General / Other | 📋 | General IT Support |

### Urgency Levels
| Level | Name | SLA | Example |
|-------|------|-----|---------|
| **P1** | Critical | 1 hour | Exam portal down, security breach |
| **P2** | High | 4 hours | Multiple users affected, deadline-critical |
| **P3** | Medium | 24 hours | Single user, workaround available |
| **P4** | Low | 72 hours | Feature request, general question |

---

## 🛠️ Built By

**Saad** — Computer Science, FAST-NUCES (4th Semester)

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
