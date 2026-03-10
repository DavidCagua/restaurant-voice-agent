"""
Observability module for structured logging and performance tracking.

Provides JSON-structured logs with timing measurements for STT, reasoning,
tool calls, and TTS stages. Sensitive user content (transcripts) are
excluded by default unless DEBUG mode is enabled.
"""

import json
import logging
import os
import time
import uuid
from contextlib import contextmanager
from typing import Optional, Dict, Any
from datetime import datetime

# Configure structured JSON logging
class StructuredJSONFormatter(logging.Formatter):
    """Formatter that outputs logs as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        # Add structured fields if present
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "turn_id"):
            log_data["turn_id"] = record.turn_id
        if hasattr(record, "tool_name"):
            log_data["tool_name"] = record.tool_name
        if hasattr(record, "latency_ms"):
            log_data["latency_ms"] = record.latency_ms
        if hasattr(record, "model"):
            log_data["model"] = record.model
        if hasattr(record, "stt_provider"):
            log_data["stt_provider"] = record.stt_provider
        if hasattr(record, "tts_provider"):
            log_data["tts_provider"] = record.tts_provider
        if hasattr(record, "stage"):
            log_data["stage"] = record.stage
        if hasattr(record, "event_type"):
            log_data["event_type"] = record.event_type
        if hasattr(record, "transcript_delay_s"):
            log_data["transcript_delay_s"] = round(record.transcript_delay_s, 4)
        
        # Only include transcript in DEBUG mode
        if hasattr(record, "transcript") and os.getenv("DEBUG", "").lower() == "true":
            log_data["transcript"] = record.transcript
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


# Set up logger
_logger = logging.getLogger("restaurant_agent")
_logger.setLevel(logging.INFO)

# Remove existing handlers
_logger.handlers.clear()

# Add console handler with JSON formatter
_handler = logging.StreamHandler()
_handler.setFormatter(StructuredJSONFormatter())
_logger.addHandler(_handler)

# Enable DEBUG logging if flag is set
if os.getenv("DEBUG", "").lower() == "true":
    _logger.setLevel(logging.DEBUG)


class ObservabilityContext:
    """Context manager for tracking observability state across agent lifecycle."""
    
    def __init__(self, session_id: str, user_id: Optional[str] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.turn_id: Optional[str] = None
        self.timings: Dict[str, float] = {}
        self.stt_provider = "deepgram"
        self.tts_provider = "elevenlabs"
        self.model = "gpt-4o-mini"
        # Set when user turn is committed; cleared when TTS starts (for turn E2E timing).
        self._turn_start_time: Optional[float] = None
    
    def log_event(
        self,
        event_type: str,
        stage: str,
        latency_ms: Optional[float] = None,
        tool_name: Optional[str] = None,
        transcript: Optional[str] = None,
        **kwargs
    ):
        """Log a structured event."""
        extra = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "turn_id": self.turn_id,
            "event_type": event_type,
            "stage": stage,
            "model": self.model,
            "stt_provider": self.stt_provider,
            "tts_provider": self.tts_provider,
        }
        
        if latency_ms is not None:
            extra["latency_ms"] = round(latency_ms, 2)
        
        if tool_name:
            extra["tool_name"] = tool_name
        
        if transcript and os.getenv("DEBUG", "").lower() == "true":
            extra["transcript"] = transcript
        if kwargs.get("transcript_delay_s") is not None:
            extra["transcript_delay_s"] = round(kwargs["transcript_delay_s"], 4)
        
        # Add any additional kwargs (avoid overwriting transcript_delay_s if already set)
        extra.update({k: v for k, v in kwargs.items() if k != "transcript_delay_s"})
        
        _logger.info(f"{event_type}: {stage}", extra=extra)
    
    @contextmanager
    def time_stage(self, stage: str, **kwargs):
        """Context manager for timing a stage."""
        start_time = time.time()
        try:
            yield
        finally:
            latency_ms = (time.time() - start_time) * 1000
            self.timings[stage] = latency_ms
            self.log_event("timing", stage, latency_ms=latency_ms, **kwargs)
    
    def start_turn(self, turn_id: Optional[str] = None):
        """Start a new conversation turn."""
        self.turn_id = turn_id or str(uuid.uuid4())
    
    def log_stt_receive(
        self,
        transcript: Optional[str] = None,
        transcript_delay_s: Optional[float] = None,
    ):
        """Log STT receive event (final user transcript). With DEBUG=true, transcript text is included."""
        self.log_event(
            "stt_receive",
            "stt",
            transcript=transcript,
            transcript_delay_s=transcript_delay_s,
        )
    
    def log_stt_start(self):
        """Log STT start event."""
        self.log_event("stt_start", "stt")
    
    def log_reasoning_start(self):
        """Log reasoning start event."""
        self.log_event("reasoning_start", "reasoning")
    
    def log_reasoning_end(self, latency_ms: float):
        """Log reasoning end event."""
        self.log_event("reasoning_end", "reasoning", latency_ms=latency_ms)
    
    def log_tool_call_start(self, tool_name: str):
        """Log tool call start event."""
        self.log_event("tool_call_start", "tool_call", tool_name=tool_name)
    
    def log_tool_call_end(self, tool_name: str, latency_ms: float):
        """Log tool call end event."""
        self.log_event("tool_call_end", "tool_call", tool_name=tool_name, latency_ms=latency_ms)
    
    def log_tts_start(self):
        """Log TTS start event."""
        self.log_event("tts_start", "tts")
    
    def log_tts_end(self, latency_ms: float):
        """Log TTS end event (time from TTS start to stream finished)."""
        self.log_event("tts_end", "tts", latency_ms=latency_ms)

    def set_turn_start_time(self, t: float) -> None:
        """Record when the user turn was committed (for turn E2E timing)."""
        self._turn_start_time = t

    def log_turn_e2e_if_set(self, tts_start_time: float) -> None:
        """If a turn start was recorded, log turn E2E (user transcript -> TTS start) and clear it."""
        if self._turn_start_time is None:
            return
        e2e_ms = (tts_start_time - self._turn_start_time) * 1000
        self.log_event("turn_e2e", "turn", latency_ms=round(e2e_ms, 2))
        self._turn_start_time = None


def get_observability_context(session_id: str, user_id: Optional[str] = None) -> ObservabilityContext:
    """Get or create an observability context for a session."""
    return ObservabilityContext(session_id, user_id)
