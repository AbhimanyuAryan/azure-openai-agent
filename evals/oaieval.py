#!/usr/bin/env python3
"""
oaieval command equivalent for Azure OpenAI Agent
Mimics OpenAI evals CLI: oaieval <model> <eval_name>
"""
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from openai_evals_runner import OpenAIEvalsRunner


def main():
    """
    CLI entry point mimicking OpenAI evals
    Usage: python oaieval.py azure_openai_agent lesson_plan_quality.dev.v0
    """
    parser = argparse.ArgumentParser(
        description="Azure OpenAI Agent Evaluation Runner (OpenAI evals compatible)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python oaieval.py azure_openai_agent lesson_plan_quality.dev.v0
  python oaieval.py azure_lesson_plan math_lesson_plans.dev.v0
  python oaieval.py azure_simple lesson_plan_quality.dev.v0

Available completion functions:
  - azure_openai_agent  : Default lesson plan agent
  - azure_lesson_plan   : Specialized lesson plan agent  
  - azure_simple        : Basic Azure OpenAI agent

Available evaluations:
  - lesson_plan_quality.dev.v0  : General lesson plan quality
  - math_lesson_plans.dev.v0     : Mathematics-specific evaluation
  - science_lesson_plans.dev.v0  : Science-specific evaluation
  - english_lesson_plans.dev.v0  : English/ELA-specific evaluation
        """
    )
    
    parser.add_argument(
        "completion_fn", 
        help="Completion function to use (e.g., azure_openai_agent)"
    )
    
    parser.add_argument(
        "eval_name",
        help="Name of evaluation to run (e.g., lesson_plan_quality.dev.v0)"
    )
    
    parser.add_argument(
        "--registry-path",
        default=None,
        help="Path to evals registry (default: ./registry)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--samples-limit",
        type=int,
        default=None,
        help="Limit number of samples to evaluate"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    print(f"Azure OpenAI Agent Evaluation Runner")
    print(f"Completion Function: {args.completion_fn}")
    print(f"Evaluation: {args.eval_name}")
    print("-" * 50)
    
    try:
        runner = OpenAIEvalsRunner()
        results = runner.run_eval(args.eval_name, args.completion_fn)
        
        if not results:
            print("❌ No results generated")
            sys.exit(1)
        
        runner.print_summary(results)
        
        # Determine exit code based on performance
        avg_score = sum(r.score for r in results) / len(results)
        
        if avg_score >= 0.8:
            print(f"\n🎉 Evaluation PASSED with excellent performance!")
            exit_code = 0
        elif avg_score >= 0.6:
            print(f"\n✅ Evaluation PASSED with good performance")
            exit_code = 0
        else:
            print(f"\n❌ Evaluation FAILED - needs improvement")
            exit_code = 1
        
        print(f"Average Score: {avg_score:.3f}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Evaluation failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
