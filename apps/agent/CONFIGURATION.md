# Agent Configuration Guide

## 🔧 **No More Hardcoded Values!**

All agent settings are now **fully configurable** through environment variables and database settings.

## 📋 **Environment Variables**

### **System Configuration**
```env
# Choose agent system
AGENT_SYSTEM=enhanced          # 'simple' or 'enhanced'

# Performance settings
AGENT_TIMEOUT_SECONDS=30       # Task timeout in seconds
AGENT_MAX_RETRIES=3            # Maximum retry attempts
```

### **Model Configuration**
```env
# Default models
DEFAULT_MODEL=gpt-3.5-turbo    # Default model for all agents
FALLBACK_MODEL=gpt-3.5-turbo   # Fallback model if default fails
```

### **Simple Agent Settings**
```env
SIMPLE_AGENT_MODEL=gpt-3.5-turbo
SIMPLE_AGENT_TEMPERATURE=0.7
SIMPLE_AGENT_MAX_TOKENS=1000
SIMPLE_AGENT_TIMEOUT=30
```

### **Enhanced Agent Settings**
```env
ENHANCED_AGENT_MODEL=gpt-3.5-turbo
ENHANCED_AGENT_TEMPERATURE=0.7
ENHANCED_AGENT_MAX_TOKENS=1000
ENHANCED_AGENT_MEMORY_TYPE=buffer
ENHANCED_AGENT_TOOL_TIMEOUT=30
```

## 🎯 **Configuration Priority**

Settings are applied in this order (highest to lowest priority):

1. **Database Agent Settings** (if agent has custom settings)
2. **Environment Variables** (from .env file)
3. **Default Values** (fallback)

## 🚀 **Quick Setup Examples**

### **Development Environment**
```env
AGENT_SYSTEM=simple
SIMPLE_AGENT_MODEL=gpt-3.5-turbo
SIMPLE_AGENT_TEMPERATURE=0.7
SIMPLE_AGENT_MAX_TOKENS=500
AGENT_TIMEOUT_SECONDS=15
```

### **Production Environment**
```env
AGENT_SYSTEM=enhanced
ENHANCED_AGENT_MODEL=gpt-4
ENHANCED_AGENT_TEMPERATURE=0.3
ENHANCED_AGENT_MAX_TOKENS=2000
AGENT_TIMEOUT_SECONDS=60
```

### **Cost-Optimized Environment**
```env
AGENT_SYSTEM=simple
SIMPLE_AGENT_MODEL=gpt-3.5-turbo
SIMPLE_AGENT_TEMPERATURE=0.5
SIMPLE_AGENT_MAX_TOKENS=300
AGENT_TIMEOUT_SECONDS=20
```

### **High-Quality Environment**
```env
AGENT_SYSTEM=enhanced
ENHANCED_AGENT_MODEL=gpt-4
ENHANCED_AGENT_TEMPERATURE=0.1
ENHANCED_AGENT_MAX_TOKENS=4000
AGENT_TIMEOUT_SECONDS=120
```

## 🔄 **Runtime Configuration**

### **Check Current Settings**
```python
from agent_config import (
    get_agent_system,
    get_agent_config,
    get_model_config,
    get_timeout_config
)

# Get current system
system = get_agent_system()  # 'simple' or 'enhanced'

# Get agent configuration
config = get_agent_config('simple')  # or 'enhanced'

# Get model settings
models = get_model_config()

# Get timeout settings
timeouts = get_timeout_config()
```

### **Create Agent with Custom Config**
```python
from agent_config import create_agent_config_from_env_and_db

# Create config for specific agent
agent_config = create_agent_config_from_env_and_db(
    agent_id="agent-123",
    system_type="enhanced"
)

# Use the config
from enhanced_agents import create_agent_from_config
agent = create_agent_from_config(agent_config)
```

## 🗄️ **Database Configuration**

### **Agent-Specific Settings**
Individual agents can have custom settings stored in the database:

```python
# Agent model with custom settings
agent = Agent(
    name="Custom Agent",
    prompt="You are a specialized agent...",
    model="gpt-4",                    # Custom model
    temperature=0.2,                  # Custom temperature
    max_tokens=2000,                  # Custom max tokens
    agent_type="specialized"
)
```

