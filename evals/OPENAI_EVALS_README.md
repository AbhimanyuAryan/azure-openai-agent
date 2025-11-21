# OpenAI Evals Integration for Azure OpenAI Agent

This directory contains an OpenAI evals-compatible evaluation system for your Azure OpenAI Agent project. It follows the same patterns and structure as the official OpenAI evals framework while being tailored for lesson plan evaluation.

## 🌟 **Key Features**

- **📋 OpenAI Evals Compatibility**: Uses the same YAML config format and JSONL data structure
- **🎯 Model-Graded Evaluation**: Advanced AI-powered evaluation of lesson plan quality
- **🧪 Multiple Subject Areas**: Specialized evaluations for Math, Science, English, and History
- **⚡ Azure Integration**: Native integration with your Azure OpenAI Agent
- **📊 Comprehensive Reporting**: Detailed results and performance metrics

## 🏗️ **Structure**

```
evals/
├── OPENAI_EVALS_README.md         # This file
├── requirements.txt               # Additional dependencies
├── oaieval.py                    # CLI tool (mimics oaieval command)
├── openai_evals_runner.py         # Main evaluation runner
├── azure_completion_fn.py         # Azure Agent integration
└── registry/                     # Evaluation registry (OpenAI evals format)
    ├── evals/                    # Eval configurations (.yaml)
    │   └── lesson_plan_quality.yaml
    ├── data/                     # Evaluation datasets (.jsonl)
    │   ├── lesson_plan_quality/
    │   │   └── samples.jsonl
    │   └── math_lesson_plans/
    │       └── samples.jsonl
    └── modelgraded/              # Model grading specifications
        ├── lesson_plan_quality/
        │   └── spec.yaml
        └── math_lesson_plans/
            └── spec.yaml
```

## 🚀 **Quick Start**

### 1. Install Dependencies
```bash
pip install pyyaml python-dotenv
```

### 2. Set Environment Variables
Make sure your `.env` file contains Azure OpenAI credentials:
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

### 3. Run Evaluations
```bash
# Using the oaieval-style CLI
python evals/oaieval.py azure_openai_agent lesson_plan_quality.dev.v0

# Using the runner directly
python evals/openai_evals_runner.py lesson_plan_quality.dev.v0
```

## 📝 **Available Evaluations**

| Evaluation Name | Description | Subject Focus |
|----------------|-------------|---------------|
| `lesson_plan_quality.dev.v0` | General lesson plan quality assessment | All subjects |
| `math_lesson_plans.dev.v0` | Mathematics-specific evaluation | Mathematics |
| `science_lesson_plans.dev.v0` | Science pedagogy and accuracy | Science |
| `english_lesson_plans.dev.v0` | Literacy and language arts focus | English/ELA |

## 🎛️ **Completion Functions**

| Function Name | Description |
|---------------|-------------|
| `azure_openai_agent` | Default lesson plan agent (recommended) |
| `azure_lesson_plan` | Specialized lesson plan agent |
| `azure_simple` | Basic Azure OpenAI agent |

## 📊 **Evaluation Criteria**

### General Lesson Plan Quality
- **Essential Components**: Objectives, materials, activities, assessment
- **Quality Indicators**: Engagement, differentiation, real-world connections
- **Educational Standards**: Alignment and pedagogical soundness

### Mathematics-Specific
- **Mathematical Accuracy**: Correct content and notation
- **Pedagogical Approach**: Effective math teaching strategies
- **Problem-Solving**: Authentic mathematical reasoning opportunities

### Science-Specific  
- **Scientific Accuracy**: Correct scientific content
- **Inquiry-Based Learning**: Hands-on experiments and observations
- **Scientific Method**: Hypothesis, experimentation, data analysis

## 📈 **Grading Scale**

| Grade | Score | Description |
|-------|-------|-------------|
| A | 1.0 | Excellent - All components + high quality |
| B | 0.8 | Good - All components + some quality indicators |
| C | 0.6 | Satisfactory - Most components present |
| D | 0.4 | Needs Improvement - Missing key components |
| F | 0.0 | Poor - Not usable as lesson plan |

## 🔧 **Usage Examples**

### Command Line Usage
```bash
# Evaluate general lesson plan quality
python evals/oaieval.py azure_openai_agent lesson_plan_quality.dev.v0

# Evaluate mathematics lessons specifically  
python evals/oaieval.py azure_lesson_plan math_lesson_plans.dev.v0

# Verbose output
python evals/oaieval.py azure_openai_agent lesson_plan_quality.dev.v0 --verbose
```

### Programmatic Usage
```python
from evals.openai_evals_runner import OpenAIEvalsRunner

# Initialize runner
runner = OpenAIEvalsRunner()

# Run evaluation
results = runner.run_eval("lesson_plan_quality.dev.v0", "azure_openai_agent")

# Print summary
runner.print_summary(results)

# Access individual results
for result in results:
    print(f"Grade: {result.grade}, Score: {result.score}")
```

