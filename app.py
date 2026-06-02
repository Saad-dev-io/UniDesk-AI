"""
UniDesk AI — FastAPI Server
==============================
Main application server that:
  - Serves the chat frontend (static HTML/CSS/JS)
  - Exposes the /api/chat endpoint for AI triage
  - Provides ticket management and statistics endpoints
  - Handles session management and error recovery

Endpoints:
  GET  /              → Serve the chat UI
  POST /api/chat      → Send a message, get AI triage response
  POST /api/reset     → Reset a chat session
  GET  /api/tickets   → List all triaged tickets
  GET  /api/tickets/{id} → Get a single ticket
  PATCH /api/tickets/{id} → Update ticket status
  GET  /api/stats     → Dashboard statistics
  GET  /api/config    → Frontend configuration (categories, urgency levels)
"""

import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config import (
    APP_NAME,
    APP_VERSION,
    CATEGORIES,
    URGENCY_LEVELS,
    WELCOME_MESSAGE,
)
from triage_engine import TriageEngine
from ticket_manager import TicketManager

# ─── Fix Windows console encoding ───────────────────────────
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ─── Logging ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("unidesk")

from typing import Optional

# ─── Global instances ───────────────────────────────────────
engine: Optional[TriageEngine] = None
tickets = TicketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the triage engine on startup."""
    global engine
    try:
        engine = TriageEngine()
        logger.info("✅ UniDesk AI is ready! (model loaded)")
    except ValueError as e:
        logger.error("❌ Failed to initialize: %s", e)
        logger.error("   Set GOOGLE_API_KEY in your .env file")
        engine = None
    yield
    logger.info("UniDesk AI shutting down")


# ─── App Setup ──────────────────────────────────────────────
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)

# CORS — allow all origins for development/demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
try:
    os.makedirs("static", exist_ok=True)
except OSError:
    pass # Vercel read-only filesystem

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ═══════════════════════════════════════════════════════════════
# ROUTES — Pages
# ═══════════════════════════════════════════════════════════════


@app.get("/", response_class=FileResponse)
async def index():
    """Serve the main chat interface."""
    return FileResponse("templates/index.html")


# ═══════════════════════════════════════════════════════════════
# ROUTES — Chat API
# ═══════════════════════════════════════════════════════════════


@app.post("/api/chat")
async def chat(request: Request):
    """Process a chat message through the AI triage engine.

    Request body:
        {
            "session_id": "uuid-string",
            "message": "my wifi isn't working"
        }

    Response:
        {
            "success": true,
            "message": "AI response with markdown",
            "category": "network",
            "urgency": "P3",
            "confidence": 0.85,
            "needs_more_info": true,
            "is_self_resolvable": true,
            "should_create_ticket": false,
            "should_escalate": false,
            "ticket": null | { ticket object },
            ...
        }
    """
    if engine is None:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "message": (
                    "⚠️ The AI engine is not available right now. "
                    "Please make sure the GOOGLE_API_KEY is configured."
                ),
                "error": "Engine not initialized",
            },
        )

    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Invalid request body", "error": "Bad JSON"},
        )

    session_id = data.get("session_id", "default")
    user_id = data.get("user_id", "demo_student_01")
    message = data.get("message", "").strip()

    if not message:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Please type a message", "error": "Empty message"},
        )

    logger.info("📩 [%s] User %s: %s", session_id[:8], user_id, message[:80])

    # ─── Inject AI Memory (Past Tickets) ─────────────────────
    session_info = engine.get_session_info(session_id)
    is_first_message = session_info is None or session_info["message_count"] == 0
    if is_first_message:
        past_tickets = tickets.get_tickets(user_id=user_id, limit=3)
        if past_tickets:
            history_text = "\n".join([f"- Ticket {t['id']}: {t['summary']} ({t['status']})" for t in past_tickets])
            message = f"[System Context: The user's ID is {user_id}. Their recent tickets are:\n{history_text}]\n\nUser Message: {message}"

    # ─── Run the AI triage ───────────────────────────────
    result = await engine.process_message(session_id, message)

    # ─── Auto-create ticket if the engine recommends it ──
    ticket = None
    if (result.get("should_create_ticket") or result.get("is_self_resolvable")) and result.get("category"):
        ticket = tickets.create_ticket(
            category=result["category"],
            urgency=result.get("urgency", "P3"),
            summary=result.get("ticket_summary") or message[:100],
            session_id=session_id,
            escalated=result.get("should_escalate", False),
            escalation_reason=result.get("escalation_reason"),
            user_id=user_id,
            is_resolved=result.get("is_self_resolvable", False),
        )
        logger.info(
            "🎫 Ticket %s created: [%s] %s",
            ticket["id"],
            ticket["urgency"],
            ticket["summary"][:60],
        )

    if result.get("should_escalate"):
        logger.warning(
            "🚨 ESCALATION [%s]: %s",
            session_id[:8],
            result.get("escalation_reason", "Unknown"),
        )

    # ─── Build response ─────────────────────────────────
    response = {
        **result,
        "ticket": ticket,
    }

    logger.info(
        "🤖 [%s] Bot: cat=%s urg=%s conf=%.2f ticket=%s escalate=%s",
        session_id[:8],
        result.get("category"),
        result.get("urgency"),
        result.get("confidence", 0),
        ticket["id"] if ticket else "none",
        result.get("should_escalate", False),
    )

    return response


@app.post("/api/reset")
async def reset_session(request: Request):
    """Reset a chat session to start fresh.

    Request body:
        { "session_id": "uuid-string" }
    """
    if engine is None:
        return {"success": False, "error": "Engine not initialized"}

    data = await request.json()
    session_id = data.get("session_id", "default")
    was_reset = engine.reset_session(session_id)
    return {"success": True, "was_reset": was_reset}


# ═══════════════════════════════════════════════════════════════
# ROUTES — Ticket Management
# ═══════════════════════════════════════════════════════════════


@app.get("/api/tickets")
async def list_tickets(
    status: Optional[str] = None,
    category: Optional[str] = None,
    urgency: Optional[str] = None,
):
    """List all triaged tickets with optional filters.

    Query params:
        status: 'open' | 'in_progress' | 'resolved' | 'escalated'
        category: category key (e.g., 'network')
        urgency: 'P1' | 'P2' | 'P3' | 'P4'
    """
    return tickets.get_tickets(status=status, category=category, urgency=urgency)


@app.get("/api/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Get a single ticket by ID."""
    ticket = tickets.get_ticket(ticket_id)
    if ticket is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Ticket {ticket_id} not found"},
        )
    return ticket


