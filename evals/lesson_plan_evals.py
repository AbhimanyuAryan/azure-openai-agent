"""
Evaluation suites for lesson plan generation
Inspired by BAML's test structure
"""
import sys
import os
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from azure_openai_agent.evaluation import (
    EvaluationSuite, TestCase, EvaluationRunner, LessonPlanEvaluator
)
from azure_openai_agent.lesson_plan import (
    generate_math_lesson, generate_science_lesson, 
    generate_english_lesson, generate_history_lesson,
    LessonPlanAgent
)


# Test cases for mathematics lessons
math_lesson_tests = EvaluationSuite(
    name="Mathematics Lesson Plans",
    description="Evaluate quality and completeness of mathematics lesson plans",
    tests=[
        TestCase(
            name="basic_algebra_lesson",
            function="generate_math_lesson", 
            args={
                "topic": "Linear Equations",
                "grade_level": "8th Grade"
            },
            expected=["objectives", "activities", "materials", "assessment"],
            metric="custom",
            custom_metric=lambda output, expected: LessonPlanEvaluator.has_required_sections(output, expected),
            metadata={"category": "algebra", "difficulty": "intermediate"}
        ),
        TestCase(
            name="geometry_lesson_completeness",
            function="generate_math_lesson",
            args={
                "topic": "Area and Perimeter", 
                "grade_level": "5th Grade"
            },
            expected=100,  # minimum word count
            metric="custom",
            custom_metric=lambda output, expected: LessonPlanEvaluator.appropriate_length(output, expected),
            metadata={"category": "geometry", "difficulty": "basic"}
        ),
        TestCase(
            name="math_lesson_has_objectives",
            function="generate_math_lesson",
            args={
                "topic": "Fractions",
                "grade_level": "4th Grade"
            },
            expected=None,
            metric="custom", 
            custom_metric=LessonPlanEvaluator.contains_objectives,
            metadata={"category": "arithmetic", "difficulty": "basic"}
        )
    ]
)

# Test cases for science lessons
science_lesson_tests = EvaluationSuite(
    name="Science Lesson Plans",
    description="Evaluate science lesson plan quality and scientific accuracy",
    tests=[
        TestCase(
            name="photosynthesis_lesson",
            function="generate_science_lesson",
            args={
                "topic": "Photosynthesis",
                "grade_level": "6th Grade"
            },
            expected=["experiment", "observation", "hypothesis", "materials"],
            metric="custom",
            custom_metric=lambda output, expected: any(term.lower() in output.lower() for term in expected),
            metadata={"category": "biology", "requires_lab": True}
        ),
        TestCase(
            name="physics_forces_lesson",
            function="generate_science_lesson", 
            args={
                "topic": "Forces and Motion",
                "grade_level": "7th Grade"
            },
            expected=150,  # minimum word count for physics lessons
            metric="custom",
            custom_metric=lambda output, expected: LessonPlanEvaluator.appropriate_length(output, expected),
            metadata={"category": "physics", "difficulty": "intermediate"}
        )
    ]
)

# Test cases for English lessons
english_lesson_tests = EvaluationSuite(
    name="English Language Arts Lesson Plans", 
    description="Evaluate English/ELA lesson plan quality and literacy focus",
    tests=[
        TestCase(
            name="creative_writing_lesson",
            function="generate_english_lesson",
            args={
                "topic": "Creative Writing - Short Stories",
                "grade_level": "9th Grade"
            },
            expected=["writing", "creativity", "narrative", "structure"],
            metric="custom", 
            custom_metric=lambda output, expected: sum(term.lower() in output.lower() for term in expected) >= 2,
            metadata={"category": "writing", "skill_focus": "creativity"}
        ),
        TestCase(
            name="reading_comprehension_lesson",
            function="generate_english_lesson",
            args={
                "topic": "Reading Comprehension Strategies", 
                "grade_level": "3rd Grade"
            },
            expected=None,
            metric="custom",
            custom_metric=LessonPlanEvaluator.contains_objectives,
            metadata={"category": "reading", "skill_focus": "comprehension"}
        )
    ]
)

# Test cases for history lessons  
history_lesson_tests = EvaluationSuite(
    name="History Lesson Plans",
    description="Evaluate history lesson plans for historical accuracy and engagement",
    tests=[
        TestCase(
            name="american_revolution_lesson", 
            function="generate_history_lesson",
            args={
                "topic": "American Revolution",
                "grade_level": "5th Grade"
            },
            expected=["timeline", "causes", "effects", "key figures"],
            metric="custom",
            custom_metric=lambda output, expected: sum(term.lower() in output.lower() for term in expected) >= 2,
            metadata={"category": "american_history", "time_period": "18th_century"}
        ),
        TestCase(
            name="world_war_lesson_depth",
            function="generate_history_lesson", 
            args={
                "topic": "World War II",
                "grade_level": "11th Grade"
            },
            expected=200,  # Higher standard for advanced history
            metric="custom",
            custom_metric=lambda output, expected: LessonPlanEvaluator.appropriate_length(output, expected),
            metadata={"category": "world_history", "complexity": "high"}
        )
    ]
)

# Integration test suite
integration_tests = EvaluationSuite(
    name="Lesson Plan Integration Tests",
    description="Test lesson plan agent functionality and integration",
    tests=[
        TestCase(
            name="agent_initialization",
            function="test_agent_creation",
            args={},
            expected=None,
            metric="exact_match",  # Just test it doesn't crash
            metadata={"test_type": "integration"}
        ),
        TestCase(
            name="custom_requirements_handling",
            function="test_custom_requirements", 
            args={
                "subject": "Mathematics",
                "topic": "Statistics", 
                "grade_level": "10th Grade",
                "additional_requirements": "Include real-world data examples"
            },
            expected="real-world",
            metric="contains",
            metadata={"test_type": "customization"}
        )
    ]
)


# Helper functions for integration tests
def test_agent_creation():
    """Test that lesson plan agent can be created successfully"""
    try:
        agent = LessonPlanAgent()
        return "SUCCESS: Agent created"
    except Exception as e:
        raise Exception(f"Failed to create agent: {e}")


def test_custom_requirements(**kwargs):
    """Test custom requirements are incorporated"""
    agent = LessonPlanAgent()
    return agent.generate_lesson_plan(**kwargs)


# All test suites
ALL_SUITES = [
    math_lesson_tests,
    science_lesson_tests, 
    english_lesson_tests,
    history_lesson_tests,
    integration_tests
]


def run_all_evaluations():
    """Run all lesson plan evaluations"""
    print("🚀 Starting Lesson Plan Evaluation Suite")
    print("=" * 60)
    
    runner = EvaluationRunner()
    
    # Register functions
    runner.register_function("generate_math_lesson", generate_math_lesson)
    runner.register_function("generate_science_lesson", generate_science_lesson) 
    runner.register_function("generate_english_lesson", generate_english_lesson)
    runner.register_function("generate_history_lesson", generate_history_lesson)
    runner.register_function("test_agent_creation", test_agent_creation)
    runner.register_function("test_custom_requirements", test_custom_requirements)
    
    # Run all suites
    all_results = []
    for suite in ALL_SUITES:
        print(f"\n📋 Running: {suite.name}")
        print(f"   {suite.description}")
        
        results = runner.run_suite(suite)
        all_results.extend(results)
        
        # Show suite summary
        suite_summary = runner.get_summary(results)
        print(f"   ✓ {suite_summary['passed']}/{suite_summary['total_tests']} passed")
    
    # Final results
    print("\n" + "="*60)
    runner.print_results(all_results)
    
    return all_results


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    run_all_evaluations()
