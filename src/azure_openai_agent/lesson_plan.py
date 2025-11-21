"""
Lesson plan generation functionality using Azure OpenAI Agent
"""
from typing import Dict, Any, Optional
from .agent import SimpleAgent


class LessonPlanAgent:
    """Specialized agent for generating lesson plans"""
    
    def __init__(self, **agent_kwargs):
        """Initialize lesson plan agent"""
        system_prompt = """You are an expert educational consultant and lesson plan designer. 
        Your role is to create comprehensive, engaging, and pedagogically sound lesson plans.
        
        When creating lesson plans, always include:
        1. Clear learning objectives
        2. Target audience/grade level
        3. Duration and timing
        4. Required materials
        5. Step-by-step activities
        6. Assessment methods
        7. Differentiation strategies
        
        Make your lesson plans practical, engaging, and aligned with educational standards."""
        
        self.agent = SimpleAgent(
            name="Lesson Plan Designer",
            system_prompt=system_prompt,
            **agent_kwargs
        )
    
    def generate_lesson_plan(
        self, 
        subject: str, 
        topic: str, 
        grade_level: str, 
        duration: str = "50 minutes",
        additional_requirements: str = ""
    ) -> str:
        """
        Generate a comprehensive lesson plan
        
        Args:
            subject: Subject area (e.g., "Mathematics", "Science", "History")
            topic: Specific topic to cover
            grade_level: Target grade level
            duration: Lesson duration
            additional_requirements: Any additional requirements or constraints
        
        Returns:
            Generated lesson plan as string
        """
        prompt = f"""Create a comprehensive lesson plan with the following specifications:

Subject: {subject}
Topic: {topic}
Grade Level: {grade_level}
Duration: {duration}

{f"Additional Requirements: {additional_requirements}" if additional_requirements else ""}

Please provide a detailed lesson plan that includes all the essential components mentioned in my instructions."""

        return self.agent.chat(prompt)
    
    def generate_activity(self, subject: str, topic: str, activity_type: str = "hands-on") -> str:
        """Generate a specific learning activity"""
        prompt = f"""Design a {activity_type} learning activity for:
Subject: {subject}
Topic: {topic}

The activity should be engaging, educational, and practical to implement in a classroom setting."""
        
        return self.agent.chat(prompt)
    
    def create_assessment(self, subject: str, topic: str, assessment_type: str = "formative") -> str:
        """Create an assessment for the lesson"""
        prompt = f"""Create a {assessment_type} assessment for:
Subject: {subject}
Topic: {topic}

Include clear rubrics and success criteria."""
        
        return self.agent.chat(prompt)
    
    def adapt_for_grade(self, lesson_content: str, target_grade: str) -> str:
        """Adapt existing lesson content for a different grade level"""
        prompt = f"""Adapt the following lesson content for {target_grade} students:

{lesson_content}

Adjust the complexity, vocabulary, activities, and expectations to be appropriate for this grade level."""
        
        return self.agent.chat(prompt)


# Convenience functions for evaluation
def generate_math_lesson(topic: str, grade_level: str) -> str:
    """Generate a mathematics lesson plan"""
    agent = LessonPlanAgent()
    return agent.generate_lesson_plan("Mathematics", topic, grade_level)


def generate_science_lesson(topic: str, grade_level: str) -> str:
    """Generate a science lesson plan"""
    agent = LessonPlanAgent()
    return agent.generate_lesson_plan("Science", topic, grade_level)


def generate_english_lesson(topic: str, grade_level: str) -> str:
    """Generate an English/Language Arts lesson plan"""
    agent = LessonPlanAgent()
    return agent.generate_lesson_plan("English Language Arts", topic, grade_level)


def generate_history_lesson(topic: str, grade_level: str) -> str:
    """Generate a history lesson plan"""
    agent = LessonPlanAgent()
    return agent.generate_lesson_plan("History", topic, grade_level)
