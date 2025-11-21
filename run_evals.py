#!/usr/bin/env python3
"""
Evaluation Runner for Azure OpenAI Agent
Run lesson plan evaluations similar to BAML's test system
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add evals to path
evals_path = Path(__file__).parent / "evals"
sys.path.insert(0, str(evals_path))

from lesson_plan_evals import run_all_evaluations


def main():
    """Main evaluation runner"""
    print("Azure OpenAI Agent - Evaluation System")
    print("Inspired by BAML's evaluation framework")
    print("=" * 50)
    
    try:
        results = run_all_evaluations()
        
        # Check if any tests failed
        failed_tests = [r for r in results if r.result.value != "pass"]
        
        if failed_tests:
            print(f"\n❌ {len(failed_tests)} test(s) failed or had errors")
            sys.exit(1)
        else:
            print(f"\n✅ All tests passed!")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n💥 Evaluation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
