import google.generativeai as genai
import json
from typing import Dict, List, Optional, Any
from .config import ROLE_CRITERIA, EXPERIENCE_CRITERIA

class InterviewAnalyzer:
    def __init__(self, model):
        self.model = model
        self.performance_weights = {
            'content': 0.5,
            'technical': 0.3,
            'experience_match': 0.2
        }
        self.min_answer_length = 10
        
    def validate_input(self, answer: str) -> tuple[bool, str]:
        """Validate user input before processing"""
        if not answer:
            return False, "Answer cannot be empty"
        if len(answer.strip()) < self.min_answer_length:
            return False, f"Answer must be at least {self.min_answer_length} characters long"
        return True, ""
        
    def analyze_response(self, 
                        job_role: str, 
                        question: str, 
                        answer: Optional[str] = None,
                        experience_level: str = "entry",
                        use_speech: bool = False) -> Dict[str, Any]:
        """
        Analyze interview response with enhanced role-specific scoring.
        
        Args:
            job_role: The role being interviewed for
            question: The interview question
            answer: Text answer (optional if use_speech is True)
            experience_level: Experience level of the candidate
            use_speech: Whether to use speech input for the answer
            
        Returns:
            Dictionary containing analysis results
        """
        from ..utils.helpers import speech_to_text
        
        if use_speech and not answer:
            answer = speech_to_text()
            if not answer:
                return {
                    "error": "Speech could not be recognized. Please try again or provide text input."
                }
        
        # Get role-specific criteria with fallback to generic criteria
        role_weights = ROLE_CRITERIA.get(job_role, {
            "general_knowledge": {
                "weight": 0.4,
                "key_aspects": ["domain knowledge", "industry awareness", "technical fundamentals"]
            },
            "communication": {
                "weight": 0.3,
                "key_aspects": ["clarity", "structure", "professionalism"]
            },
            "experience": {
                "weight": 0.3,
                "key_aspects": ["practical application", "problem handling", "decision making"]
            }
        })
        
        # Get experience expectations
        exp_expect = EXPERIENCE_CRITERIA.get(experience_level, EXPERIENCE_CRITERIA["0-2 years"])
        
        # Enhanced prompt for more accurate analysis
        prompt = f"""As an expert technical interviewer for {job_role} positions with {experience_level} experience expectation, provide a detailed evaluation of this response.

Question: {question}
Answer: {answer}

Experience Level Expectations:
{json.dumps(exp_expect['criteria'], indent=2)}

Role-Specific Evaluation Criteria:
{json.dumps(role_weights, indent=2)}

Evaluate thoroughly and provide output in this JSON format:
{{
    "content_analysis": {{
        "relevance_score": (1-10),
        "clarity_score": (1-10),
        "structure_score": (1-10),
        "strengths": ["detailed strength points"],
        "improvements": ["specific improvement areas"],
        "example_better_answer": "concise improved answer example"
    }},
    "technical_assessment": {{
        "knowledge_depth": (1-10),
        "practical_understanding": (1-10),
        "problem_solving": (1-10),
        "specific_feedback": ["detailed technical feedback points"]
    }},
    "experience_level_assessment": {{
        "meets_expectations": boolean,
        "gap_analysis": ["specific gaps compared to experience level"],
        "recommendations": ["targeted improvement suggestions"],
        "alignment_score": (1-10)
    }},
    "role_specific_evaluation": {{
        "strengths": ["role-specific strong points"],
        "areas_to_improve": ["role-specific improvement areas"],
        "key_competencies_rating": (1-10)
    }},
    "overall_impression": "comprehensive evaluation summary"
}}"""
        
        try:
            # Get AI evaluation
            response = self.model.generate_content(prompt)
            ai_feedback = json.loads(response.text)
            
            # Enhanced content score calculation with weighted components
            content_score = (
                ai_feedback['content_analysis']['relevance_score'] * 0.4 +
                ai_feedback['content_analysis']['clarity_score'] * 0.3 +
                ai_feedback['content_analysis']['structure_score'] * 0.3
            )
            
            # Apply dynamic experience-level threshold
            if content_score < exp_expect['base_score']:
                content_score = max(
                    content_score * exp_expect['threshold'],
                    exp_expect['base_score'] - 2.0
                )
            
            # Enhanced technical score calculation using role-specific weights
            tech_score = sum(
                ai_feedback['technical_assessment'][metric] * weight
                for metric, weight in [
                    ('knowledge_depth', 0.4),
                    ('practical_understanding', 0.3),
                    ('problem_solving', 0.3)
                ]
            )
            
            # Calculate experience alignment score
            exp_alignment_score = ai_feedback['experience_level_assessment']['alignment_score']
            
            # Calculate final score with all components
            final_score = (
                content_score * self.performance_weights['content'] +
                tech_score * self.performance_weights['technical'] +
                exp_alignment_score * self.performance_weights['experience_match']
            ) * exp_expect['threshold']
            
            # Apply experience-based bounds
            final_score = min(final_score, exp_expect['base_score'] + 1.5)
            final_score = max(final_score, exp_expect['base_score'] - 2.0)
            
            return {
                "score": round(final_score, 1),
                "content_analysis": ai_feedback['content_analysis'],
                "technical_assessment": ai_feedback['technical_assessment'],
                "experience_level_assessment": ai_feedback['experience_level_assessment'],
                "role_specific_evaluation": ai_feedback['role_specific_evaluation'],
                "overall_impression": ai_feedback['overall_impression']
            }
            
        except Exception as e:
            # Enhanced error handling with more specific feedback
            error_type = type(e).__name__
            error_msg = str(e)
            return {
                "score": exp_expect['base_score'] - 2.0,
                "content_analysis": {
                    "strengths": ["Analysis incomplete"],
                    "improvements": [f"Technical error occurred: {error_type}"],
                    "example_better_answer": "Analysis unavailable due to error"
                },
                "technical_assessment": {
                    "knowledge_depth": exp_expect['base_score'] - 2.0,
                    "practical_understanding": exp_expect['base_score'] - 2.0,
                    "problem_solving": exp_expect['base_score'] - 2.0,
                    "specific_feedback": [f"Error details: {error_msg}"]
                },
                "experience_level_assessment": {
                    "meets_expectations": False,
                    "gap_analysis": ["Assessment interrupted due to technical error"],
                    "recommendations": ["Please try again or contact support if error persists"],
                    "alignment_score": exp_expect['base_score'] - 2.0
                },
                "role_specific_evaluation": {
                    "strengths": [],
                    "areas_to_improve": ["Could not complete role-specific evaluation"],
                    "key_competencies_rating": exp_expect['base_score'] - 2.0
                },
                "overall_impression": f"Analysis incomplete due to error: {error_type}"
            }
