"""
Enhanced Agent System with Advanced LangChain Features
"""
import os
import sys
import logging
from typing import Dict, Any, List, Optional
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, ConversationChain, SequentialChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate

# Add project root to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from libs.shared.database import get_db
from libs.shared.models import Task, Agent
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.schema import Document
# These imports are already handled above
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class EnhancedAgent:
    """Enhanced agent with advanced LangChain capabilities"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.agent_config = agent_config
        self.llm = self._initialize_llm()
        self.memory = self._initialize_memory()
        self.tools = self._initialize_tools()
        self.chain = self._initialize_chain()
        
    def _initialize_llm(self):
        """Initialize LLM based on agent configuration"""
        model_type = self.agent_config.get('model_type', 'gpt-3.5-turbo')
        temperature = self.agent_config.get('temperature', 0.7)
        max_tokens = self.agent_config.get('max_tokens', 1000)
        
        if model_type.startswith('gpt-4'):
            return ChatOpenAI(
                model_name=model_type,
                temperature=temperature,
                max_tokens=max_tokens,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            return OpenAI(
                model_name=model_type,
                temperature=temperature,
                max_tokens=max_tokens,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
    
    def _initialize_memory(self):
        """Initialize memory based on agent type"""
        memory_type = self.agent_config.get('memory_type', 'buffer')
        
        if memory_type == 'window':
            return ConversationBufferWindowMemory(k=5)
        else:
            return ConversationBufferMemory()
    
    def _initialize_tools(self):
        """Initialize tools for the agent"""
        tools = []
        
        # Database search tool
        tools.append(Tool(
            name="Database Search",
            func=self._search_database,
            description="Search the database for information about users, tasks, or agents"
        ))
        
        # Calculator tool
        tools.append(Tool(
            name="Calculator",
            func=self._calculate,
            description="Perform mathematical calculations"
        ))
        
        # Email tool
        tools.append(Tool(
            name="Send Email",
            func=self._send_email,
            description="Send emails to users"
        ))
        
        # File operations tool
        tools.append(Tool(
            name="File Operations",
            func=self._file_operations,
            description="Read, write, or manipulate files"
        ))
        
        return tools
    
    def _initialize_chain(self):
        """Initialize the appropriate chain based on agent type"""
        agent_type = self.agent_config.get('type', 'basic')
        
        if agent_type == 'conversational':
            return ConversationChain(
                llm=self.llm,
                memory=self.memory,
                verbose=True
            )
        elif agent_type == 'tool_enabled':
            return initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                memory=self.memory
            )
        elif agent_type == 'sequential':
            return self._create_sequential_chain()
        else:
            return self._create_basic_chain()
    
    def _create_basic_chain(self):
        """Create a basic LLM chain"""
        prompt_template = PromptTemplate(
            input_variables=["task_title", "task_description", "agent_prompt", "context"],
            template="""
            You are an AI agent with the following characteristics:
            {agent_prompt}
            
            Task to complete:
            Title: {task_title}
            Description: {task_description}
            
            Context: {context}
            
            Please provide a detailed response to complete this task.
            """
        )
        
        return LLMChain(llm=self.llm, prompt=prompt_template)
    
    def _create_sequential_chain(self):
        """Create a sequential chain for multi-step reasoning"""
        # Step 1: Analyze the task
        analysis_prompt = PromptTemplate(
            input_variables=["task"],
            template="""
            Analyze this task and break it down into steps:
            Task: {task}
            
            Provide:
            1. Main objective
            2. Required steps
            3. Potential challenges
            4. Success criteria
            """
        )
        
        analysis_chain = LLMChain(
            llm=self.llm,
            prompt=analysis_prompt,
            output_key="analysis"
        )
        
        # Step 2: Execute the task
        execution_prompt = PromptTemplate(
            input_variables=["task", "analysis"],
            template="""
            Based on this analysis, execute the task:
            
            Task: {task}
            Analysis: {analysis}
            
            Provide a detailed solution.
            """
        )
        
        execution_chain = LLMChain(
            llm=self.llm,
            prompt=execution_prompt,
            output_key="result"
        )
        
        return SequentialChain(
            chains=[analysis_chain, execution_chain],
            input_variables=["task"],
            output_variables=["analysis", "result"]
        )
    
    def process_task(self, task: Task, context: Optional[Dict] = None) -> str:
        """Process a task using the enhanced agent"""
        try:
            # Prepare context
            context_str = self._prepare_context(context) if context else "No additional context"
            
            # Process based on chain type
            if hasattr(self.chain, 'run'):
                # Basic or sequential chain
                if isinstance(self.chain, SequentialChain):
                    result = self.chain.run(task=f"{task.title}: {task.description}")
                    return result.get('result', str(result))
                else:
                    return self.chain.run(
                        task_title=task.title,
                        task_description=task.description or "",
                        agent_prompt=self.agent_config.get('prompt', ''),
                        context=context_str
                    )
            else:
                # Agent with tools
                return self.chain.run(
                    input=f"Task: {task.title}\nDescription: {task.description}\nContext: {context_str}"
                )
                
        except Exception as e:
            logger.error(f"Error processing task {task.id}: {str(e)}")
            return f"Error processing task: {str(e)}"
    
    def _prepare_context(self, context: Dict) -> str:
        """Prepare context information for the agent"""
        context_parts = []
        
        if 'user_info' in context:
            context_parts.append(f"User: {context['user_info']}")
        
        if 'previous_tasks' in context:
            context_parts.append(f"Previous tasks: {context['previous_tasks']}")
        
        if 'system_status' in context:
            context_parts.append(f"System status: {context['system_status']}")
        
        return "\n".join(context_parts)
    
    # Tool functions
    def _search_database(self, query: str) -> str:
        """Search the database for information"""
        try:
            db = next(get_db())
            # Implement database search logic
            # This is a simplified example
            return f"Database search results for: {query}"
        except Exception as e:
            return f"Database search error: {str(e)}"
        finally:
            db.close()
    
    def _calculate(self, expression: str) -> str:
        """Perform mathematical calculations"""
        try:
            # Simple calculation (in production, use a proper math parser)
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    def _send_email(self, message: str) -> str:
        """Send email (placeholder implementation)"""
        # In production, integrate with email service
        return f"Email sent: {message}"
    
    def _file_operations(self, operation: str) -> str:
        """Perform file operations (placeholder implementation)"""
        # In production, implement file operations
        return f"File operation completed: {operation}"


class DocumentAwareAgent(EnhancedAgent):
    """Agent that can process and retrieve information from documents"""
    
    def __init__(self, agent_config: Dict[str, Any], documents_path: Optional[str] = None):
        super().__init__(agent_config)
        self.vectorstore = None
        if documents_path:
            self._load_documents(documents_path)
    
    def _load_documents(self, documents_path: str):
        """Load and process documents for retrieval"""
        try:
            # Load documents
            loader = TextLoader(documents_path)
            documents = loader.load()
            
            # Split documents
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            texts = text_splitter.split_documents(documents)
            
            # Create embeddings
            embeddings = OpenAIEmbeddings()
            self.vectorstore = FAISS.from_documents(texts, embeddings)
            
            # Create retrieval chain
            self.retrieval_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever()
            )
            
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
    
    def process_with_documents(self, query: str) -> str:
        """Process query with document retrieval"""
        if self.vectorstore:
            return self.retrieval_chain.run(query)
        else:
            return "No documents loaded for retrieval"


class SpecializedAgentFactory:
    """Factory for creating specialized agents"""
    
    @staticmethod
    def create_customer_support_agent() -> EnhancedAgent:
        """Create a customer support agent"""
        config = {
            'type': 'conversational',
            'model_type': 'gpt-3.5-turbo',
            'temperature': 0.3,
            'memory_type': 'window',
            'prompt': 'You are a helpful customer support agent. Be empathetic, professional, and solution-oriented.'
        }
        return EnhancedAgent(config)
    
    @staticmethod
    def create_content_writer_agent() -> EnhancedAgent:
        """Create a content writer agent"""
        config = {
            'type': 'basic',
            'model_type': 'gpt-4',
            'temperature': 0.8,
            'prompt': 'You are a professional content writer. Create engaging, well-structured content that is SEO-optimized.'
        }
        return EnhancedAgent(config)
    
    @staticmethod
    def create_data_analyst_agent() -> EnhancedAgent:
        """Create a data analyst agent"""
        config = {
            'type': 'tool_enabled',
            'model_type': 'gpt-4',
            'temperature': 0.2,
            'prompt': 'You are a data analyst expert. Provide insights, analysis, and recommendations based on data.'
        }
        return EnhancedAgent(config)
    
    @staticmethod
    def create_research_agent() -> DocumentAwareAgent:
        """Create a research agent with document capabilities"""
        config = {
            'type': 'basic',
            'model_type': 'gpt-4',
            'temperature': 0.4,
            'prompt': 'You are a research assistant. Provide accurate, well-sourced information and analysis.'
        }
        return DocumentAwareAgent(config)


def create_agent_from_config(agent_config: Dict[str, Any]) -> EnhancedAgent:
    """Create an agent from configuration"""
    agent_type = agent_config.get('specialization', 'general')
    
    if agent_type == 'customer_support':
        return SpecializedAgentFactory.create_customer_support_agent()
    elif agent_type == 'content_writer':
        return SpecializedAgentFactory.create_content_writer_agent()
    elif agent_type == 'data_analyst':
        return SpecializedAgentFactory.create_data_analyst_agent()
    elif agent_type == 'research':
        return SpecializedAgentFactory.create_research_agent()
    else:
        return EnhancedAgent(agent_config)
