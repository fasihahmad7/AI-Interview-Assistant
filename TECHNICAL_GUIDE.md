# AI Interview Assistant - Technical Guide

## Overview
A Streamlit application that uses Google Gemini (`gemini-2.5-flash`) to run mock interviews: it generates role-specific questions, grades answers, and shows model answers. Answers can be typed or spoken; speech is transcribed with Google's free Web Speech service.

There is no backend server and no database in the live flow: all state lives in Streamlit's session state for the browser tab.

## Architecture

```
           ┌──────────────────┐   ┌──────────────────┐                          ┌──────────────────┐
UI         │      app.py      │──►│    UIManager     │                          │    AudioInput    │
           └─────────┬────────┘   └──────────────────┘                          └─────────┬────────┘
                     │                                                                    │
           ┌─────────▼──────────────────────────────────────────────────────┐             │
CONTROL    │                      InterviewController                       │             │
           └─────────┬──────────────────────┬──────────────────────┬────────┘             │
                     │                      │                      │                      │
           ┌─────────▼────────┐   ┌─────────▼────────┐   ┌─────────▼────────┐   ┌─────────▼────────┐
SERVICES   │    AIService     │   │  SessionManager  │   │metrics_calculator│   │ speech_to_text() │
           └─────────┬────────┘   └─────────┬────────┘   └──────────────────┘   └─────────┬────────┘
                     │                      │                                             │
           ┌─────────▼────────┐   ┌─────────▼────────┐                          ┌─────────▼────────┐
EXTERNAL   │    Gemini API    │   │ st.session_state │                          │Google Web Speech │
           └──────────────────┘   └──────────────────┘                          └──────────────────┘
```

- **`app.py`** builds the services on every rerun, draws the sidebar, and hands user input to the controller.
- **`InterviewController`** is the only place that coordinates the AI service, session state and scoring.
- **Voice** goes `AudioInput` → `speech_to_text()` → Google Web Speech, completely separate from Gemini.

### Where things live

| File | Responsibility |
|---|---|
| `app.py` | Entry point: sidebar, main loop |
| `.streamlit/config.toml` | Dark theme matching the app CSS; hides the Deploy button |
| `src/controllers/interview_controller.py` | Interview flow (start, each answer) |
| `src/services/ai_service.py` | Gemini prompts, retries, parsing |
| `src/services/session_manager.py` | All `st.session_state` reads and writes |
| `src/ui/ui_manager.py` | CSS and conversation rendering |
| `src/components/audio_input.py` | Answer box, voice recording, transcript review |
| `src/components/custom_text_input.py` | Text area (plus a paste-block script, see Known issues) |
| `src/utils/helpers.py` | `speech_to_text()` and small helpers |
| `src/utils/metrics_calculator.py` | Score extraction and weighting |
| `src/utils/config.py` | Roles, levels, model name, focus map |
| `src/utils/interview_analyzer.py` | `validate_input()` (minimum answer length) |
| `check_models.py` | Lists the Gemini models your key can use |

In the repo but **not wired into the app yet**: `components/dashboard.py`, `database/db_manager.py`, and `InterviewAnalyzer.analyze_response()`.

## Streamlit's rerun model

Every interaction (click, typing, submit) re-runs `app.py` from top to bottom, and the UI is rebuilt from `st.session_state`. Anything that must survive a click has to live there:

| Key | Purpose |
|---|---|
| `messages` | The conversation (questions, answers, assessments) |
| `interview_history` | Per-answer record used by Export |
| `session_stats` | Answered count and latest metrics |
| `question_count` | Drives skill rotation |
| `is_processing` | Blocks double submits |
| `current_response` | Ignores duplicate input |
| `last_request_time` | 1-second rate limit |
| `voice_draft` | Transcript awaiting review: `{"question", "text", "take"}` |
| `voice_take` | Gives each review box a fresh widget key |

Refreshing the browser clears all of this.

## Life of an answer

`InterviewController.process_user_response()` runs these steps; the two Gemini calls happen one after the other:

