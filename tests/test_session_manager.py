"""
Unit tests for SessionManager.
Run with: pytest tests/
"""
import pytest
from unittest.mock import patch


class MockSessionState(dict):
    """Dict-backed mock for st.session_state."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value


@pytest.fixture
def mock_state():
    return MockSessionState()


@pytest.fixture
def manager(mock_state):
    with patch("streamlit.session_state", mock_state):
        from src.services.session_manager import SessionManager
        return SessionManager(), mock_state


class TestInit:
    def test_all_keys_initialized(self, manager):
        _, state = manager
        for key in ["messages", "request_count", "interview_history",
                    "session_stats", "interview_started", "is_processing",
                    "current_response", "question_count"]:
            assert key in state

    def test_question_count_starts_at_zero(self, manager):
        _, state = manager
        assert state["question_count"] == 0


class TestResetInterview:
    def test_clears_messages(self, manager):
        mgr, state = manager
        state["messages"] = [{"role": "user", "content": "hi"}]
        with patch("streamlit.session_state", state):
            mgr.reset_interview()
        assert state["messages"] == []

    def test_resets_question_count(self, manager):
        mgr, state = manager
        state["question_count"] = 7
        with patch("streamlit.session_state", state):
            mgr.reset_interview()
        assert state["question_count"] == 0

    def test_resets_stats(self, manager):
        mgr, state = manager
        state["session_stats"] = {"total_questions": 10, "technical_score": 8,
                                   "communication_score": 7, "role_specific_metrics": {}}
        with patch("streamlit.session_state", state):
            mgr.reset_interview()
        assert state["session_stats"]["total_questions"] == 0

    def test_sets_interview_started_false(self, manager):
        mgr, state = manager
        state["interview_started"] = True
        with patch("streamlit.session_state", state):
            mgr.reset_interview()
        assert state["interview_started"] is False


class TestValidateUserInput:
    def test_empty_is_invalid(self, manager):
        mgr, _ = manager
        valid, msg = mgr.validate_user_input("")
        assert valid is False and msg

    def test_too_short_is_invalid(self, manager):
        mgr, _ = manager
        valid, _ = mgr.validate_user_input("ok")
        assert valid is False

    def test_sufficient_length_is_valid(self, manager):
        mgr, _ = manager
        valid, msg = mgr.validate_user_input("This is a detailed enough answer.")
        assert valid is True and msg is None


class TestShouldProcessInput:
    def test_false_when_processing(self, manager):
        mgr, state = manager
        state["is_processing"] = True
        state["current_response"] = ""
        with patch("streamlit.session_state", state):
            assert mgr.should_process_input("answer") is False

    def test_false_for_duplicate(self, manager):
        mgr, state = manager
        state["is_processing"] = False
        state["current_response"] = "same"
        with patch("streamlit.session_state", state):
            assert mgr.should_process_input("same") is False

    def test_true_for_new_input(self, manager):
        mgr, state = manager
        state["is_processing"] = False
        state["current_response"] = ""
        with patch("streamlit.session_state", state):
            assert mgr.should_process_input("new answer") is True


class TestAddMessage:
    def test_appends_message(self, manager):
        mgr, state = manager
        with patch("streamlit.session_state", state):
            mgr.add_message("user", "hello")
        assert len(state["messages"]) == 1
        assert state["messages"][0]["role"] == "user"

    def test_default_type_is_message(self, manager):
        mgr, state = manager
        with patch("streamlit.session_state", state):
            mgr.add_message("assistant", "hi")
        assert state["messages"][0]["type"] == "message"

    def test_custom_type_stored(self, manager):
        mgr, state = manager
        with patch("streamlit.session_state", state):
            mgr.add_message("assistant", {"question": "Q?"}, message_type="question")
        assert state["messages"][0]["type"] == "question"
