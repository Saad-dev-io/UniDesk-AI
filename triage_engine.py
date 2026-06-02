"""
UniDesk AI — Triage Engine
============================
The AI brain of the helpdesk agent. Uses Google Gemini 3.1 Flash Lite to:
  1. Understand user messages in natural language
  2. Classify issues into categories
  3. Assess urgency (P1-P4)
  4. Decide whether to self-resolve, ask questions, create ticket, or escalate
  5. Generate empathetic, helpful responses

Architecture:
  - Uses the google.genai SDK (async chat sessions)
  - Responses are strictly structured JSON via Pydantic response_schema
"""

import logging
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

from config import GOOGLE_API_KEY, MODEL, SYSTEM_PROMPT
from knowledge_base import format_solution

logger = logging.getLogger(__name__)

class TriageResult(BaseModel):
    """Strict schema for the AI's triage response."""
    message: str = Field(description="The natural language response to the user.")
    category: str | None = Field(None, description="Issue category (network, account, etc) or None if greeting.")
    urgency: str | None = Field(None, description="Urgency level (P1, P2, P3, P4) or None.")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0.")
    needs_more_info: bool = Field(..., description="True if the AI needs more info from the user.")
    is_self_resolvable: bool = Field(..., description="True if the issue has a known step-by-step solution.")
    should_create_ticket: bool = Field(..., description="True if a human agent is needed.")
    should_escalate: bool = Field(..., description="True if the issue is a P1, security risk, or urgent.")
    escalation_reason: str | None = Field(None, description="Why this was escalated, if applicable.")
    ticket_summary: str | None = Field(None, description="A 1-line summary for the ticket title.")
    suggested_solution_topic: str | None = Field(None, description="The knowledge base topic key, if self_resolvable.")

class TriageEngine:
    """Gemini-powered IT issue triage engine."""

    def __init__(self):
        """Initialize the Gemini client and session store."""
        if not GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY not set. Get a free key at https://aistudio.google.com/"
            )

        self._client = genai.Client(api_key=GOOGLE_API_KEY)
        self._model = MODEL
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
            max_output_tokens=1024,
            response_mime_type="application/json",
            response_schema=TriageResult,
        )
        self._sessions: dict[str, dict] = {}
        logger.info("TriageEngine initialized with model: %s", MODEL)

    def _get_session(self, session_id: str) -> dict:
        """Get or create a chat session."""
        self._cleanup_old_sessions()

        if session_id not in self._sessions:
            chat = self._client.aio.chats.create(
                model=self._model,
                config=self._config,
            )
            self._sessions[session_id] = {
                "chat": chat,
                "created_at": datetime.now(timezone.utc),
                "message_count": 0,
                "last_category": None,
                "last_urgency": None,
            }
            logger.info("New session created: %s", session_id)
        return self._sessions[session_id]

    def _cleanup_old_sessions(self):
        """Evict sessions older than 2 hours to prevent memory leaks."""
        max_age = timedelta(hours=2)
        now = datetime.now(timezone.utc)
        expired = [
            sid for sid, s in self._sessions.items()
            if now - s["created_at"] > max_age
        ]
        for sid in expired:
            del self._sessions[sid]
            logger.info("Session expired and cleaned up: %s", sid)

    async def process_message(self, session_id: str, message: str) -> dict:
        """Process a user message and return the triage result."""
        session = self._get_session(session_id)
        session["message_count"] += 1

        try:
            chat = session["chat"]
            response = await chat.send_message(message)
            
            # Use Pydantic parsed object directly
            result_obj = response.parsed
            if not result_obj:
                # Fallback to model_validate_json if parsed is not populated
                result_obj = TriageResult.model_validate_json(response.text)
                
            result = result_obj.model_dump()

            # Track classification state for the session
            if result.get("category"):
                session["last_category"] = result["category"]
            if result.get("urgency"):
                session["last_urgency"] = result["urgency"]

            # Enhance self-resolvable responses with knowledge base content
            if result.get("is_self_resolvable") and result.get("suggested_solution_topic"):
                solution_md = format_solution(result["suggested_solution_topic"])
                if solution_md and solution_md not in result.get("message", ""):
                    result["message"] += f"\n\n---\n\n{solution_md}"

            result["success"] = True
            return result

        except Exception as e:
            logger.error("Triage error for session %s: %s", session_id, str(e))
            return {
                "message": (
                    "I'm having a bit of trouble processing that right now. "
                    "Could you try rephrasing your issue? If the problem persists, "
                    "please contact the IT Service Desk directly."
                ),
                "category": None,
                "urgency": None,
                "confidence": 0.0,
                "needs_more_info": True,
                "is_self_resolvable": False,
                "should_create_ticket": False,
                "should_escalate": False,
                "escalation_reason": None,
                "ticket_summary": None,
                "suggested_solution_topic": None,
                "success": False,
                "error": str(e),
            }

    def get_session_info(self, session_id: str) -> dict | None:
        """Get metadata about a session."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            return {
                "session_id": session_id,
                "message_count": session["message_count"],
                "created_at": session["created_at"].isoformat(),
                "last_category": session["last_category"],
                "last_urgency": session["last_urgency"],
            }
        return None

    def reset_session(self, session_id: str) -> bool:
        """Delete a session and free its resources."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info("Session reset: %s", session_id)
            return True
        return False

    @property
    def active_sessions(self) -> int:
        """Number of currently active chat sessions."""
        return len(self._sessions)