1. **Answer arrives** - `AudioInput.get_user_input()` returns text when the user clicks *Submit answer*, or *Submit for evaluation* on a voice draft.
2. **Guard** - `should_process_input()`: not empty, not a duplicate, not already processing.
3. **Validate** - `InterviewAnalyzer.validate_input()`: at least 10 characters.
4. **Rate limit** - `check_rate_limit()`: at least 1 second since the last request.
5. **Store the answer** - `add_message("user", ...)`.
6. **Grade it (Gemini call #1)** - `AIService.evaluate_response()`.
7. **Ask the next question (Gemini call #2)** - `question_count += 1`, then `generate_interview_question()`.
8. **Save** - assessment and next question added to `messages`; `add_interview_history()`.
9. **Score** - `calculate_role_specific_metrics()` → `update_session_stats()`.
10. **Rerun** - `st.rerun()`; the page redraws.

Failures in steps 2-4 show a warning and stop. Steps 5-9 run inside `try/finally`, so `is_processing` is always reset; an exception shows an error message.

### Message model

```python
st.session_state.messages = [
  {"role": "assistant", "type": "question",
   "content": {"question": "...", "expected_answer": "..."}},
  {"role": "user", "type": "message", "content": "I would first ..."},
  {"role": "assistant", "type": "assessment", "content": "Technical Assessment:\n- ..."},
  {"role": "assistant", "type": "question", "content": {...}},
]
```

### Rendering

`UIManager.render_conversation()` shows each exchange as **Question → Your Response → Assessment → Model Answer**. A question's expected answer is held back and only rendered after that question's assessment.

`UIManager._format_rich_text()` turns Gemini's markdown-like text into HTML:

| Input | Output |
|---|---|
| `<`, `>` in any text | Escaped first (`html.escape`), so e.g. `List<WebElement>` displays correctly |
| `**bold**` | `<b>bold</b>` |
| `` `code` `` | `<code>code</code>` |
| Line ending with `:` | Section heading |
| `- `, `* `, `• `, `1. ` | Bullet item |
| `Label: 7.5 - reason` | Bullet item |

Each assessment shows a score badge computed from that assessment alone.

## Prompts and parsing

### Prompt #1 - ask a question (`generate_interview_question`)
Built from five blocks:
1. **Role context** - role, experience, interview type, difficulty, focus points
2. **Conversation history** - the last 4 messages, with answers truncated to 200 characters
3. **Skill strategy** - which focus skill to ask about next (see below)
4. **Question criteria** - relevance, level, style, plus definitions of each difficulty
5. **Output format** - `Question: ...` / `Expected Answer: ...`

Parsing is a string split:

```python
parts = reply.split("Expected Answer:", 1)
question = parts[0].replace("Question:", "", 1).strip()
expected = parts[1].strip() if len(parts) > 1 else "No model answer provided."
```

If Gemini omits the marker, the whole reply becomes the question.

### Prompt #2 - grade the answer (`evaluate_response`)
Demands an exact format with decimal scores so the regexes can find them:

```
Technical Assessment:
- Knowledge Depth: 7.5 - ...
- Implementation Understanding: 6.0 - ...
- Best Practices Awareness: 7.0 - ...
Communication Assessment:
- Clarity / Structure / Professionalism: n.n - ...
Experience Level Match:
- Expected Level / Demonstrated Level / Score: 7.0
Key Strengths: / Areas for Improvement:
Follow-up Question:
Expected Answer:
```

The reply is split on `Follow-up Question:`. The first part is shown as the assessment and parsed for scores. The follow-up question and answer are returned but **not used**; the next question comes from prompt #1.

### Skill rotation
Focus areas are split on commas. Example with `Selenium, API testing, CI/CD`:

| `question_count` | Previous skill | Guidance sent to Gemini |
|---|---|---|
| 0 | - | First question: focus on Selenium |
| 1 | Selenium | Weak answer? One follow-up on Selenium, else move to API testing |
| 2 | API testing | Weak? Follow-up, else move to CI/CD |
| 3 | CI/CD | Weak? Follow-up, else move to Selenium |
| 4 | Selenium | **Must** move to API testing |
| 5 | API testing | **Must** move to CI/CD |

Rotation is computed from `question_count`, not from what Gemini actually asked, so it can drift after follow-ups.

## Scoring

`metrics_calculator.extract_scores_from_text()` pulls seven numbers from each assessment, and `calculate_role_specific_metrics()` averages them across all assessments in the session:

| Sidebar label | Internal key | Calculation |
|---|---|---|
| Technical | `domain_knowledge` | Mean of Knowledge Depth, Implementation, Best Practices |
| Communication | `methodology_understanding` | Mean of Clarity, Structure, Professionalism |
| Experience Match | `practical_experience` | The `Score:` line under Experience Level Match |
| Overall | `overall_score` | `0.5 × Technical + 0.3 × Experience + 0.2 × Communication` |

Worked example: Technical (7.5, 6.5, 7.0) = 7.0; Communication (8.0, 7.0, 8.5) = 7.8; Experience = 7.0 → Overall = 0.5×7.0 + 0.3×7.0 + 0.2×7.8 = **7.2**.

### When parsing fails
1. **Labelled match** - three regex patterns per metric (`Knowledge Depth: 7.5`, `- Knowledge Depth: 7.5`, `Knowledge ... 7.5/10`); only values 1-10 count.
2. **Positional fallback** - no labels found: the first six numbers between 1 and 10 in the text, in order (can mis-assign).
3. **Placeholder scores** - still nothing: the controller fills in `6.0 + 0.5 × questions` (max 8.5). These are not real grades.

## Voice pipeline

`helpers.speech_to_text(on_update, start_timeout=10, end_silence=3, max_duration=180)`:

1. **Calibrate** - 1 second of ambient noise sets the energy threshold.
2. **Listen** - `recognizer.listen()` returns one phrase; a phrase ends after a 1.2 s pause (`pause_threshold`) and is capped at 30 s.
3. **Transcribe** - each phrase is submitted to a thread pool and sent to `recognize_google()` while listening continues. Short requests also suit the free endpoint.
4. **Live update** - `on_update` receives the joined transcript so far, shown in an `st.status` panel.
5. **Stop** - after 3 s of silence following a phrase, 10 s with no speech at the start, or 180 s in total.

`AudioInput` stores the result as `voice_draft`, tied to the current question number, and renders a review panel: **Submit for evaluation**, **Record again**, or **Type instead**. The draft survives validation failures and API errors, and is dropped once the answer is accepted (the question number moves on). A confirmed draft then follows the same path as a typed answer.

Streamlit can't process clicks while the recording call is blocking, so silence is the only way to end a recording.

## Guardrails

| Guardrail | Behaviour |
|---|---|
| Retry | `retry_on_error(max_retries=3, delay=2)` on `generate_content`: up to 3 attempts, waiting 2 s then 4 s. Empty replies count as failures. |
| Quota | An error mentioning "quota" stops retrying immediately. |
| Rate limit | At least 1 second between submissions. |
| Minimum length | Answers under 10 characters are rejected with a warning. |
| Double submit | `is_processing` and `current_response` block repeats. |
| No lost input | On error, the typed text or voice draft stays for a resubmit. |

## Configuration

| What | Where |
|---|---|
| API key | `.env` (`GOOGLE_API_KEY`). `.env.example` also lists `LOG_LEVEL`, but `app.py` currently hard-codes `INFO`. |
| Roles and levels | `src/utils/config.py` - `JOB_ROLES` (QA roles listed first), `EXPERIENCE_RANGES`, `INTERVIEW_TYPES`, `DIFFICULTY_LEVELS` |
| Gemini model | `config.MODEL_NAME` |
| Prompts | `src/services/ai_service.py` |
| Score weights | `src/utils/metrics_calculator.py` |
| Voice timing | `speech_to_text(end_silence=..., start_timeout=..., max_duration=...)` |
| Look and feel | `.streamlit/config.toml` and the CSS in `ui_manager.py` |

`TEMPERATURE`, `TOP_P` and `TOP_K` in `config.py` are defined but not currently passed to the model.

## Testing

```bash
python -m pytest -q
```

| Suite | Tests | Covers |
|---|---|---|
| `test_session_manager.py` | 15 | State init and reset, input validation, duplicate and busy guards, adding messages |
| `test_speech_to_text.py` | 7 | Microphone and recognizer mocked: phrases joined across pauses, timeouts, unintelligible audio, microphone errors |
| `test_ui_formatting.py` | 7 | Bullets, headings, bold and code, HTML escaping, no stray spacing |

Not automated: the Streamlit UI end to end, real Gemini replies, and a real microphone.

### Testing without using API quota
Replace `AIService.generate_content` with canned replies and run the real app. Save this as `mock_app.py` in the project root and run `streamlit run mock_app.py`:

```python
import runpy
from src.services import ai_service

QUESTION = "Question: ...\nExpected Answer:\n- ..."
ASSESSMENT = "Technical Assessment:\n- Knowledge Depth: 7.5 - ..."

def fake(self, prompt):
    if "evaluate this response" in str(prompt):
        return ASSESSMENT
    return QUESTION

ai_service.AIService.generate_content = fake
runpy.run_path("app.py", run_name="__main__")
```

Edit the canned text to exercise the parsing fallbacks (remove scores, drop the `Expected Answer:` marker, add HTML).

### Manual QA charter
- **Configuration** - every role × level × type × difficulty; focus areas with 1, 3 and 10 skills; changing the setup mid-interview (the next question uses the new settings); New Interview fully resets.
- **Voice** - long pauses mid-answer; total silence; noisy room; no or blocked microphone; editing the transcript; Record again.
- **Input edge cases** - under 10 characters; HTML, `List<T>`, emoji; very long answers; double-clicking Submit; refreshing mid-interview.
- **AI and network** - quota exhausted; offline or slow network; a reply with no scores; a reply missing `Expected Answer:`.

## Known issues

| Severity | Issue |
|---|---|
| High | Placeholder scores are shown when no scores can be parsed |
| Medium | Two Gemini calls per answer; the follow-up generated during grading is discarded |
| Medium | Session is lost on browser refresh; no persistence |
| Medium | Voice relies on Google's free, unofficial speech endpoint |
| Low | Skill rotation follows `question_count`, not the topics actually asked |
| Low | The paste-blocking script never runs (it's inside a sandboxed iframe) |
| Low | Unused modules: `dashboard.py`, `db_manager.py`, `analyze_response()` |
| Low | Any error containing the word "invalid" is reported as an invalid API key |

## Security and privacy
- The API key is read from `.env`, which is excluded from git.
- User answers and AI text are HTML-escaped before rendering.
- Interview content is sent to Google's Gemini API, and voice audio to Google's speech service. Don't enter client-confidential information.
- Nothing is stored on disk by the running app; Export is a download the user triggers.

## Running locally
```bash
pip install -r requirements.txt
# .env
GOOGLE_API_KEY=your_key_here

streamlit run app.py          # run from the project folder so .streamlit/config.toml is used
python -m pytest -q
python check_models.py        # list models your key can use
```