### **Settings Override**
Database settings override environment variables:

```python
# Environment: SIMPLE_AGENT_TEMPERATURE=0.7
# Database: agent.temperature=0.3
# Result: Uses 0.3 (database wins)
```

## 🔧 **Configuration Functions**

### **Available Functions**
```python
# System configuration
get_agent_system()                    # Get current system
should_use_enhanced_agent()           # Check if enhanced should be used
should_fallback_to_simple()           # Check fallback setting

# Agent configuration
get_agent_config(system_type)         # Get config for system type
get_agent_settings_from_db(agent_id)  # Get settings from database
create_agent_config_from_env_and_db() # Combine env + db settings

# Model configuration
get_model_config()                    # Get all model settings

# Timeout configuration
get_timeout_config()                  # Get timeout settings
```

## 📊 **Configuration Examples**

### **Temperature Settings**
```env
# Creative tasks
SIMPLE_AGENT_TEMPERATURE=0.9
ENHANCED_AGENT_TEMPERATURE=0.8

# Analytical tasks
SIMPLE_AGENT_TEMPERATURE=0.2
ENHANCED_AGENT_TEMPERATURE=0.1

# Balanced tasks
SIMPLE_AGENT_TEMPERATURE=0.7
ENHANCED_AGENT_TEMPERATURE=0.5
```

### **Token Limits**
```env
# Short responses
SIMPLE_AGENT_MAX_TOKENS=300
ENHANCED_AGENT_MAX_TOKENS=500

# Medium responses
SIMPLE_AGENT_MAX_TOKENS=1000
ENHANCED_AGENT_MAX_TOKENS=1500

# Long responses
SIMPLE_AGENT_MAX_TOKENS=2000
ENHANCED_AGENT_MAX_TOKENS=4000
```

### **Timeout Settings**
```env
# Fast responses
AGENT_TIMEOUT_SECONDS=15
SIMPLE_AGENT_TIMEOUT=10

# Standard responses
AGENT_TIMEOUT_SECONDS=30
SIMPLE_AGENT_TIMEOUT=20

# Complex responses
AGENT_TIMEOUT_SECONDS=60
ENHANCED_AGENT_TOOL_TIMEOUT=45
```

## 🚀 **Deployment Configurations**

### **Docker Environment**
```dockerfile
# In Dockerfile
ENV AGENT_SYSTEM=enhanced
ENV ENHANCED_AGENT_MODEL=gpt-4
ENV ENHANCED_AGENT_TEMPERATURE=0.3
```

### **Kubernetes ConfigMap**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-config
data:
  AGENT_SYSTEM: "enhanced"
  ENHANCED_AGENT_MODEL: "gpt-4"
  ENHANCED_AGENT_TEMPERATURE: "0.3"
```

### **Terraform Variables**
```hcl
# In terraform.tfvars
agent_system = "enhanced"
enhanced_agent_model = "gpt-4"
enhanced_agent_temperature = 0.3
```

## 🔍 **Debugging Configuration**

### **Check Current Settings**
```python
import os
from agent_config import AGENT_SYSTEM_CONFIG

# Print all current settings
print("Current Configuration:")
for key, value in AGENT_SYSTEM_CONFIG.items():
    print(f"  {key}: {value}")

# Check environment variables
print("\nEnvironment Variables:")
env_vars = [
    'AGENT_SYSTEM',
    'SIMPLE_AGENT_MODEL',
    'ENHANCED_AGENT_MODEL',
    'AGENT_TIMEOUT_SECONDS'
]
for var in env_vars:
    print(f"  {var}: {os.getenv(var, 'Not set')}")
```

## ✅ **Benefits of Configurable Settings**

1. **No Hardcoded Values** - Everything is configurable
2. **Environment-Specific** - Different settings for dev/staging/prod
3. **Agent-Specific** - Individual agents can have custom settings
4. **Runtime Flexibility** - Change settings without code changes
5. **Easy Testing** - Different configurations for different test scenarios
6. **Cost Control** - Optimize settings for cost vs quality
7. **Performance Tuning** - Adjust timeouts and retries as needed

Your agent system is now **fully configurable** and **production-ready**! 🚀
