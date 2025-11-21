"""
Configuration for evaluation system
Define custom test suites and evaluation parameters
"""

# Evaluation Configuration
EVAL_CONFIG = {
    "timeout_seconds": 30,
    "retry_attempts": 2,
    "parallel_execution": False,
    "save_results": True,
    "results_directory": "eval_results",
    
    # Quality thresholds
    "min_lesson_length": 100,  # words
    "required_sections": [
        "objectives", "materials", "activities", 
        "assessment", "duration", "grade"
    ],
    
    # Subject-specific requirements
    "subject_requirements": {
        "mathematics": {
            "keywords": ["problem", "solve", "calculate", "equation"],
            "min_length": 120
        },
        "science": {
            "keywords": ["experiment", "hypothesis", "observation", "data"],
            "min_length": 150
        },
        "english": {
            "keywords": ["reading", "writing", "vocabulary", "comprehension"],
            "min_length": 130
        },
        "history": {
            "keywords": ["timeline", "cause", "effect", "significance"],
            "min_length": 140
        }
    },
    
    # Grade level adaptations
    "grade_adaptations": {
        "elementary": {"vocabulary_level": "basic", "concept_complexity": "simple"},
        "middle": {"vocabulary_level": "intermediate", "concept_complexity": "moderate"}, 
        "high": {"vocabulary_level": "advanced", "concept_complexity": "complex"}
    }
}

# Custom evaluation functions
def evaluate_lesson_structure(output: str, expected_sections: list) -> bool:
    """
    Evaluate if lesson plan has proper structure
    Similar to BAML's custom evaluation functions
    """
    output_lower = output.lower()
    found_sections = []
    
    for section in expected_sections:
        if section.lower() in output_lower:
            found_sections.append(section)
    
    # Require at least 75% of sections
    return len(found_sections) / len(expected_sections) >= 0.75


def evaluate_grade_appropriateness(output: str, grade_level: str) -> bool:
    """Evaluate if content is appropriate for grade level"""
    
    # Simple heuristics for grade appropriateness
    word_count = len(output.split())
    sentence_count = output.count('.') + output.count('!') + output.count('?')
    avg_sentence_length = word_count / max(sentence_count, 1)
    
    if "elementary" in grade_level.lower() or any(grade in grade_level for grade in ["K", "1", "2", "3", "4", "5"]):
        # Elementary: shorter sentences, simpler vocabulary
        return avg_sentence_length <= 15
    elif "middle" in grade_level.lower() or any(grade in grade_level for grade in ["6", "7", "8"]):
        # Middle school: moderate complexity
        return 10 <= avg_sentence_length <= 20
    else:
        # High school and above: more complex is OK
        return avg_sentence_length >= 12


def evaluate_educational_standards(output: str, subject: str) -> bool:
    """Evaluate alignment with educational standards"""
    
    subject_lower = subject.lower()
    output_lower = output.lower()
    
    # Check for standards-based language
    standards_indicators = [
        "standard", "benchmark", "objective", "outcome",
        "assess", "evaluate", "demonstrate", "understand"
    ]
    
    found_indicators = sum(1 for indicator in standards_indicators if indicator in output_lower)
    
    # Require at least 2 standards-based indicators
    return found_indicators >= 2
