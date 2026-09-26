"""
Configuration settings for the AI Interview Assistant.
"""
from typing import Dict, List, Any

# --- AI Model Settings ---
MODEL_NAME = 'gemini-2.5-flash'
TEMPERATURE = 0.7
TOP_P = 0.8
TOP_K = 40

# --- Interview Settings ---
INTERVIEW_TYPES = [
    "Technical", "Behavioral", "Problem Solving"
]
DIFFICULTY_LEVELS = [
    "Easy", "Medium", "Hard", "Legend"
]
JOB_ROLES = [
    # QA roles first - the primary audience
    "QA Engineer", "Functional Tester", "Automation Test Engineer", "SDET",
    "API Test Engineer", "Performance Test Engineer",
    "Mobile Test Engineer", "Security Test Engineer",
    "QA Lead", "Test Architect",
    # Other engineering roles
    "Software Engineer", "Full Stack Developer", "DevOps Engineer",
    "Data Scientist", "AI/ML Engineer", "Product Manager"
]
EXPERIENCE_RANGES = [
    "0-2 years", "2-5 years", "5-8 years", "8+ years"
]

# --- Role-specific evaluation criteria ---
ROLE_CRITERIA = {
    "Software Engineer": {
        "technical_depth": {
            "weight": 0.4,
            "key_aspects": ["algorithms", "data structures", "system design", "coding practices"]
        },
        "problem_solving": {
            "weight": 0.3,
            "key_aspects": ["analytical thinking", "optimization", "edge cases", "scalability"]
        },
        "best_practices": {
            "weight": 0.3,
            "key_aspects": ["clean code", "testing", "documentation", "security"]
        },
        "core_skills": ["Data Structures", "Algorithms", "System Design", "Programming Languages"],
        "practices": ["Clean Code", "Testing", "Version Control", "CI/CD"],
        "soft_skills": ["Problem Solving", "Communication", "Collaboration"],
    },
    "Data Scientist": {
        "analytical_thinking": {
            "weight": 0.4,
            "key_aspects": ["statistical analysis", "data preprocessing", "feature engineering", "model evaluation"]
        },
        "technical_knowledge": {
            "weight": 0.3,
            "key_aspects": ["machine learning", "deep learning", "data visualization", "big data"]
        },
        "research_methodology": {
            "weight": 0.3,
            "key_aspects": ["experiment design", "hypothesis testing", "validation methods", "literature review"]
        },
        "core_skills": ["Statistics", "Machine Learning", "Data Analysis", "Feature Engineering"],
        "practices": ["Model Evaluation", "Data Preprocessing", "Experiment Design"],
        "soft_skills": ["Research", "Data Visualization", "Business Understanding"],
    },
    "Functional Tester": {
        "test_methodology": {
            "weight": 0.4,
            "key_aspects": ["test planning", "test case design", "defect lifecycle", "test coverage"]
        },
        "quality_mindset": {
            "weight": 0.3,
            "key_aspects": ["attention to detail", "risk assessment", "user perspective", "quality standards"]
        },
        "technical_understanding": {
            "weight": 0.3,
            "key_aspects": ["testing tools", "automation concepts", "test environments", "debugging"]
        },
        "core_skills": ["Test Design", "Test Automation", "Bug Tracking", "Test Coverage"],
        "practices": ["Test Planning", "Quality Metrics", "Test Frameworks"],
        "soft_skills": ["Attention to Detail", "Process Improvement", "Risk Assessment"],
    },
    "DevOps Engineer": {
        "core_skills": ["Infrastructure", "Automation", "Cloud Services", "CI/CD"],
        "practices": ["Monitoring", "Security", "Scalability", "Reliability"],
        "soft_skills": ["Troubleshooting", "Documentation", "Incident Response"],
        "evaluation_weights": {
            "infrastructure_knowledge": 0.4,
            "automation_skills": 0.3,
            "operational_excellence": 0.3
        }
    },
    "QA Engineer": {
        "core_skills": ["Test Design", "Test Automation", "Bug Tracking", "Test Coverage"],
        "practices": ["Test Planning", "Quality Metrics", "Test Frameworks"],
        "soft_skills": ["Attention to Detail", "Process Improvement", "Risk Assessment"],
        "evaluation_weights": {
            "testing_methodology": 0.4,
            "automation_expertise": 0.3,
            "quality_mindset": 0.3
        }
    }
}

# --- Experience level expectations ---
EXPERIENCE_CRITERIA = {
    "0-2 years": {
        "base_score": 6.0,
        "threshold": 0.7,
        "criteria": {
            "technical_depth": "Basic understanding of core concepts",
            "practical_skills": "Able to handle basic tasks with guidance",
            "independence": "Requires regular supervision"
        }
    },
    "2-5 years": {
        "base_score": 7.0,
        "threshold": 0.75,
        "criteria": {
            "technical_depth": "Good understanding of advanced concepts",
            "practical_skills": "Can handle moderate complexity independently",
            "independence": "Occasional guidance needed"
        }
    },
    "5-8 years": {
        "base_score": 8.0,
        "threshold": 0.8,
        "criteria": {
            "technical_depth": "Deep understanding of complex topics",
            "practical_skills": "Handles complex tasks effectively",
            "independence": "Works independently, guides others"
        }
    },
    "8+ years": {
        "base_score": 8.5,
        "threshold": 0.85,
        "criteria": {
            "technical_depth": "Expert-level understanding",
            "practical_skills": "Tackles challenging problems innovatively",
            "independence": "Strategic thinking, mentors others"
        }
    }
}

# --- Interview type focus areas ---
INTERVIEW_FOCUS = {
    "Technical": {
        "primary": "technical_skills",
        "secondary": "problem_solving",
        "evaluation_aspects": [
            "Technical depth",
            "Code quality",
            "Architecture",
            "Best practices"
        ]
    },
    "Behavioral": {
        "primary": "soft_skills",
        "secondary": "experience",
        "evaluation_aspects": [
            "Communication",
            "Leadership",
            "Collaboration",
            "Problem handling"
        ]
    },
    "Problem Solving": {
        "primary": "analytical",
        "secondary": "approach",
        "evaluation_aspects": [
            "Problem breakdown",
            "Solution design",
            "Trade-offs",
            "Implementation"
        ]
    }
}

# --- Difficulty level modifiers ---
DIFFICULTY_MODIFIERS = {
    "Easy": {
        "complexity": 0.7,
        "depth": "fundamental concepts",
        "scope": "single concept"
    },
    "Medium": {
        "complexity": 0.85,
        "depth": "applied knowledge",
        "scope": "multiple concepts"
    },
    "Hard": {
        "complexity": 1.0,
        "depth": "advanced topics",
        "scope": "complex scenarios"
    },
    "Legend": {
        "complexity": 1.2,
        "depth": "expert knowledge",
        "scope": "system design"
    }
}

# --- Error Messages ---
ERROR_MESSAGES = {
    'rate_limit': '⚠️ Please wait a moment before submitting another response.',
    'invalid_input': '⚠️ Your response is too short. Please provide a more detailed answer.',
    'api_error': '⚠️ There was an issue connecting to the AI service. Please try again.',
    'speech_error': '⚠️ Could not recognize speech. Please try again or use text input.'
}