import openai
import os
import sys
from typing import Dict, Any
import logging
from sqlalchemy.orm import Session

# Add project root to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from libs.shared.database import get_db
from libs.shared.models import Task, Agent

logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def process_task(task: Task, agent: Agent, use_enhanced: bool = True) -> str:
    """Process a task using either simple or enhanced agent system"""
    try:
        if use_enhanced:
            return _process_with_enhanced_agent(task, agent)
        else:
            return _process_with_simple_agent(task, agent)
            
    except Exception as e:
        logger.error(f"Error processing task {task.id}: {str(e)}")
        return f"Error processing task: {str(e)}"

def _process_with_enhanced_agent(task: Task, agent: Agent) -> str:
    """Process task with enhanced LangChain agent"""
    try:
        from enhanced_agents import create_agent_from_config
        from agent_config import create_agent_config_from_env_and_db
        
        # Create agent configuration from environment and database
        agent_config = create_agent_config_from_env_and_db(agent.id, 'enhanced')
        agent_config.update({
            'prompt': agent.prompt,
            'type': 'basic'
        })
        
        # Create enhanced agent
        enhanced_agent = create_agent_from_config(agent_config)
        
        # Prepare context
        context = {
            'user_info': f"User ID: {task.user_id}",
            'system_status': 'operational'
        }
        
        # Process the task
        result = enhanced_agent.process_task(task, context)
        
        logger.info(f"Task processed successfully with enhanced agent: {task.id}")
        return result
        
    except ImportError:
        logger.warning("Enhanced agents not available, falling back to simple agent")
        return _process_with_simple_agent(task, agent)
    except Exception as e:
        logger.error(f"Error with enhanced agent: {str(e)}")
        return _process_with_simple_agent(task, agent)

def _process_with_simple_agent(task: Task, agent: Agent) -> str:
    """Process task with simple agent (no LangChain)"""
    try:
        from simple_agent import process_task_simple
        return process_task_simple(task, agent)
        
    except ImportError:
        logger.error("Simple agent not available")
        return "Error: No agent system available"
    except Exception as e:
        logger.error(f"Error with simple agent: {str(e)}")
        return f"Error processing task: {str(e)}"

def update_task_status(task_id: str, status: str):
    """Update task status in database"""
    try:
        db = next(get_db())
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = status
            db.commit()
            logger.info(f"Task status updated to {status}: {task_id}")
        else:
            logger.error(f"Task not found for status update: {task_id}")
    except Exception as e:
        logger.error(f"Error updating task status: {str(e)}")
    finally:
        db.close()

def create_agent_task(task_data: Dict[str, Any]) -> str:
    """Create a new agent task and queue it for processing"""
    try:
        db = next(get_db())
        
        # Create task
        task = Task(
            title=task_data["title"],
            description=task_data.get("description"),
            agent_id=task_data["agent_id"],
            user_id=task_data["user_id"],
            status="pending"
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Queue task for processing
        from worker import process_agent_task
        process_agent_task.delay(task.id)
        
        logger.info(f"Task created and queued: {task.id}")
        return task.id
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise
    finally:
        db.close()
