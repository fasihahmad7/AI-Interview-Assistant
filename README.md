# AI Interview Assistant

An AI-powered mock interviewer that helps engineers prepare for client interviews. It asks realistic, role-specific questions, lets you answer by typing or speaking, scores each answer with detailed feedback, and shows a model answer so every question is also a learning moment. Powered by Google Gemini.

## Demo
Watch the demo on YouTube: [AI Interview Assistant Demo](https://youtu.be/w6jjtutRZ4M)

## Features

- 🎯 **Role-specific questions** for 16 roles, including 10 QA and testing roles (QA Engineer, SDET, Automation, API, Performance, Mobile, Security, QA Lead, Test Architect, Functional Tester)
- 📈 **Adjustable interview**: 4 experience bands, 3 interview types (Technical, Behavioral, Problem Solving) and 4 difficulty levels (Easy to Legend)
- 🧭 **Focus areas**: list skills such as `Selenium, API testing, CI/CD` and questions rotate across them
- 🔁 **Adaptive follow-ups**: a weak answer gets one follow-up; a strong one moves on to the next skill
- 🎙️ **Answer by voice**: keeps listening through natural pauses, shows the transcript live, stops after about 3 seconds of silence, and lets you review and edit the transcript before it's evaluated
- 📊 **Scored feedback**: technical depth, communication and experience-level match, with strengths and areas to improve
- ✅ **Model answers** revealed after you answer each question
- 📋 **Session progress** in the sidebar and a one-click **JSON export** of the whole session

## Setup

1. Clone the repository
2. Install dependencies (Python 3.10+):
   ```bash
   pip install -r requirements.txt
   ```
   This installs Streamlit, the Google Generative AI SDK, SpeechRecognition and PyAudio, plus data and charting libraries.

3. Create a `.env` file in the project folder with your Google AI API key (see `.env.example`):
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
   To check which Gemini models your key can use, run `python check_models.py`.

4. Run the application **from the project folder** (so the theme in `.streamlit/config.toml` is picked up):
   ```bash
   streamlit run app.py
   ```

### Voice input
Voice input records from the microphone of the machine running the app, so it's designed for running locally.
- Make sure a microphone is connected and your OS allows Python to use it
- Speech is converted to text by Google's free Web Speech service (no API key needed, internet required). It does not use your Gemini quota.

## Usage

1. In the sidebar, choose the role, experience level, interview type and difficulty. Optionally add focus areas (comma-separated).
2. Click **Start Interview** to get the first question.
3. Answer:
   - **Type** your answer and click **Submit answer**, or
   - Click **Answer by voice**, speak your answer, and pause for about 3 seconds when you're done. Review the transcript, fix anything misheard, then click **Submit for evaluation** (or **Record again** / **Type instead**).
4. Read the assessment and its score, then compare with the model answer. The next question appears below.
5. Use **New Interview** to start over, or **Export History** to download the session as JSON.

## Scores

Each answer is scored from 1 to 10 on six criteria, plus a match against the expected experience level. The sidebar shows averages across the session:

| Score | Made up of |
|---|---|
| **Technical** | Knowledge depth, implementation understanding, best practices |
| **Communication** | Clarity, structure, professionalism |
| **Experience Match** | How well the answer fits the chosen experience level |
| **Overall** | 50% Technical + 30% Experience Match + 20% Communication |

Each assessment also shows its own overall score as a badge.

## Testing

```bash
python -m pytest -q
```

29 unit tests cover session state management, the voice-input loop (microphone and speech service mocked) and the formatting of AI responses. See [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md) for how to test the app without using API quota.

## Project Structure

```
ai_interview_assistant/
├── app.py                        # Entry point: sidebar, main interview loop
├── check_models.py               # Lists the Gemini models available to your API key
├── requirements.txt
├── .env.example                  # Environment configuration example
├── .streamlit/
│   └── config.toml               # Dark theme, hides the Deploy button
├── TECHNICAL_GUIDE.md            # Architecture and internals
├── tests/
│   ├── test_session_manager.py   # Session state, validation, duplicate guards
│   ├── test_speech_to_text.py    # Voice-input loop (mocked microphone)
│   └── test_ui_formatting.py     # Rendering of AI responses
└── src/
    ├── controllers/
    │   └── interview_controller.py  # Interview flow: start, process each answer
    ├── services/
    │   ├── ai_service.py            # Gemini prompts, retries, response parsing
    │   └── session_manager.py       # Streamlit session state
    ├── ui/
    │   └── ui_manager.py            # CSS and conversation rendering
    ├── components/
    │   ├── audio_input.py           # Answer box, voice recording and review
    │   ├── custom_text_input.py     # Text area component
    │   └── dashboard.py             # Analytics dashboard (not yet wired into the app)
    ├── database/
    │   └── db_manager.py            # SQLite storage (not yet wired into the app)
    └── utils/
        ├── config.py                # Roles, levels, model name, evaluation criteria
        ├── helpers.py               # speech_to_text() and small helpers
        ├── metrics_calculator.py    # Score extraction and weighting
        ├── interview_analyzer.py    # Input validation
        └── logging_config.py        # Logging setup
```

## Current Limitations

This is an MVP intended to run locally:
- One user at a time; the session is lost when the browser is refreshed
- Each answer uses two Gemini calls, so the free API tier can run out during long sessions
- Voice input depends on Google's free speech service and the local microphone
- Answers are sent to Google's AI service, so don't include client-confidential information
