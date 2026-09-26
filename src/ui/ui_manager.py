"""
UI Manager for handling user interface components and styling.
"""
import html
import re
import streamlit as st
from typing import Dict, Any, List
from ..utils.metrics_calculator import calculate_role_specific_metrics

# List item prefixes the AI uses: "- ", "* ", "• " or "1. "
BULLET_PATTERN = re.compile(r'^([-*•]|\d+\.)\s+')

class UIManager:
    """Manages UI components and styling."""
    
    def __init__(self):
        """Initialize UI manager."""
        self._apply_custom_css()
    
    def _apply_custom_css(self):
        """Apply custom CSS styling."""
        st.markdown("""
            <style>
            /* Hide default Streamlit elements */
            #MainMenu, footer {visibility: hidden;}
            
            /* Base styles - Adobe-like theme */
            .stApp {
                background-color: #2D2D2D;
            }
            
            /* Top bar styling */
            header {
                background-color: #323232 !important;
                border-bottom: 1px solid #464646;
            }
            
            /* Global text color */
            .stApp, .stTextInput, .stSelectbox, div[data-baseweb="select"],
            .streamlit-expanderHeader, div[data-testid="stMarkdown"] {
                color: #E6E6E6 !important;
            }
            
            /* Sidebar styling - Adobe-like */
            section[data-testid="stSidebar"] {
                background-color: #2D2D2D;
                border-right: 1px solid #464646;
            }
            section[data-testid="stSidebar"] .stMarkdown {
                color: #E6E6E6;
            }
            section[data-testid="stSidebar"] .stMarkdown a {
                color: #4B9AD8;
            }
            
            /* Title and containers - Adobe-like */
            .main-title {
                text-align: center;
                color: #E6E6E6;
                padding: 1.5rem;
                border-radius: 6px;
                margin: 1rem 0;
                background: #1473E6;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            }
            .stat-box {
                background-color: #393939;
                padding: 1rem;
                border-radius: 6px;
                margin: 0.5rem 0;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                border-left: 4px solid #1473E6;
            }
            
            /* Interview messages - Adobe-like */
            .interview-message {
                padding: 1rem;
                border-radius: 6px;
                margin: 1rem 0;
                background-color: #393939;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                color: #E6E6E6;
            }
            .interviewer-message {
                border-left: 4px solid #1473E6;
            }
            .model-answer {
                border-left: 4px solid #4CAF50;
                background-color: #3a4a3a;
            }
            .assessment {
                border-left: 4px solid #FF9800;
                background-color: #4a423a;
            }
            .user-message {
                border-left: 4px solid #4B9AD8;
                background-color: #2D2D2D;
            }
            .user-message b, .user-message br, .user-message {
                color: #E6E6E6 !important;
            }
            
            /* Form elements - Adobe-like */
            .stTextInput > div > div > input {
                color: #E6E6E6 !important;
                background-color: #393939 !important;
                border: 1px solid #464646 !important;
                border-radius: 6px !important;
                padding: 0.5rem 1rem !important;
            }
            .stTextInput > div > div > input:focus {
                border-color: #1473E6 !important;
                box-shadow: 0 0 0 1px #1473E6 !important;
            }
            .stTextInput input::placeholder {
                color: #95A5A6 !important;
            }
            
            /* Button styling - Adobe-like: solid blue for the main action, outlined otherwise */
            .stButton > button, .stDownloadButton > button {
                width: 100%;
                padding: 0.5rem 1rem !important;
                border-radius: 6px !important;
                font-weight: 500 !important;
                white-space: nowrap;
                transition: all 0.2s ease !important;
            }
            button[data-testid="stBaseButton-primary"] {
                background: #1473E6 !important;
                color: white !important;
                border: none !important;
            }
            button[data-testid="stBaseButton-primary"]:hover {
                background: #0D66D0 !important;
                transform: translateY(-1px);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
            }
            button[data-testid="stBaseButton-secondary"] {
                background: transparent !important;
                color: #E6E6E6 !important;
                border: 1px solid #5A5A5A !important;
            }
            button[data-testid="stBaseButton-secondary"]:hover {
                border-color: #1473E6 !important;
                color: #4B9AD8 !important;
            }
            .stButton > button:disabled, .stDownloadButton > button:disabled {
                opacity: 0.4;
                pointer-events: none;
            }
            .interview-message code {
                background: #2D2D2D;
                color: #9CDCFE;
                padding: 1px 5px;
                border-radius: 4px;
            }

            /* Headers and labels - Adobe-like */
            h1, h2, h3, h4, h5, h6, label, .stMarkdown p {
                color: #E6E6E6 !important;
            }

            /* Keep alert text (success/warning/error) readable on the dark theme */
            div[data-testid="stAlert"] p, div[data-testid="stAlert"] div {
                color: #E6E6E6 !important;
            }

            /* Rich text inside message cards */
            .interview-message ul {
                margin: 4px 0 4px 18px;
                padding: 0;
            }
            .interview-message li {
                margin: 3px 0;
            }
            .section-heading {
                margin-top: 12px;
                font-weight: 600;
            }
            .card-label {
                display: block;
                margin-bottom: 6px;
            }
            .score-chip {
                display: inline-block;
                margin-left: 8px;
                padding: 1px 10px;
                border-radius: 10px;
                background: #1473E6;
                color: white;
                font-size: 0.85em;
                font-weight: 600;
            }
            
            /* Links */
            a {
                color: #4B9AD8 !important;
                text-decoration: none !important;
            }
            a:hover {
                text-decoration: underline !important;
            }
            </style>
        """, unsafe_allow_html=True)
    
    def render_title(self):
        """Render the main application title."""
        st.markdown('<h1 class="main-title">🎯 AI Interview Assistant</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;">Powered by Google Gemini 2.5 Flash</p>', unsafe_allow_html=True)
    
    def render_welcome_message(self, role: str, experience: str, interview_type: str, difficulty: str):
        """Render the welcome message when no interview has started."""
        st.markdown(f"""
            <div style="text-align: center; padding: 32px 40px; background-color: #393939; border-radius: 6px; margin: 20px 0; border: 1px solid #464646;">
                <h2 style="color: #E6E6E6;">👋 Welcome to Your Interview Session!</h2>
                <p style="color: #E6E6E6;">
                    <b>{role}</b> &nbsp;·&nbsp; {experience} &nbsp;·&nbsp; {interview_type} &nbsp;·&nbsp; {difficulty}
                </p>
                <p style="color: #B8B8B8; margin-top: 16px;">
                    1️⃣ Answer each question by typing or speaking &nbsp;&nbsp;
                    2️⃣ Get scored feedback on your answer &nbsp;&nbsp;
                    3️⃣ Compare with a model answer
                </p>
                <p style="color: #B8B8B8;">Change the setup in the sidebar, then press <b>Start Interview</b>.</p>
            </div>
        """, unsafe_allow_html=True)

    def render_session_stats(self, stats: Dict[str, Any]):
        """Render session statistics in the sidebar."""
        metrics = stats.get('role_specific_metrics', {})
        st.markdown(f"""
            <div class="stat-box">
                <b>Questions Answered:</b> {stats['total_questions']}<br>
                <b>Technical:</b> {metrics.get('domain_knowledge', 0):.1f}/10<br>
                <b>Communication:</b> {metrics.get('methodology_understanding', 0):.1f}/10<br>
                <b>Experience Match:</b> {metrics.get('practical_experience', 0):.1f}/10<br>
                <b>Overall Score:</b> {metrics.get('overall_score', 0):.1f}/10
            </div>
        """, unsafe_allow_html=True)

    def _format_rich_text(self, content: str) -> str:
        """
        Format AI-generated text into consistent HTML with headings and bullet points.
        Works regardless of how the AI formats the response. Text is HTML-escaped
        first, so answers mentioning e.g. List<WebElement> display correctly.
        """
        html_lines = []

        for line in content.split('\n'):
            stripped = html.escape(line.strip())
            if not stripped:
                continue

            # Markdown bold (**text**) and `code`, then drop stray heading markers
            stripped = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', stripped)
            stripped = re.sub(r'`([^`]+)`', r'<code>\1</code>', stripped)
            stripped = re.sub(r'^#+\s*', '', stripped)

            # Section headers (e.g. "Technical Assessment:", "Key Strengths:")
            if re.match(r'^(<b>)?[A-Z][^:]{0,60}:(</b>)?$', stripped):
                heading = re.sub(r'</?b>', '', stripped)
                html_lines.append(f'<div class="section-heading">{heading}</div>')

            # Bullet points: "- ", "* ", "• " or "1. "
            elif BULLET_PATTERN.match(stripped):
                html_lines.append(f'<li>{BULLET_PATTERN.sub("", stripped)}</li>')

            # Lines that look like inline bullets (e.g. "Knowledge Depth: 7.5 - explanation")
            elif re.match(r'^[A-Za-z ]+:\s*\d', stripped) and ' - ' in stripped:
                html_lines.append(f'<li>{stripped}</li>')

            else:
                html_lines.append(f'<div>{stripped}</div>')

        # Wrap consecutive <li> items in <ul>
        result = '\n'.join(html_lines)
        return re.sub(r'(<li>.*?</li>\n?)+', lambda m: f'<ul>{m.group()}</ul>', result)

    def _render_card(self, css_class: str, label: str, body_html: str):
        """Render one conversation card."""
        st.markdown(
            f'<div class="interview-message {css_class}">'
            f'<b class="card-label">{label}</b>{body_html}'
            f'</div>',
            unsafe_allow_html=True
        )

    def _render_model_answer(self, expected_answer: str):
        """Render the model answer for a question that has been answered."""
        if expected_answer:
            self._render_card("model-answer", "✓ Model Answer", self._format_rich_text(expected_answer))

    def render_conversation(self, messages: List[Dict[str, Any]]):
        """
        Render the entire conversation.

        Each exchange reads Question -> Your Response -> Assessment -> Model Answer;
        the model answer is only revealed once the question has been answered.
        """
        question_number = 0
        pending_model_answer = ""

        for i, message in enumerate(messages):
            content = message["content"]
            msg_type = message.get("type", "question")

            if message["role"] == "user":
                self._render_card("user-message", "💬 Your Response",
                                  html.escape(content).replace("\n", "<br>"))

            elif msg_type == "question":
                # Model answer of an answered question whose assessment never arrived
                self._render_model_answer(pending_model_answer)
                question_number += 1
                self._render_card("interviewer-message", f"❓ Question {question_number}",
                                  self._format_rich_text(content.get("question", "Error: Question text missing.")))

                is_answered = i + 1 < len(messages) and messages[i + 1]["role"] == "user"
                pending_model_answer = content.get("expected_answer", "") if is_answered else ""

            elif msg_type == "assessment":
                overall = calculate_role_specific_metrics("", "", [message])["overall_score"]
                chip = f'<span class="score-chip">{overall:.1f}/10</span>' if overall else ""
                self._render_card("assessment", f"📊 Assessment{chip}", self._format_rich_text(content))
                self._render_model_answer(pending_model_answer)
                pending_model_answer = ""

        self._render_model_answer(pending_model_answer)