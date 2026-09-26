"""
AI Interview Assistant - Main Application
A refactored, modular interview preparation tool powered by Google's Gemini AI.
"""
import streamlit as st
import os
from dotenv import load_dotenv

# Import our modular components
from src.services.ai_service import AIService
from src.services.session_manager import SessionManager
from src.controllers.interview_controller import InterviewController
from src.ui.ui_manager import UIManager
from src.components.audio_input import AudioInput
from src.utils.logging_config import setup_logging, log_user_interaction, log_error
from src.utils.config import (
    INTERVIEW_TYPES,
    DIFFICULTY_LEVELS,
    JOB_ROLES,
    EXPERIENCE_RANGES
)

# --- Configuration ---
load_dotenv()
logger = setup_logging("INFO")

# Configure Streamlit page
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_services():
    """Initialize all services and check API configuration."""
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        st.error("⚠️ API Key not found! Please follow these steps:")
        st.markdown("""
        1. Create a `.env` file in the project root
        2. Add your Google API key: `GOOGLE_API_KEY=your_key_here`
        3. Restart the application
        """)
        st.stop()
    
    try:
        # Initialize services
        ai_service = AIService(api_key)
        session_manager = SessionManager()
        interview_controller = InterviewController(ai_service, session_manager)
        ui_manager = UIManager()
        
        logger.info("All services initialized successfully")
        return ai_service, session_manager, interview_controller, ui_manager
        
    except Exception as e:
        log_error(e, "Service initialization")
        st.error(f"⚠️ Error initializing services: {str(e)}")
        st.stop()

def render_sidebar(session_manager: SessionManager, interview_controller: InterviewController, ui_manager: UIManager):
    """Render the sidebar with controls and statistics."""
    with st.sidebar:
        st.header("🔧 Interview Setup")
        
        # Interview configuration
        selected_role = st.selectbox("Choose Your Role", JOB_ROLES, 
                                   help="Select the position you're interviewing for")
        experience_level = st.selectbox("Your Experience Level", EXPERIENCE_RANGES, 
                                      help="Select your years of experience")
        interview_type = st.selectbox("Interview Type", INTERVIEW_TYPES, 
                                    help="Select the type of interview questions")
        difficulty_level = st.selectbox("Question Difficulty", DIFFICULTY_LEVELS, 
                                      help="Select the difficulty level of questions")
        
        # Custom context/skills field
        st.markdown("### 🎯 Focus Areas (Optional)")
        custom_context = st.text_area(
            "Specific Skills or Topics",
            placeholder="e.g., Selenium, API testing with Postman, JMeter, SQL",
            height=100,
            help="Add any specific skills, technologies, or topics you want to practice"
        )

        # Interview controls
        st.markdown("### 📊 Interview Controls")
        if st.button("🔄 New Interview", use_container_width=True):
            log_user_interaction("new_interview_started", {
                "role": selected_role,
                "experience": experience_level,
                "type": interview_type
            })
            session_manager.reset_interview()
            st.rerun()

        st.download_button(
            "💾 Export History",
            session_manager.export_history(),
            "interview_history.json",
            "application/json",
            use_container_width=True,
            disabled=not st.session_state.interview_history
        )

        # Display session statistics
        st.markdown("### 📈 Session Progress")
        ui_manager.render_session_stats(st.session_state.session_stats)
        
        return selected_role, experience_level, interview_type, difficulty_level, custom_context

def main():
    """Main application function."""
    try:
        # Initialize services
        ai_service, session_manager, interview_controller, ui_manager = initialize_services()
        
        # Render UI title
        ui_manager.render_title()
        
        # Render sidebar and get configuration
        selected_role, experience_level, interview_type, difficulty_level, custom_context = render_sidebar(
            session_manager, interview_controller, ui_manager
        )

        # Main content area
        if not st.session_state.messages:
            # Show welcome message
            ui_manager.render_welcome_message(selected_role, experience_level, interview_type, difficulty_level)
            
            # Start interview button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🎯 Start Interview", use_container_width=True, type="primary"):
                    with st.spinner("🤖 Preparing your first question..."):
                        log_user_interaction("interview_started", {
                            "role": selected_role,
                            "experience": experience_level,
                            "type": interview_type,
                            "difficulty": difficulty_level,
                            "custom_context": custom_context if custom_context else "None"
                        })
                        interview_controller.start_interview(
                            selected_role, experience_level, interview_type, difficulty_level, custom_context
                        )
                        st.rerun()
        else:
            # Display conversation
            ui_manager.render_conversation(st.session_state.messages)
            
            # Handle user input
            if st.session_state.interview_started and not st.session_state.is_processing:
                audio_input = AudioInput()
                user_input = audio_input.get_user_input(
                    placeholder="Type your answer here, then press Submit answer - or answer by voice"
                )
                
                if user_input and session_manager.should_process_input(user_input):
                    log_user_interaction("response_submitted", {
                        "response_length": len(user_input),
                        "role": selected_role
                    })
                    
                    interview_controller.handle_user_input(
                        user_input, selected_role, experience_level, 
                        interview_type, difficulty_level, custom_context
                    )
                    
    except Exception as e:
        log_error(e, "Main application")
        st.error("An unexpected error occurred. Please refresh the page and try again.")

if __name__ == "__main__":
    main()

