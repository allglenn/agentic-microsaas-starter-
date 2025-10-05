# Agent Service (Enhanced LangChain)

Advanced AI agent processing service using Celery with enhanced LangChain capabilities, memory, tools, and specialized agent types.

## 🚀 Enhanced Features

- **Advanced LangChain Integration**: Memory, tools, chains, and agents
- **Shared Models Architecture** - Uses `libs/shared/models.py` for all database models
- **Specialized Agent Types**: Customer support, content writer, data analyst, etc.
- **Memory Management**: Conversation history and context awareness
- **Tool Integration**: Database search, calculations, email, file operations
- **Document Processing**: Vector search and retrieval capabilities
- **Multi-Step Reasoning**: Sequential chains for complex tasks
- **Agent Factory**: Pre-configured specialized agents

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Task Queue    │    │  Enhanced Agent │    │   LangChain     │
│   (Celery)      │───▶│   System        │───▶│   Components    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       ▼
         │                       │              ┌─────────────────┐
         │                       │              │   Memory &      │
         │                       │              │   Context       │
         │                       │              └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Database      │    │   Tools &       │    │   OpenAI API    │
│   (PostgreSQL)  │    │   Functions     │    │   (GPT-4/3.5)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🏗️ Shared Models Architecture

This agent service uses the **shared models architecture** where all database models are defined in `libs/shared/models.py`:

```python
# Import pattern used in all agent files
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from libs.shared.database import get_db, engine, Base
from libs.shared.models import User, Agent, Task, # ... other models as needed
```

### Key Models Used by Agent Service
- **User** - User accounts and authentication
- **Agent** - Agent configurations and settings
- **Task** - Task execution and status tracking
- **ApiCall** - API usage monitoring and metrics

> **📋 [Complete Shared Models Documentation](../../SHARED_MODELS_ARCHITECTURE.md)**

## 🤖 Agent Types

### **1. Customer Support Agent**
- **Type**: Conversational with memory
- **Model**: GPT-3.5-turbo
- **Features**: Empathetic responses, issue escalation, follow-up
- **Specialties**: Billing, technical support, complaints

### **2. Content Writer Agent**
- **Type**: Basic chain
- **Model**: GPT-4
- **Features**: SEO optimization, audience adaptation, creative writing
- **Specialties**: Blog posts, social media, marketing copy

### **3. Data Analyst Agent**
- **Type**: Tool-enabled
- **Model**: GPT-4
- **Features**: Data analysis, insights, recommendations
- **Specialties**: Sales analysis, user behavior, reporting

### **4. Research Assistant Agent**
- **Type**: Sequential chain
- **Model**: GPT-4
- **Features**: Multi-step research, source verification
- **Specialties**: Market research, fact checking, summarization

## 🔧 Enhanced Capabilities

### **Memory Management**
```python
# Conversation memory
memory = ConversationBufferWindowMemory(k=5)  # Remember last 5 interactions

# Context-aware processing
context = {
    'user_info': 'User ID: 123',
    'previous_tasks': 'Recent billing inquiry',
    'system_status': 'operational'
}
```

### **Tool Integration**
```python
tools = [
    Tool(name="Database Search", func=search_database),
    Tool(name="Calculator", func=calculate),
    Tool(name="Send Email", func=send_email),
    Tool(name="File Operations", func=file_operations)
]
```

### **Multi-Step Reasoning**
```python
# Sequential chain for complex tasks
sequential_chain = SequentialChain(
    chains=[analysis_chain, execution_chain],
    input_variables=["task"],
    output_variables=["analysis", "result"]
)
```

### **Document Processing**
```python
# Vector search and retrieval
vectorstore = FAISS.from_documents(documents, embeddings)
retrieval_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)
```

## 📊 Agent Configuration

### **Basic Configuration**
```python
agent_config = {
    'name': 'Customer Support Agent',
    'type': 'conversational',
    'model_type': 'gpt-3.5-turbo',
    'temperature': 0.3,
    'max_tokens': 1000,
    'memory_type': 'window',
    'prompt': 'You are a helpful customer support agent...'
}
```

### **Advanced Configuration**
```python
advanced_config = {
    'type': 'tool_enabled',
    'model_type': 'gpt-4',
    'temperature': 0.2,
    'tools': ['database', 'calculator', 'email'],
    'memory_type': 'buffer',
    'specialties': ['data_analysis', 'reporting']
}
```

## 🚀 Usage Examples

