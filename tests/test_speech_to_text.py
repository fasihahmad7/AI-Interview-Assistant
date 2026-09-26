"""
Unit tests for speech_to_text (microphone and Google recognizer are mocked).
Run with: pytest tests/
"""
from unittest.mock import MagicMock, patch

import speech_recognition as sr

from src.utils.helpers import speech_to_text


def run_with_phrases(phrases, **kwargs):
    """Simulate a speaker saying `phrases` (one per listen call) and then going quiet."""
    recognizer = MagicMock()
    audios = [MagicMock(name=f"audio_{i}") for i in range(len(phrases))]
    recognizer.listen.side_effect = audios + [sr.WaitTimeoutError()]

    transcripts = dict(zip(audios, phrases))

    def recognize(audio):
        text = transcripts[audio]
        if text is None:
            raise sr.UnknownValueError()
        return text

    recognizer.recognize_google.side_effect = recognize

    with patch("src.utils.helpers.sr.Recognizer", return_value=recognizer), \
         patch("src.utils.helpers.sr.Microphone"):
        return speech_to_text(**kwargs), recognizer


def test_joins_phrases_across_pauses():
    text, _ = run_with_phrases(["I would start with", "a risk based test plan"])
    assert text == "I would start with a risk based test plan"


def test_skips_unintelligible_phrases():
    text, _ = run_with_phrases(["first point", None, "second point"])
    assert text == "first point second point"


def test_returns_none_when_nothing_said():
    text, _ = run_with_phrases([])
    assert text is None


def test_returns_none_when_nothing_understood():
    text, _ = run_with_phrases([None, None])
    assert text is None


def test_uses_start_timeout_first_then_end_silence():
    _, recognizer = run_with_phrases(["one", "two"], start_timeout=10, end_silence=3)
    timeouts = [call.kwargs["timeout"] for call in recognizer.listen.call_args_list]
    assert timeouts == [10, 3, 3]


def test_on_update_receives_only_non_empty_text():
    updates = []
    run_with_phrases(["hello there", "general"], on_update=updates.append)
    assert all(updates)


def test_microphone_error_returns_none():
    with patch("src.utils.helpers.sr.Microphone", side_effect=OSError("no mic")):
        assert speech_to_text() is None
