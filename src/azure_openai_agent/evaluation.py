"""
Evaluation framework for Azure OpenAI agents
Inspired by BAML's evaluation system but built from scratch
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from pydantic import BaseModel, Field
from dataclasses import dataclass
from enum import Enum
import json
import time
import traceback
from datetime import datetime


class EvaluationResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"


@dataclass
class TestResult:
    """Result of a single test execution"""
    test_name: str
    function_name: str
    result: EvaluationResult
    output: Any
    expected: Any
    execution_time: float
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EvaluationMetric(ABC):
    """Abstract base class for evaluation metrics"""
    
    @abstractmethod
    def evaluate(self, output: Any, expected: Any, **kwargs) -> bool:
        """Evaluate if output matches expected result"""
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Return metric name"""
        pass


class ExactMatchMetric(EvaluationMetric):
    """Exact string match evaluation"""
    
    def evaluate(self, output: Any, expected: Any, **kwargs) -> bool:
        return str(output).strip() == str(expected).strip()
    
    def name(self) -> str:
        return "exact_match"


class ContainsMetric(EvaluationMetric):
    """Check if output contains expected substring"""
    
    def evaluate(self, output: Any, expected: Any, **kwargs) -> bool:
        return str(expected).lower() in str(output).lower()
    
    def name(self) -> str:
        return "contains"


class CustomMetric(EvaluationMetric):
    """Custom evaluation using a provided function"""
    
    def __init__(self, eval_func: Callable[[Any, Any], bool], metric_name: str):
        self.eval_func = eval_func
        self.metric_name = metric_name
    
    def evaluate(self, output: Any, expected: Any, **kwargs) -> bool:
        return self.eval_func(output, expected)
    
    def name(self) -> str:
        return self.metric_name


class TestCase(BaseModel):
    """Definition of a test case"""
    name: str = Field(..., description="Name of the test")
    function: str = Field(..., description="Function to test")
    args: Dict[str, Any] = Field(default_factory=dict, description="Arguments to pass to function")
    expected: Any = Field(None, description="Expected output")
    metric: str = Field("exact_match", description="Evaluation metric to use")
    custom_metric: Optional[Callable[[Any, Any], bool]] = Field(None, description="Custom evaluation function")
    timeout: float = Field(30.0, description="Test timeout in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional test metadata")


class EvaluationSuite(BaseModel):
    """Collection of test cases"""
    name: str = Field(..., description="Name of the evaluation suite")
    description: Optional[str] = Field(None, description="Suite description")
    tests: List[TestCase] = Field(default_factory=list, description="Test cases")
    setup: Optional[Callable[[], None]] = Field(None, description="Setup function")
    teardown: Optional[Callable[[], None]] = Field(None, description="Teardown function")


