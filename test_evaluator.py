#!/usr/bin/env python3
"""
Test script to run the evaluator programmatically
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add evals to path
sys.path.insert(0, str(Path(__file__).parent / "evals"))

from openai_evals_runner import OpenAIEvalsRunner


def main():
    """Test the evaluator"""
    print("🧪 Testing Azure OpenAI Agent Evaluator")
    print("=" * 50)
    
    runner = OpenAIEvalsRunner()
    
    # Run evaluation
    results = runner.run_eval("lesson_plan_quality.dev.v0", "azure_openai_agent")
    
    # Print results
    runner.print_summary(results)
    
    return results


if __name__ == "__main__":
    results = main()
    print(f"\n✅ Evaluation completed with {len(results)} samples")
