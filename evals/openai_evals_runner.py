#!/usr/bin/env python3
"""
OpenAI Evals compatible runner for Azure OpenAI Agent
Follows OpenAI evals patterns and structure
"""
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import yaml

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from azure_completion_fn import COMPLETION_FNS


@dataclass
class EvalResult:
    """Result of a single evaluation"""
    prompt: str
    completion: str
    ideal: str
    score: float
    grade: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0


class ModelGradedEvaluator:
    """
    Model-graded evaluator similar to OpenAI evals
    """
    
    def __init__(self, spec_path: str, completion_fn_name: str = "azure_openai_agent"):
        """Initialize evaluator with spec file"""
        self.spec_path = Path(spec_path)
        self.completion_fn_name = completion_fn_name
        self.spec = self._load_spec()
        self.completion_fn = self._get_completion_fn()
    
    def _load_spec(self) -> Dict[str, Any]:
        """Load model-graded spec from YAML file"""
        try:
            with open(self.spec_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading spec {self.spec_path}: {e}")
            return {}
    
    def _get_completion_fn(self):
        """Get completion function"""
        if self.completion_fn_name in COMPLETION_FNS:
            return COMPLETION_FNS[self.completion_fn_name]()
        else:
            raise ValueError(f"Unknown completion function: {self.completion_fn_name}")
    
    def evaluate_sample(self, sample: Dict[str, Any]) -> EvalResult:
        """Evaluate a single sample"""
        start_time = time.time()
        
        try:
            # Generate completion
            input_prompt = sample.get("input", "")
            completion_result = self.completion_fn(input_prompt)
            completion = completion_result.completion if hasattr(completion_result, 'completion') else str(completion_result)
            
            # Grade the completion using model grader
            grade, score = self._grade_completion(completion, sample)
            
            execution_time = time.time() - start_time
            
            return EvalResult(
                prompt=str(input_prompt),
                completion=completion,
                ideal=sample.get("ideal", ""),
                score=score,
                grade=grade,
                metadata={
                    "subject": sample.get("subject"),
                    "grade_level": sample.get("grade_level"),
                    "topic": sample.get("topic"),
                    "eval_criteria": sample.get("eval_criteria")
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            return EvalResult(
                prompt=str(sample.get("input", "")),
                completion=f"ERROR: {str(e)}",
                ideal=sample.get("ideal", ""),
                score=0.0,
                metadata={"error": str(e)},
                execution_time=time.time() - start_time
            )
    
    def _grade_completion(self, completion: str, sample: Dict[str, Any]) -> tuple:
        """Grade completion using model grader"""
        try:
            # Format grading prompt
            prompt_template = self.spec.get("prompt", "")
            
            # Substitute variables in prompt
            grading_prompt = prompt_template.format(
                lesson_plan_output=completion,
                subject=sample.get("subject", "Unknown"),
                grade_level=sample.get("grade_level", "Unknown"),
                topic=sample.get("topic", "Unknown")
            )
            
            # Get model grade (using the same completion function for now)
            # In a real implementation, you'd use a separate grading model
            grader_result = self.completion_fn(grading_prompt)
            grader_response = grader_result.completion if hasattr(grader_result, 'completion') else str(grader_result)
            
            # Extract grade from response
            grade = self._extract_grade(grader_response)
            
            # Convert grade to score
            choice_scores = self.spec.get("choice_scores", {"A": 1, "B": 0.8, "C": 0.6, "D": 0.4, "F": 0})
            score = choice_scores.get(grade, 0.0)
            
            return grade, score
            
        except Exception as e:
            print(f"Error in grading: {e}")
            # Fallback scoring based on length and basic criteria
            return self._fallback_scoring(completion)
    
    def _extract_grade(self, grader_response: str) -> str:
        """Extract grade letter from grader response"""
        response_upper = grader_response.upper()
        
        # Look for grade patterns
        import re
        
        # Look for "Grade: X" or "Final grade: X" patterns
        grade_patterns = [
            r'(?:FINAL\s+)?GRADE:\s*([A-F])',
            r'(?:OVERALL\s+)?GRADE\s+(?:IS\s+)?([A-F])',
            r'\b([A-F])\b(?:\s*[-:]|\s+GRADE)',
        ]
        
        for pattern in grade_patterns:
            match = re.search(pattern, response_upper)
            if match:
                return match.group(1)
        
        # Look for explicit grade mentions
        if " A " in response_upper or response_upper.endswith(" A") or "GRADE A" in response_upper:
            return "A"
        elif " B " in response_upper or response_upper.endswith(" B") or "GRADE B" in response_upper:
            return "B"
        elif " C " in response_upper or response_upper.endswith(" C") or "GRADE C" in response_upper:
            return "C"
        elif " D " in response_upper or response_upper.endswith(" D") or "GRADE D" in response_upper:
            return "D"
        elif " F " in response_upper or response_upper.endswith(" F") or "GRADE F" in response_upper:
            return "F"
        
        # Default to C if no clear grade found
        return "C"
    
    def _fallback_scoring(self, completion: str) -> tuple:
        """Fallback scoring when model grading fails"""
        # Simple heuristics
        word_count = len(completion.split())
        
        required_terms = ["objective", "materials", "activities", "assessment"]
        found_terms = sum(1 for term in required_terms if term.lower() in completion.lower())
        
        if word_count >= 200 and found_terms >= 3:
            return "B", 0.8
        elif word_count >= 100 and found_terms >= 2:
            return "C", 0.6
        elif word_count >= 50 and found_terms >= 1:
            return "D", 0.4
        else:
            return "F", 0.0


class OpenAIEvalsRunner:
    """
    Main runner following OpenAI evals patterns
    """
    
    def __init__(self):
        self.results: List[EvalResult] = []
        self.registry_path = Path(__file__).parent / "registry"
    
    def run_eval(self, eval_name: str, completion_fn: str = "azure_openai_agent") -> List[EvalResult]:
        """
        Run an evaluation by name
        
        Args:
            eval_name: Name of eval to run (e.g., "lesson_plan_quality.dev.v0")
            completion_fn: Completion function to use
            
        Returns:
            List of evaluation results
        """
        print(f"🚀 Running eval: {eval_name}")
        print(f"📋 Using completion function: {completion_fn}")
        
        # Load eval config
        eval_config = self._load_eval_config(eval_name)
        if not eval_config:
            print(f"❌ Could not load eval config for {eval_name}")
            return []
        
        # Load samples
        samples_file = eval_config.get("args", {}).get("samples_jsonl")
        if not samples_file:
            print(f"❌ No samples_jsonl specified in eval config")
            return []
        
        samples = self._load_samples(samples_file)
        if not samples:
            print(f"❌ Could not load samples from {samples_file}")
            return []
        
        # Load model-graded spec if needed
        spec_file = eval_config.get("args", {}).get("modelgraded_spec")
        if spec_file:
            spec_path = self.registry_path / "modelgraded" / spec_file
            evaluator = ModelGradedEvaluator(spec_path, completion_fn)
        else:
            # Fallback to basic evaluator
            evaluator = ModelGradedEvaluator(
                self.registry_path / "modelgraded" / "lesson_plan_quality" / "spec.yaml",
                completion_fn
            )
        
        # Run evaluation on all samples
        results = []
        print(f"📝 Evaluating {len(samples)} samples...")
        
        for i, sample in enumerate(samples, 1):
            print(f"   Sample {i}/{len(samples)}", end=" ")
            result = evaluator.evaluate_sample(sample)
            results.append(result)
            
            # Show quick result
            print(f"-> {result.grade or 'N/A'} ({result.score:.2f}) [{result.execution_time:.2f}s]")
        
        self.results.extend(results)
        return results
    
    def _load_eval_config(self, eval_name: str) -> Optional[Dict[str, Any]]:
        """Load evaluation configuration"""
        # Look in registry/evals/
        eval_files = list(self.registry_path.glob("evals/*.yaml"))
        
        for eval_file in eval_files:
            try:
                with open(eval_file, 'r') as f:
                    config = yaml.safe_load(f)
                    if eval_name in config:
                        return config[eval_name]
            except Exception as e:
                print(f"Error loading {eval_file}: {e}")
        
        return None
    
    def _load_samples(self, samples_file: str) -> List[Dict[str, Any]]:
        """Load samples from JSONL file"""
        samples_path = self.registry_path / "data" / samples_file
        
        if not samples_path.exists():
            print(f"Samples file not found: {samples_path}")
            return []
        
        samples = []
        try:
            with open(samples_path, 'r') as f:
                for line in f:
                    if line.strip():
                        samples.append(json.loads(line))
        except Exception as e:
            print(f"Error loading samples: {e}")
        
        return samples
    
    def print_summary(self, results: Optional[List[EvalResult]] = None):
        """Print evaluation summary"""
        if results is None:
            results = self.results
        
        if not results:
            print("No results to summarize")
            return
        
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        
        # Overall stats
        total = len(results)
        avg_score = sum(r.score for r in results) / total
        avg_time = sum(r.execution_time for r in results) / total
        
        # Grade distribution
        grade_counts = {}
        for result in results:
            grade = result.grade or "N/A"
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        print(f"📊 Total samples: {total}")
        print(f"📈 Average score: {avg_score:.3f}")
        print(f"⏱️  Average time: {avg_time:.2f}s")
        print(f"📋 Grade distribution: {dict(sorted(grade_counts.items()))}")
        
        # Individual results
        print(f"\n{'Sample':<10} {'Grade':<6} {'Score':<6} {'Time':<8} {'Topic'}")
        print("-" * 60)
        
        for i, result in enumerate(results, 1):
            topic = result.metadata.get("topic", "Unknown") if result.metadata else "Unknown"
            print(f"{i:<10} {result.grade or 'N/A':<6} {result.score:<6.2f} {result.execution_time:<8.2f} {topic}")
        
        # Pass/fail analysis
        passing_score = 0.6  # C or better
        passed = sum(1 for r in results if r.score >= passing_score)
        pass_rate = passed / total
        
        print(f"\n✅ Passed (≥{passing_score}): {passed}/{total} ({pass_rate:.1%})")
        
        if pass_rate >= 0.8:
            print("🎉 Excellent performance!")
        elif pass_rate >= 0.6:
            print("👍 Good performance")
        elif pass_rate >= 0.4:
            print("⚠️  Needs improvement")
        else:
            print("❌ Poor performance - needs significant work")


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenAI Evals compatible runner for Azure OpenAI Agent")
    parser.add_argument("eval_name", help="Name of evaluation to run")
    parser.add_argument("--completion-fn", default="azure_openai_agent", help="Completion function to use")
    
    args = parser.parse_args()
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    runner = OpenAIEvalsRunner()
    results = runner.run_eval(args.eval_name, args.completion_fn)
    runner.print_summary(results)
    
    # Exit code based on performance
    if not results:
        sys.exit(1)
    
    avg_score = sum(r.score for r in results) / len(results)
    sys.exit(0 if avg_score >= 0.6 else 1)


if __name__ == "__main__":
    main()
