# Evaluation System

This evaluation system is inspired by BAML's test framework but built from scratch for the Azure OpenAI Agent project. It provides a comprehensive way to test and validate AI-generated content, specifically lesson plans.

## Overview

The evaluation system follows BAML's pattern of defining test cases with:
- **Function to test**: The AI function being evaluated
- **Input arguments**: Parameters passed to the function  
- **Expected outputs**: What we expect the function to produce
- **Evaluation metrics**: How to determine if the output is correct

## Structure

```
evals/
├── README.md              # This file
├── eval_config.py         # Configuration and custom evaluators
├── lesson_plan_evals.py   # Main evaluation suites
└── run_evals.py           # Evaluation runner script
```

## Quick Start

1. **Set up environment**:
   ```bash
   # Make sure your .env file has Azure OpenAI credentials
   cp .env.example .env  # Edit with your credentials
   ```

2. **Run all evaluations**:
   ```bash
   python run_evals.py
   ```

3. **Run specific evaluation suite**:
   ```python
   from evals.lesson_plan_evals import math_lesson_tests, run_all_evaluations
   from azure_openai_agent.evaluation import EvaluationRunner
   
   runner = EvaluationRunner()
   results = runner.run_suite(math_lesson_tests)
   runner.print_results(results)
   ```

## Test Suites

### Mathematics Lessons
Tests algebra, geometry, and arithmetic lesson generation:
- ✅ Required sections (objectives, materials, activities)
- ✅ Appropriate length (100+ words)
- ✅ Learning objectives present

### Science Lessons  
Tests biology, chemistry, and physics lessons:
- ✅ Scientific methodology (experiments, hypotheses)
- ✅ Lab requirements and materials
- ✅ Observation and data collection

### English Language Arts
Tests reading, writing, and literature lessons:
- ✅ Literacy skill focus
- ✅ Creative and analytical components
- ✅ Vocabulary and comprehension strategies

### History Lessons
Tests historical content and critical thinking:
- ✅ Timeline and chronology
- ✅ Cause and effect relationships
- ✅ Historical significance and context

### Integration Tests
Tests system functionality:
- ✅ Agent initialization
- ✅ Custom requirements handling
- ✅ Error handling and recovery

## Creating Custom Tests

### Basic Test Case
```python
from azure_openai_agent.evaluation import TestCase

test = TestCase(
    name="my_custom_test",
    function="generate_math_lesson",  # Function to test
    args={
        "topic": "Algebra", 
        "grade_level": "8th Grade"
    },
    expected="objectives",  # What to look for
    metric="contains",      # How to evaluate
    metadata={"category": "math"}
)
```

### Custom Evaluation Function
```python
def my_evaluator(output: str, expected: str) -> bool:
    """Custom evaluation logic"""
    return len(output.split()) >= 100 and expected.lower() in output.lower()

test = TestCase(
    name="custom_eval_test", 
    function="generate_lesson",
    args={"topic": "Science"},
    expected="experiment",
    metric="custom",
    custom_metric=my_evaluator
)
```

### Test Suite
```python
from azure_openai_agent.evaluation import EvaluationSuite

suite = EvaluationSuite(
    name="My Custom Suite",
    description="Testing custom functionality",
    tests=[test1, test2, test3],
    setup=lambda: print("Starting tests"),
    teardown=lambda: print("Tests completed")
)
```

## Evaluation Metrics

### Built-in Metrics
- **`exact_match`**: Exact string comparison
- **`contains`**: Check if output contains expected text
- **`custom`**: Use custom evaluation function

### Lesson Plan Evaluators
- **`has_required_sections`**: Check for lesson plan components
- **`appropriate_length`**: Validate minimum word count
- **`contains_objectives`**: Ensure learning objectives present
- **`grade_appropriateness`**: Age-appropriate content
- **`educational_standards`**: Standards alignment

## Results and Reporting

### Console Output
```
✅ basic_algebra_lesson (generate_math_lesson)
   Status: PASS
   Time: 2.341s

❌ geometry_lesson_completeness (generate_math_lesson) 
   Status: FAIL
   Time: 1.876s
   Expected: 100
   Got: 87

Summary: 8/10 tests passed (80.0%)
Average execution time: 2.108s
```

### Programmatic Access
```python
results = runner.run_suite(suite)

for result in results:
    print(f"{result.test_name}: {result.result.value}")
    if result.result != EvaluationResult.PASS:
        print(f"  Error: {result.error}")

# Get summary statistics
summary = runner.get_summary(results)
print(f"Success rate: {summary['success_rate']:.1%}")
```

## Configuration

Edit `eval_config.py` to customize:
- **Timeouts**: Maximum execution time per test
- **Quality thresholds**: Minimum requirements for content
- **Subject requirements**: Subject-specific validation
- **Grade adaptations**: Grade-level appropriateness

## Comparison with BAML

| BAML Pattern | Our Implementation |
|--------------|-------------------|
| `test name { ... }` | `TestCase(name="name", ...)` |
| `functions [FuncName]` | `function="func_name"` |
| `args { ... }` | `args={...}` |
| Built-in validation | Custom `EvaluationMetric` classes |
| VSCode playground | Python test runner |

## Examples

### Running Single Test
```python
from azure_openai_agent.evaluation import EvaluationRunner, TestCase
from azure_openai_agent.lesson_plan import generate_math_lesson

runner = EvaluationRunner()
runner.register_function("generate_math_lesson", generate_math_lesson)

test = TestCase(
    name="quick_test",
    function="generate_math_lesson", 
    args={"topic": "Fractions", "grade_level": "3rd Grade"},
    expected="objectives",
    metric="contains"
)

result = runner.run_test(test)
print(f"Result: {result.result.value}")
```

### Batch Evaluation
```bash
# Run all lesson plan evaluations
python run_evals.py

# Check exit code
echo $?  # 0 = success, 1 = failure
```

This evaluation system provides the same structured testing approach as BAML but is tailored specifically for your Azure OpenAI Agent and lesson plan generation use case.
