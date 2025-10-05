"""
Simple Agent System - No LangChain Dependencies
Direct OpenAI API integration for lightweight, fast processing
"""
import os
import sys
from typing import Dict, Any, Optional

# Add project root to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from libs.shared.database import get_db
from libs.shared.models import Task, Agent
from libs.shared.logging_config import get_agent_logger
from libs.shared.openai_config import create_chat_completion, OpenAIError
from libs.shared.monitoring import monitor_task_execution
from sqlalchemy.orm import Session

# Initialize logger
logger = get_agent_logger()

class SimpleAgent:
    """Simple agent using direct OpenAI API calls"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.agent_config = agent_config
        self.model = agent_config.get('model', 'gpt-3.5-turbo')
        self.temperature = agent_config.get('temperature', 0.7)
        self.max_tokens = agent_config.get('max_tokens', 1000)
    
    @monitor_task_execution("simple_agent_process_task", user_id=None)
    def process_task(self, task: Task, context: Optional[Dict] = None) -> str:
        """Process a task using shared OpenAI configuration"""
        try:
            # Build the prompt
            prompt = self._build_prompt(task, context)
            
            # Use shared OpenAI configuration
            messages = [
                {"role": "system", "content": self.agent_config.get('prompt', 'You are a helpful AI assistant.')},
                {"role": "user", "content": prompt}
            ]
            
            response = create_chat_completion(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                user_id=task.user_id
            )
            
            result = response["content"]
            logger.info(f"Task processed successfully: {task.id}", task_id=task.id, user_id=task.user_id)
            return result
            
        except OpenAIError as e:
            logger.error(f"OpenAI error processing task {task.id}: {str(e)}", task_id=task.id, error_code=e.error_code)
            return f"OpenAI error: {str(e)}"
        except Exception as e:
            logger.error(f"Error processing task {task.id}: {str(e)}", task_id=task.id)
            return f"Error processing task: {str(e)}"
    
    def _build_prompt(self, task: Task, context: Optional[Dict] = None) -> str:
        """Build the prompt for the task"""
        prompt_parts = [
            f"Task Title: {task.title}",
            f"Task Description: {task.description or 'No description provided'}"
        ]
        
        if context:
            if 'user_info' in context:
                prompt_parts.append(f"User Information: {context['user_info']}")
            if 'previous_tasks' in context:
                prompt_parts.append(f"Previous Tasks: {context['previous_tasks']}")
            if 'system_status' in context:
                prompt_parts.append(f"System Status: {context['system_status']}")
        
        return "\n".join(prompt_parts)


class SimpleAgentFactory:
    """Factory for creating simple agents"""
    
    @staticmethod
    def create_basic_agent() -> SimpleAgent:
        """Create a basic simple agent"""
        config = {
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 1000,
            'prompt': 'You are a helpful AI assistant. Provide clear, accurate, and helpful responses.'
        }
        return SimpleAgent(config)
    
    @staticmethod
    def create_customer_support_agent() -> SimpleAgent:
        """Create a customer support agent"""
        config = {
            'model': 'gpt-3.5-turbo',
            'temperature': 0.3,
            'max_tokens': 1000,
            'prompt': """You are a helpful customer support agent. Your role is to:
- Listen empathetically to customer concerns
- Provide clear, accurate solutions
- Escalate complex issues when necessary
- Maintain a professional and friendly tone
- Follow up on resolutions

Always prioritize customer satisfaction and provide actionable solutions."""
        }
        return SimpleAgent(config)
    
    @staticmethod
    def create_content_writer_agent() -> SimpleAgent:
        """Create a content writer agent"""
        config = {
            'model': 'gpt-4',
            'temperature': 0.8,
            'max_tokens': 2000,
            'prompt': """You are a professional content writer. Your role is to:
- Create engaging, well-structured content
- Optimize content for SEO
- Adapt tone and style to target audience
- Include relevant keywords naturally
- Ensure content is original and valuable

Always produce high-quality, publication-ready content."""
        }
        return SimpleAgent(config)
    
    @staticmethod
    def create_data_analyst_agent() -> SimpleAgent:
        """Create a data analyst agent"""
        config = {
            'model': 'gpt-4',
            'temperature': 0.2,
            'max_tokens': 1500,
            'prompt': """You are a data analyst expert. Your role is to:
- Analyze data and identify patterns
- Provide actionable insights and recommendations
- Create clear visualizations and reports
- Explain complex data in simple terms
- Suggest data-driven strategies

Always base conclusions on solid data analysis."""
        }
        return SimpleAgent(config)


def process_task_simple(task: Task, agent: Agent) -> str:
    """Process a task using the simple agent system"""
    try:
        from agent_config import create_agent_config_from_env_and_db
        
        # Create simple agent configuration from environment and database
        agent_config = create_agent_config_from_env_and_db(agent.id, 'simple')
        agent_config.update({
            'prompt': agent.prompt
        })
        
        # Create simple agent
        simple_agent = SimpleAgent(agent_config)
        
        # Prepare context
        context = {
            'user_info': f"User ID: {task.user_id}",
            'system_status': 'operational'
        }
        
        # Process the task
        result = simple_agent.process_task(task, context)
        
        logger.info(f"Task processed successfully with simple agent: {task.id}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing task {task.id}: {str(e)}")
        return f"Error processing task: {str(e)}"


def create_simple_agent_from_config(agent_config: Dict[str, Any]) -> SimpleAgent:
    """Create a simple agent from configuration"""
    agent_type = agent_config.get('specialization', 'basic')
    
    if agent_type == 'customer_support':
        return SimpleAgentFactory.create_customer_support_agent()
    elif agent_type == 'content_writer':
        return SimpleAgentFactory.create_content_writer_agent()
    elif agent_type == 'data_analyst':
        return SimpleAgentFactory.create_data_analyst_agent()
    else:
        return SimpleAgentFactory.create_basic_agent()
