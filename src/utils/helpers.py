"""
Common utility functions for the AI Interview Assistant.
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from concurrent.futures import Future, ThreadPoolExecutor
import json
import logging
import time
import speech_recognition as sr

logger = logging.getLogger(__name__)

def _transcribe_phrase(recognizer: sr.Recognizer, audio: sr.AudioData) -> str:
    """Transcribe one recorded phrase; returns an empty string if it can't be understood."""
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        logger.error(f"Speech recognition service unavailable: {e}")
        return ""

def _join_transcripts(chunks: List[Future]) -> str:
    """Join the transcripts of the phrases that have finished transcribing so far."""
    return " ".join(f.result() for f in chunks if f.done() and f.result())

def speech_to_text(on_update: Optional[Callable[[str], None]] = None,
                   start_timeout: float = 10,
                   end_silence: float = 3,
                   max_duration: float = 180) -> Optional[str]:
    """
    Record a spoken answer from the microphone and convert it to text.

    Listens phrase by phrase so natural pauses don't cut the answer short.
    Each phrase is transcribed in the background while listening continues,
    and recording stops once the speaker has been silent for `end_silence` seconds.

    Args:
        on_update: Called with the (non-empty) transcript so far after each phrase
        start_timeout: Seconds to wait for the speaker to start talking
        end_silence: Seconds of silence (after a phrase ends) that finish the answer
        max_duration: Hard cap on total recording time in seconds

    Returns:
        The recognized text, or None if nothing could be recognized.
    """
    recognizer = sr.Recognizer()
    # A phrase ends after this much silence; longer than the 0.8s default
    # so a short pause mid-sentence doesn't split words
    recognizer.pause_threshold = 1.2
    chunks: List[Future] = []

    try:
        with sr.Microphone() as source, ThreadPoolExecutor(max_workers=3) as pool:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            started = time.monotonic()

            while time.monotonic() - started < max_duration:
                try:
                    audio = recognizer.listen(
                        source,
                        timeout=end_silence if chunks else start_timeout,
                        phrase_time_limit=30
                    )
                except sr.WaitTimeoutError:
                    break  # Speaker has stopped talking

                chunks.append(pool.submit(_transcribe_phrase, recognizer, audio))
                transcript_so_far = _join_transcripts(chunks)
                if on_update and transcript_so_far:
                    on_update(transcript_so_far)

            text = " ".join(t for t in (f.result() for f in chunks) if t)

    except Exception as e:
        logger.error(f"Error accessing microphone: {e}")
        return None

    return text or None

def calculate_average_metrics(metrics_list: List[Dict[str, float]]) -> Dict[str, float]:
    """Calculate average values for a list of metrics."""
    if not metrics_list:
        return {}
        
    result = {}
    for key in metrics_list[0].keys():
        values = [m[key] for m in metrics_list if key in m]
        result[key] = sum(values) / len(values) if values else 0
    return result

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable string."""
    duration = timedelta(seconds=seconds)
    if duration.days > 0:
        return f"{duration.days}d {duration.seconds//3600}h"
    elif duration.seconds >= 3600:
        return f"{duration.seconds//3600}h {(duration.seconds//60)%60}m"
    else:
        return f"{duration.seconds//60}m {duration.seconds%60}s"

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string with a default value if parsing fails."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp in consistent way across the application."""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def calculate_progress(current: float, target: float) -> Dict[str, Any]:
    """Calculate progress towards a target value."""
    progress = (current / target) if target else 0
    return {
        'percentage': min(progress * 100, 100),
        'status': 'completed' if progress >= 1 else 'in_progress',
        'remaining': max(target - current, 0)
    }

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length while preserving words."""
    if len(text) <= max_length:
        return text
        
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return f"{truncated}..."

def parse_duration_string(duration_str: str) -> int:
    """Parse duration string (e.g., '1h 30m') to seconds."""
    total_seconds = 0
    parts = duration_str.lower().split()
    
    for part in parts:
        if part.endswith('h'):
            total_seconds += int(part[:-1]) * 3600
        elif part.endswith('m'):
            total_seconds += int(part[:-1]) * 60
        elif part.endswith('s'):
            total_seconds += int(part[:-1])
            
    return total_seconds

def get_trend_indicator(current: float, previous: float) -> str:
    """Get trend indicator (↑, ↓, or →) based on value comparison."""
    if current > previous:
        return "↑"
    elif current < previous:
        return "↓"
    return "→"