## 🎯 **Creating Custom Evaluations**

### 1. Create Evaluation Data (JSONL)
```jsonl
{"input": [{"role": "user", "content": "Create a lesson about fractions"}], "ideal": "B", "subject": "Mathematics", "grade_level": "4th Grade", "topic": "Fractions"}
```

### 2. Create Eval Configuration (YAML)
```yaml
my_custom_eval:
  id: my_custom_eval.dev.v0
  description: "My custom lesson plan evaluation"
  metrics: [accuracy]

my_custom_eval.dev.v0:
  class: evals.elsuite.modelgraded.classify:ModelBasedClassify
  args:
    samples_jsonl: my_custom_eval/samples.jsonl
    modelgraded_spec: my_custom_eval/spec.yaml
```

### 3. Create Model Grading Spec (YAML)
```yaml
completion_fn: azure_openai_agent
eval_type: cot_classify
prompt: |
  Evaluate this lesson plan and assign a grade A-F:
  {lesson_plan_output}
  
choice_scores:
  A: 1
  B: 0.8
  C: 0.6
  D: 0.4
  F: 0
```

## 📋 **Sample Data Format**

Each line in the JSONL file represents one test case:

```json
{
  "input": [
    {"role": "system", "content": "You are an expert lesson plan designer."},
    {"role": "user", "content": "Create a comprehensive lesson plan for teaching Linear Equations to 8th grade students."}
  ],
  "ideal": "A",
  "subject": "Mathematics",
  "grade_level": "8th Grade", 
  "topic": "Linear Equations",
  "eval_criteria": "Should include objectives, materials, activities, and assessment"
}
```

## 🔍 **Understanding Results**

### Console Output
```
🚀 Running eval: lesson_plan_quality.dev.v0
📋 Using completion function: azure_openai_agent
📝 Evaluating 6 samples...
   Sample 1/6 -> A (1.00) [3.45s]
   Sample 2/6 -> B (0.80) [2.87s]
   ...

============================================================
EVALUATION SUMMARY
============================================================
📊 Total samples: 6
📈 Average score: 0.767
⏱️ Average time: 3.12s
📋 Grade distribution: {'A': 2, 'B': 3, 'C': 1}

✅ Passed (≥0.6): 6/6 (100.0%)
🎉 Excellent performance!
```

### Programmatic Access
```python
# Access detailed results
for result in results:
    print(f"Prompt: {result.prompt[:100]}...")
    print(f"Completion: {result.completion[:200]}...")
    print(f"Grade: {result.grade}")
    print(f"Score: {result.score}")
    print(f"Metadata: {result.metadata}")
    print(f"Execution Time: {result.execution_time:.2f}s")
```

## 🎯 **Comparison with BAML vs OpenAI Evals**

| Aspect | BAML Pattern | OpenAI Evals Pattern | Our Implementation |
|--------|--------------|---------------------|-------------------|
| **Test Definition** | `test name { ... }` | YAML config files | YAML config + JSONL data |
| **Data Format** | Embedded in test | JSONL files | JSONL files |
| **Evaluation** | Built-in types | Model-graded + basic | Model-graded evaluation |
| **Running Tests** | VSCode playground | `oaieval` CLI | `oaieval.py` CLI |
| **Results** | Interactive | Structured logs | Structured results + summary |

## ⚙️ **Advanced Configuration**

### Custom Completion Function
```python
from evals.azure_completion_fn import COMPLETION_FNS, CompletionFn, CompletionResult

class MyCustomCompletionFn(CompletionFn):
    def __call__(self, prompt, **kwargs) -> CompletionResult:
        # Your custom logic here
        response = "Generated lesson plan..."
        return CompletionResult(response)

# Register your function
COMPLETION_FNS["my_custom_fn"] = MyCustomCompletionFn
```

### Environment Variables
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2023-07-01-preview

# Optional: Logging configuration
LOG_LEVEL=INFO
```

## 🤝 **Contributing New Evaluations**

1. **Create your dataset** in JSONL format
2. **Write evaluation spec** following our YAML templates
3. **Register the eval** in the registry structure
4. **Test thoroughly** with sample data
5. **Document your eval** with clear descriptions

## 🎉 **Benefits of This Approach**

- **✅ Industry Standard**: Uses OpenAI's proven evaluation framework
- **🔄 Compatibility**: Easy to migrate to official OpenAI evals if needed
- **🎯 Specialized**: Tailored specifically for educational content evaluation
- **📊 Comprehensive**: Detailed scoring and analysis capabilities
- **🚀 Production Ready**: Robust error handling and reporting

This OpenAI evals integration gives you a professional-grade evaluation system that matches industry standards while being perfectly suited for your lesson plan generation use case!
