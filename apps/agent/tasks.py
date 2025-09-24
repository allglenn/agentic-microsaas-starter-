import openai
import os
from typing import Dict, Any
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import logging
from database import get_db
from models import Task, Agent
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def process_task(task: Task, agent: Agent) -> str:
    """Process a task using the specified agent"""
    try:
        # Initialize LLM
        llm = OpenAI(
            temperature=0.7,
            max_tokens=1000,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create prompt template
        prompt_template = PromptTemplate(
            input_variables=["task_title", "task_description", "agent_prompt"],
            template="""
            You are an AI agent with the following characteristics:
            {agent_prompt}
            
            Task to complete:
            Title: {task_title}
            Description: {task_description}
            
            Please provide a detailed response to complete this task.
            """
        )
        
        # Create chain
        chain = LLMChain(llm=llm, prompt=prompt_template)
        
        # Process the task
        result = chain.run(
            task_title=task.title,
            task_description=task.description or "",
            agent_prompt=agent.prompt
        )
        
        logger.info(f"Task processed successfully: {task.id}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing task {task.id}: {str(e)}")
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
