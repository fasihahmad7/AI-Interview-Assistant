import streamlit as st
from .custom_text_input import custom_text_area
from typing import Optional
from ..utils.helpers import speech_to_text

class AudioInput:
    def __init__(self):
        if 'voice_draft' not in st.session_state:
            # Transcribed answer awaiting review: {"question": int, "text": str, "take": int}
            st.session_state.voice_draft = None
        if 'voice_take' not in st.session_state:
            st.session_state.voice_take = 0

    def get_user_input(self, placeholder: str = "Enter your answer") -> Optional[str]:
        """
        Get user input through either text or speech.

        Spoken answers are not submitted straight away: after recording stops,
        the transcript is shown for review and only returned once confirmed.

        Args:
            placeholder: Placeholder text for the text input field

        Returns:
            str: The user's input text, either typed or a confirmed transcript
        """
        question_number = st.session_state.session_stats['total_questions']
        draft = st.session_state.voice_draft

        # Drop a draft left over from a question that has already been answered
        if draft and draft["question"] != question_number:
            st.session_state.voice_draft = draft = None

        if draft:
            return self._render_voice_review(draft)

        # Use a unique key for the text area to prevent pre-filling
        text_input = custom_text_area(
            "Your Answer",
            placeholder=placeholder,
            height=150,
            allow_paste=False,
            key=f"user_input_{question_number}"
        )

        col1, col2, _ = st.columns([1, 1, 2])
        with col1:
            submit = st.button("✅ Submit answer", type="primary", use_container_width=True)
        with col2:
            use_mic = st.button(
                "🎤 Answer by voice",
                use_container_width=True,
                help="Record your answer using your microphone"
            )

        if use_mic or st.session_state.pop('voice_record_again', False):
            self._record_answer(question_number)
            return None

        if submit:
            if text_input and text_input.strip():
                return text_input
            st.warning("Type your answer first, or use the microphone.")

        return None

    def _record_answer(self, question_number: int):
        """Record a spoken answer, then store it as a draft for review."""
        with st.status("🎤 Listening... speak your answer", expanded=True) as status:
            st.caption("Pause for about 3 seconds when you're done and I'll stop listening.")
            live_transcript = st.empty()

            def show_transcript(text: str):
                live_transcript.markdown(f"*{text}*")

            speech_text = speech_to_text(on_update=show_transcript)

            if not speech_text:
                status.update(label="Couldn't hear an answer", state="error")
                st.error("Could not recognize speech. Please try again or type your answer.")
                return

            status.update(label="✅ Stopped listening", state="complete")

        st.session_state.voice_take += 1
        st.session_state.voice_draft = {
            "question": question_number,
            "text": speech_text,
            "take": st.session_state.voice_take
        }
        st.rerun()

    def _render_voice_review(self, draft: dict) -> Optional[str]:
        """Show the transcribed answer and let the user submit, re-record or discard it."""
        st.success("🎤 I've stopped listening. Here's what I heard - "
                   "fix anything that was misheard, then submit it for evaluation.")

        reviewed_text = st.text_area(
            "Your spoken answer",
            value=draft["text"],
            height=150,
            key=f"voice_review_{draft['take']}"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            submit = st.button("✅ Submit for evaluation", type="primary", use_container_width=True)
        with col2:
            record_again = st.button("🔁 Record again", use_container_width=True)
        with col3:
            type_instead = st.button("⌨️ Type instead", use_container_width=True)

        if record_again or type_instead:
            st.session_state.voice_draft = None
            st.session_state.voice_record_again = record_again
            st.rerun()

        # The draft is kept until the answer is accepted (the question number
        # moves on), so it isn't lost if validation rejects it
        if submit:
            return (reviewed_text or "").strip() or None

        return None
