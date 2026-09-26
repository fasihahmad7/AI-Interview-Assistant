"""
Session Manager for handling Streamlit session state operations.
"""
import streamlit as st
import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..utils.config import ERROR_MESSAGES

class SessionManager:
    """Manages session state and user interactions."""
    
    def __init__(self):
        """Initialize session manager and set up session state."""
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize all session state variables."""
        defaults = {
            'messages': [],
            'request_count': 0,
            'last_request_time': time.time(),
            'interview_history': [],
            'session_stats': {
                'total_questions': 0,
                'technical_score': 0,
                'communication_score': 0,
                'role_specific_metrics': {}
            },
            'interview_started': False,
            'is_processing': False,
            'current_response': "",
            'question_count': 0  # Track number of questions for skill rotation
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def check_rate_limit(self) -> tuple[bool, float]:
        """Check if the request should be rate limited."""
        current_time = time.time()
        time_diff = current_time - st.session_state.last_request_time
        
        if time_diff < 1.0:  # Minimum 1 second between requests
            return False, 1.0 - time_diff
            
        st.session_state.last_request_time = current_time
        st.session_state.request_count += 1
        return True, 0.0
    
    def reset_interview(self):
        """Reset session state for a new interview."""
        st.session_state.messages = []
        st.session_state.session_stats = {
            'total_questions': 0,
            'technical_score': 0,
            'communication_score': 0,
            'role_specific_metrics': {}
        }
        st.session_state.interview_started = False
        st.session_state.is_processing = False
        st.session_state.current_response = ""
        st.session_state.question_count = 0
    
    def add_message(self, role: str, content: Any, message_type: str = "message"):
        """Add a message to the conversation history."""
        message = {
            "role": role,
            "type": message_type,
            "content": content
        }
        st.session_state.messages.append(message)
    
    def add_interview_history(self, role: str, experience: str, interview_type: str,
                            question: str, answer: str, feedback: str, model_answer: str = ""):
        """Add an entry to the interview history."""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "experience": experience,
            "interview_type": interview_type,
            "question": question,
            "model_answer": model_answer,
            "answer": answer,
            "feedback": feedback
        }
        st.session_state.interview_history.append(history_entry)
    
    def update_session_stats(self, role_metrics: Dict[str, float]):
        """Update session statistics with new metrics."""
        st.session_state.session_stats['total_questions'] += 1
        st.session_state.session_stats['role_specific_metrics'] = role_metrics
    
    def export_history(self) -> str:
        """Export the interview history and stats as JSON with full details."""
        # Build comprehensive history with all details
        detailed_history = []
        
        for i, entry in enumerate(st.session_state.interview_history, 1):
            detailed_entry = {
                "session_number": i,
                "timestamp": entry.get("timestamp"),
                "role": entry.get("role"),
                "experience_level": entry.get("experience"),
                "interview_type": entry.get("interview_type"),
                "question": entry.get("question"),
                "model_answer": entry.get("model_answer", "N/A"),
                "user_answer": entry.get("answer"),
                "assessment": entry.get("feedback"),
                "notes": entry.get("notes", "")
            }
            detailed_history.append(detailed_entry)
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_sessions': len(detailed_history),
            'session_statistics': st.session_state.session_stats,
            'interview_sessions': detailed_history
        }
        
        return json.dumps(export_data, indent=2)
    
    def validate_user_input(self, user_input: str) -> tuple[bool, Optional[str]]:
        """Validate user input before processing."""
        if not user_input:
            return False, ERROR_MESSAGES['invalid_input']
        
        if len(user_input.strip()) < 10:
            return False, ERROR_MESSAGES['invalid_input']
        
        return True, None
    
    def set_processing_state(self, is_processing: bool, current_response: str = ""):
        """Set the processing state and current response."""
        st.session_state.is_processing = is_processing
        st.session_state.current_response = current_response
    
    def start_interview(self):
        """Mark the interview as started."""
        st.session_state.interview_started = True
    
    def get_last_question(self) -> Dict[str, str]:
        """Get the last question from the message history."""
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "assistant" and msg.get("type") == "question":
                return msg["content"]
        return {"question": "Unknown Question", "expected_answer": ""}
    
    def should_process_input(self, user_input: str) -> bool:
        """Check if user input should be processed."""
        return bool(
            user_input and
            user_input != st.session_state.current_response and
            not st.session_state.is_processing
        )