"""
Azure OpenAI Agent completion function for OpenAI evals
This integrates your Azure Agent with the OpenAI evals framework
"""
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from evals.api import CompletionFn, CompletionResult
    from evals.prompt.base import is_chat_prompt, ChatCompletionPrompt
except ImportError:
    # Fallback classes if evals package not available
    class CompletionResult:
        def __init__(self, response: str):
            self.completion = response
    
    class CompletionFn:
        def __call__(self, prompt, **kwargs) -> CompletionResult:
            raise NotImplementedError

from azure_openai_agent import LessonPlanAgent, SimpleAgent


class AzureLessonPlanCompletionFn(CompletionFn):
    """
    Completion function for Azure OpenAI Agent integrated with evals
    """
    
    def __init__(
        self, 
        agent_type: str = "lesson_plan",
        **agent_kwargs
    ):
        """
        Initialize Azure completion function
        
        Args:
            agent_type: Type of agent ("lesson_plan" or "simple")
            **agent_kwargs: Additional arguments for agent initialization
        """
        self.agent_type = agent_type
        self.agent_kwargs = agent_kwargs
        self._agent = None
    
    @property
    def agent(self):
        """Lazy initialization of agent"""
        if self._agent is None:
            if self.agent_type == "lesson_plan":
                self._agent = LessonPlanAgent(**self.agent_kwargs)
            else:
                self._agent = SimpleAgent(**self.agent_kwargs)
        return self._agent
    
    def __call__(
        self, 
        prompt: Union[str, List[Dict[str, str]]], 
        **kwargs
    ) -> CompletionResult:
        """
        Generate completion using Azure OpenAI Agent
        
        Args:
            prompt: Input prompt (string or chat messages)
            **kwargs: Additional parameters
            
        Returns:
            CompletionResult with the agent's response
        """
        try:
            # Handle chat format vs string format
            if isinstance(prompt, list) and len(prompt) > 0:
                # Chat format - extract user message
                user_message = None
                for message in prompt:
                    if message.get("role") == "user":
                        user_message = message.get("content", "")
                        break
                
                if user_message is None:
                    user_message = str(prompt[-1].get("content", ""))
            else:
                # String format
                user_message = str(prompt)
            
            # Reset conversation for each eval to ensure clean state
            self.agent.agent.reset_conversation()
            
            # Generate response using the agent
            if self.agent_type == "lesson_plan":
                # Try to extract lesson parameters from the prompt
                subject, topic, grade_level = self._extract_lesson_params(user_message)
                if subject and topic and grade_level:
                    response = self.agent.generate_lesson_plan(
                        subject=subject,
                        topic=topic, 
                        grade_level=grade_level,
                        **kwargs
                    )
                else:
                    # Fallback to general chat
                    response = self.agent.agent.chat(user_message)
            else:
                response = self.agent.chat(user_message)
            
            return CompletionResult(response)
            
        except Exception as e:
            # Return error as response for debugging
            error_response = f"Error generating response: {str(e)}"
            return CompletionResult(error_response)
    
    def _extract_lesson_params(self, prompt: str) -> tuple:
        """
        Extract subject, topic, and grade level from prompt
        
        Returns:
            (subject, topic, grade_level) tuple
        """
        prompt_lower = prompt.lower()
        
        # Common subjects
        subjects = {
            "math": "Mathematics",
            "mathematics": "Mathematics", 
            "science": "Science",
            "english": "English Language Arts",
            "history": "History",
            "social studies": "Social Studies",
            "physics": "Physics",
            "chemistry": "Chemistry",
            "biology": "Biology",
            "algebra": "Mathematics",
            "geometry": "Mathematics"
        }
        
        # Find subject
        subject = None
        for key, value in subjects.items():
            if key in prompt_lower:
                subject = value
                break
        
        # Find grade level
        grade_level = None
        import re
        
        # Look for patterns like "8th grade", "grade 8", "3rd grade"
        grade_patterns = [
            r'(\d+)(?:st|nd|rd|th)\s+grade',
            r'grade\s+(\d+)',
            r'(\d+)(?:st|nd|rd|th)\s+graders',
        ]
        
        for pattern in grade_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                grade_num = match.group(1)
                grade_level = f"{grade_num}th Grade"
                break
        
        # Find topic (this is more challenging, use a simple heuristic)
        topic = None
        
        # Look for common topic patterns
        topic_indicators = ["about", "on", "for", "teach", "lesson", "covering"]
        for indicator in topic_indicators:
            if indicator in prompt_lower:
                # Extract text after the indicator
                parts = prompt_lower.split(indicator, 1)
                if len(parts) > 1:
                    potential_topic = parts[1].strip()
                    # Take first few words as topic
                    topic_words = potential_topic.split()[:3]
                    topic = " ".join(topic_words).strip(" .,!?")
                    if topic:
                        break
        
        # Fallback - look for specific topics
        if not topic:
            common_topics = [
                "linear equations", "photosynthesis", "fractions", 
                "american revolution", "reading comprehension", "area and perimeter",
                "forces and motion", "creative writing"
            ]
            
            for t in common_topics:
                if t in prompt_lower:
                    topic = t.title()
                    break
        
        return subject, topic, grade_level


class AzureSimpleCompletionFn(CompletionFn):
    """Simple completion function using basic Azure Agent"""
    
    def __init__(self, **agent_kwargs):
        self.agent_kwargs = agent_kwargs
        self._agent = None
    
    @property 
    def agent(self):
        if self._agent is None:
            self._agent = SimpleAgent(**self.agent_kwargs)
        return self._agent
    
    def __call__(self, prompt, **kwargs) -> CompletionResult:
        try:
            # Handle chat vs string format
            if isinstance(prompt, list):
                # Extract last user message
                user_message = ""
                for message in prompt:
                    if message.get("role") == "user":
                        user_message = message.get("content", "")
            else:
                user_message = str(prompt)
            
            response = self.agent.chat(user_message)
            return CompletionResult(response)
            
        except Exception as e:
            return CompletionResult(f"Error: {str(e)}")


# Registry of completion functions
COMPLETION_FNS = {
    "azure_lesson_plan": AzureLessonPlanCompletionFn,
    "azure_simple": AzureSimpleCompletionFn,
    "azure_openai_agent": AzureLessonPlanCompletionFn,  # Default alias
}
