import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from utils import verbose_print

class SessionLogger:
    """Comprehensive session logging for voice markdown editing."""
    
    def __init__(self):
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / f"session_{self.session_id}.txt"
        self.json_file = self.log_dir / f"session_{self.session_id}.json"
        
        self.session_data = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "events": []
        }
        
        self.log_session_start()
    
    def log_session_start(self):
        """Log session start information."""
        self.log_event("SESSION_START", {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id
        })
        
        verbose_print(f"Session logging started: {self.log_file}")
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event to both text and JSON logs."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Text log entry
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {event_type}: {json.dumps(data, indent=2)}\n\n")
        
        # JSON log entry
        event = {
            "timestamp": timestamp,
            "event_type": event_type,
            "data": data
        }
        self.session_data["events"].append(event)
        
        # Write updated JSON
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        
        verbose_print(f"Logged {event_type} event")
    
    def log_audio_capture(self, duration: float, success: bool, error: Optional[str] = None):
        """Log audio capture attempt."""
        self.log_event("AUDIO_CAPTURE", {
            "duration_seconds": duration,
            "success": success,
            "error": error
        })
    
    def log_transcription(self, transcript: str, model: str, success: bool, 
                         processing_time: Optional[float] = None, error: Optional[str] = None):
        """Log transcription attempt."""
        self.log_event("TRANSCRIPTION", {
            "transcript": transcript if success else None,
            "transcript_length": len(transcript) if transcript else 0,
            "whisper_model": model,
            "success": success,
            "processing_time_seconds": processing_time,
            "error": error
        })
    
    def log_gpt_request(self, instruction: str, filename: str, success: bool,
                       input_length: int = 0, output_length: int = 0, 
                       processing_time: Optional[float] = None, error: Optional[str] = None):
        """Log GPT-4 API request."""
        self.log_event("GPT_REQUEST", {
            "instruction": instruction,
            "filename": filename,
            "input_content_length": input_length,
            "output_content_length": output_length,
            "success": success,
            "processing_time_seconds": processing_time,
            "error": error
        })
    
    def log_diff_analysis(self, additions: int, deletions: int, filename: str):
        """Log diff analysis results."""
        self.log_event("DIFF_ANALYSIS", {
            "filename": filename,
            "additions": additions,
            "deletions": deletions,
            "total_changes": additions + deletions
        })
    
    def log_user_decision(self, decision: str, changes_applied: bool, filename: str,
                         backup_created: Optional[str] = None):
        """Log user's approval/rejection decision."""
        self.log_event("USER_DECISION", {
            "decision": decision,  # "accept", "reject", "cancel"
            "changes_applied": changes_applied,
            "filename": filename,
            "backup_file": backup_created
        })
    
    def log_file_operation(self, operation: str, filename: str, success: bool,
                          backup_created: Optional[str] = None, error: Optional[str] = None):
        """Log file read/write operations."""
        self.log_event("FILE_OPERATION", {
            "operation": operation,  # "read", "write", "backup"
            "filename": filename,
            "success": success,
            "backup_created": backup_created,
            "error": error
        })
    
    def log_session_end(self, success: bool, summary: Optional[Dict[str, Any]] = None):
        """Log session completion."""
        self.session_data["end_time"] = datetime.now().isoformat()
        self.session_data["success"] = success
        if summary:
            self.session_data["summary"] = summary
        
        self.log_event("SESSION_END", {
            "success": success,
            "duration_seconds": self._calculate_session_duration(),
            "summary": summary or {}
        })
        
        verbose_print(f"Session logging completed: {self.log_file}")
    
    def _calculate_session_duration(self) -> float:
        """Calculate total session duration."""
        start = datetime.fromisoformat(self.session_data["start_time"])
        end = datetime.now()
        return (end - start).total_seconds()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Generate a summary of the current session."""
        events = self.session_data["events"]
        
        summary = {
            "total_events": len(events),
            "transcriptions": len([e for e in events if e["event_type"] == "TRANSCRIPTION"]),
            "gpt_requests": len([e for e in events if e["event_type"] == "GPT_REQUEST"]),
            "files_modified": len([e for e in events if e["event_type"] == "USER_DECISION" and e["data"]["changes_applied"]]),
            "session_duration": self._calculate_session_duration()
        }
        
        return summary

# Global session logger instance
_session_logger: Optional[SessionLogger] = None

def get_session_logger() -> SessionLogger:
    """Get or create the global session logger."""
    global _session_logger
    if _session_logger is None:
        _session_logger = SessionLogger()
    return _session_logger

def end_session(success: bool = True):
    """End the current session and finalize logs."""
    global _session_logger
    if _session_logger:
        summary = _session_logger.get_session_summary()
        _session_logger.log_session_end(success, summary)
        _session_logger = None