@app.patch("/api/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, request: Request):
    """Update a ticket's status.

    Request body:
        { "status": "resolved" }
    """
    data = await request.json()
    new_status = data.get("status")
    if new_status not in ("open", "in_progress", "resolved", "escalated"):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid status. Use: open, in_progress, resolved, escalated"},
        )

    ticket = tickets.update_status(ticket_id, new_status)
    if ticket is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Ticket {ticket_id} not found"},
        )
    return ticket


# ═══════════════════════════════════════════════════════════════
# ROUTES — Dashboard & Config
# ═══════════════════════════════════════════════════════════════


@app.get("/api/stats")
async def get_stats():
    """Get aggregate statistics for the admin dashboard."""
    stats = tickets.get_stats()
    stats["active_sessions"] = engine.active_sessions if engine else 0
    return stats


@app.get("/api/config")
async def get_config():
    """Return frontend configuration (categories, urgency levels, welcome message)."""
    return {
        "app_name": APP_NAME,
        "categories": CATEGORIES,
        "urgency_levels": URGENCY_LEVELS,
        "welcome_message": WELCOME_MESSAGE,
    }


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║         🎓 UniDesk AI — IT Support        ║")
    print("  ║   Intelligent University Helpdesk Agent    ║")
    print("  ╠═══════════════════════════════════════════╣")
    print("  ║  Open:  http://localhost:8000              ║")
    print("  ║  Docs:  http://localhost:8000/docs         ║")
    print("  ║  Stop:  Ctrl+C                             ║")
    print("  ╚═══════════════════════════════════════════╝")
    print()

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