### **Creating Specialized Agents**
```python
# Customer support agent
support_agent = SpecializedAgentFactory.create_customer_support_agent()

# Content writer agent
writer_agent = SpecializedAgentFactory.create_content_writer_agent()

# Data analyst agent
analyst_agent = SpecializedAgentFactory.create_data_analyst_agent()
```

### **Processing Tasks**
```python
# Process with context
result = agent.process_task(task, context={
    'user_info': 'VIP customer',
    'previous_tasks': 'Recent purchase',
    'system_status': 'operational'
})
```

### **Document-Aware Processing**
```python
# Research agent with documents
research_agent = DocumentAwareAgent(config, documents_path="docs/")
result = research_agent.process_with_documents("What are the latest AI trends?")
```

## 🔄 Task Processing Flow

### **1. Task Creation**
```python
task = Task(
    title="Customer Inquiry",
    description="Billing issue with recent charge",
    agent_id="customer-support-agent",
    user_id="user123"
)
```

### **2. Agent Selection**
```python
# System automatically selects appropriate agent
agent = create_agent_from_config(agent_config)
```

### **3. Context Preparation**
```python
context = {
    'user_info': get_user_info(task.user_id),
    'previous_tasks': get_recent_tasks(task.user_id),
    'system_status': get_system_status()
}
```

### **4. Task Processing**
```python
# Enhanced processing with memory and tools
result = agent.process_task(task, context)
```

### **5. Result Storage**
```python
task.status = "completed"
task.result = result
db.commit()
```

## 🛠️ Development

### **Setup**
```bash
cd apps/agent
pip install -r requirements.txt
```

### **Start Worker**
```bash
celery -A worker worker --loglevel=info
```

### **Test Agent**
```python
from enhanced_agents import SpecializedAgentFactory

# Create and test agent
agent = SpecializedAgentFactory.create_customer_support_agent()
result = agent.process_task(test_task)
print(result)
```

## 📈 Performance Features

### **Memory Optimization**
- Conversation buffer with configurable window size
- Context compression for long conversations
- Memory persistence across sessions

### **Tool Efficiency**
- Lazy loading of tools
- Caching of tool results
- Parallel tool execution

### **Model Selection**
- Automatic model selection based on task complexity
- Cost optimization with model switching
- Performance monitoring per model

## 🔒 Security Features

### **Input Validation**
- Task content sanitization
- Prompt injection prevention
- Rate limiting per user

### **Tool Security**
- Sandboxed tool execution
- Permission-based tool access
- Audit logging for tool usage

### **Data Protection**
- Sensitive data filtering
- Context encryption
- Secure memory storage

## 📊 Monitoring

### **Agent Performance**
```python
# Track agent metrics
metrics = {
    'success_rate': 0.95,
    'avg_response_time': '2.3 minutes',
    'user_satisfaction': 4.8,
    'tool_usage': {'database': 45, 'email': 12}
}
```

### **Memory Usage**
```python
# Monitor memory consumption
memory_stats = {
    'conversation_count': 150,
    'memory_size': '2.3MB',
    'hit_rate': 0.87
}
```

## 🚀 Deployment

### **Local Development**
```bash
make agent.dev
```

### **Production**
```bash
# Start multiple workers
celery -A worker worker --loglevel=info --concurrency=4

# With supervisor
supervisord -c supervisord.conf
```

### **Docker**
```bash
docker build -t agent-service .
docker run agent-service
```

## 🔧 Configuration

### **Environment Variables**
```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agentic_microsaas

# Redis
REDIS_URL=redis://localhost:6379/0

# Agent Settings
DEFAULT_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
DEFAULT_TEMPERATURE=0.7
```

### **Agent Settings**
```python
# Global agent settings
AGENT_SETTINGS = {
    'default_model': 'gpt-3.5-turbo',
    'max_tokens': 1000,
    'temperature': 0.7,
    'memory_window': 5,
    'tool_timeout': 30
}
```

## 🎯 Best Practices

### **Agent Design**
- Use appropriate model for task complexity
- Implement proper error handling
- Monitor performance metrics
- Regular prompt optimization

### **Memory Management**
- Limit conversation history
- Compress old memories
- Implement memory cleanup
- Monitor memory usage

### **Tool Integration**
- Validate tool inputs
- Handle tool failures gracefully
- Implement tool timeouts
- Log tool usage

The enhanced LangChain integration makes your agentic microsaas significantly more powerful and capable of handling complex, multi-step tasks with memory, context awareness, and tool integration! 🚀