class EvaluationRunner:
    """Runs evaluation suites and manages results"""
    
    def __init__(self):
        self.metrics = {
            "exact_match": ExactMatchMetric(),
            "contains": ContainsMetric()
        }
        self.functions: Dict[str, Callable] = {}
        self.results: List[TestResult] = []
    
    def register_function(self, name: str, func: Callable):
        """Register a function for testing"""
        self.functions[name] = func
    
    def register_metric(self, metric: EvaluationMetric):
        """Register a custom metric"""
        self.metrics[metric.name()] = metric
    
    def run_test(self, test: TestCase) -> TestResult:
        """Run a single test case"""
        if test.function not in self.functions:
            return TestResult(
                test_name=test.name,
                function_name=test.function,
                result=EvaluationResult.ERROR,
                output=None,
                expected=test.expected,
                execution_time=0.0,
                error=f"Function '{test.function}' not registered"
            )
        
        try:
            start_time = time.time()
            
            # Execute function with provided args
            func = self.functions[test.function]
            output = func(**test.args)
            
            execution_time = time.time() - start_time
            
            # Evaluate result
            if test.expected is None:
                # No evaluation, just check if function runs
                result = EvaluationResult.PASS
            else:
                # Use appropriate metric
                if test.custom_metric:
                    metric = CustomMetric(test.custom_metric, "custom")
                else:
                    metric = self.metrics.get(test.metric, ExactMatchMetric())
                
                is_pass = metric.evaluate(output, test.expected)
                result = EvaluationResult.PASS if is_pass else EvaluationResult.FAIL
            
            return TestResult(
                test_name=test.name,
                function_name=test.function,
                result=result,
                output=output,
                expected=test.expected,
                execution_time=execution_time,
                metadata=test.metadata
            )
            
        except Exception as e:
            return TestResult(
                test_name=test.name,
                function_name=test.function,
                result=EvaluationResult.ERROR,
                output=None,
                expected=test.expected,
                execution_time=time.time() - start_time if 'start_time' in locals() else 0.0,
                error=f"{type(e).__name__}: {str(e)}",
                metadata={"traceback": traceback.format_exc()}
            )
    
    def run_suite(self, suite: EvaluationSuite) -> List[TestResult]:
        """Run an entire evaluation suite"""
        results = []
        
        # Setup
        if suite.setup:
            try:
                suite.setup()
            except Exception as e:
                print(f"Setup failed for suite '{suite.name}': {e}")
                return results
        
        # Run tests
        for test in suite.tests:
            result = self.run_test(test)
            results.append(result)
            self.results.append(result)
        
        # Teardown
        if suite.teardown:
            try:
                suite.teardown()
            except Exception as e:
                print(f"Teardown failed for suite '{suite.name}': {e}")
        
        return results
    
    def get_summary(self, results: Optional[List[TestResult]] = None) -> Dict[str, Any]:
        """Get summary statistics for test results"""
        if results is None:
            results = self.results
        
        total = len(results)
        passed = sum(1 for r in results if r.result == EvaluationResult.PASS)
        failed = sum(1 for r in results if r.result == EvaluationResult.FAIL)
        errors = sum(1 for r in results if r.result == EvaluationResult.ERROR)
        
        avg_time = sum(r.execution_time for r in results) / total if total > 0 else 0
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": passed / total if total > 0 else 0,
            "average_execution_time": avg_time,
            "timestamp": datetime.now().isoformat()
        }
    
    def print_results(self, results: Optional[List[TestResult]] = None):
        """Print formatted test results"""
        if results is None:
            results = self.results
        
        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)
        
        for result in results:
            status_icon = "✅" if result.result == EvaluationResult.PASS else "❌" if result.result == EvaluationResult.FAIL else "⚠️"
            print(f"\n{status_icon} {result.test_name} ({result.function_name})")
            print(f"   Status: {result.result.value.upper()}")
            print(f"   Time: {result.execution_time:.3f}s")
            
            if result.result == EvaluationResult.FAIL:
                print(f"   Expected: {result.expected}")
                print(f"   Got: {result.output}")
            elif result.result == EvaluationResult.ERROR:
                print(f"   Error: {result.error}")
        
        # Summary
        summary = self.get_summary(results)
        print(f"\n" + "-"*60)
        print(f"Summary: {summary['passed']}/{summary['total_tests']} tests passed ({summary['success_rate']:.1%})")
        print(f"Average execution time: {summary['average_execution_time']:.3f}s")


class LessonPlanEvaluator:
    """Specialized evaluator for lesson plan generation"""
    
    @staticmethod
    def has_required_sections(output: str, expected_sections: List[str]) -> bool:
        """Check if lesson plan contains all required sections"""
        output_lower = output.lower()
        return all(section.lower() in output_lower for section in expected_sections)
    
    @staticmethod
    def appropriate_length(output: str, min_words: int = 100) -> bool:
        """Check if lesson plan meets minimum word count"""
        word_count = len(output.split())
        return word_count >= min_words
    
    @staticmethod
    def contains_objectives(output: str, _: Any = None) -> bool:
        """Check if lesson plan contains learning objectives"""
        keywords = ["objective", "goal", "learn", "understand", "demonstrate", "identify"]
        output_lower = output.lower()
        return any(keyword in output_lower for keyword in keywords)
