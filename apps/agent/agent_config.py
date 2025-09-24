"""
Agent Configuration - Choose between Simple and Enhanced Agents
"""
import os
from typing import Dict, Any

# Agent system configuration
AGENT_SYSTEM_CONFIG = {
    # Choose agent system: 'simple' or 'enhanced'
    'default_system': os.getenv('AGENT_SYSTEM', 'enhanced'),
    
    # Fallback configuration
    'fallback_to_simple': True,
    
    # Performance settings (configurable via environment variables)
    'timeout_seconds': int(os.getenv('AGENT_TIMEOUT_SECONDS', '30')),
    'max_retries': int(os.getenv('AGENT_MAX_RETRIES', '3')),
    
    # Model settings (configurable via environment variables)
    'default_model': os.getenv('DEFAULT_MODEL', 'gpt-3.5-turbo'),
    'fallback_model': os.getenv('FALLBACK_MODEL', 'gpt-3.5-turbo'),
    
    # Simple agent settings (configurable via environment variables)
    'simple_agent': {
        'model': os.getenv('SIMPLE_AGENT_MODEL', 'gpt-3.5-turbo'),
        'temperature': float(os.getenv('SIMPLE_AGENT_TEMPERATURE', '0.7')),
        'max_tokens': int(os.getenv('SIMPLE_AGENT_MAX_TOKENS', '1000')),
        'timeout': int(os.getenv('SIMPLE_AGENT_TIMEOUT', '30'))
    },
    
    # Enhanced agent settings (configurable via environment variables)
    'enhanced_agent': {
        'model': os.getenv('ENHANCED_AGENT_MODEL', 'gpt-3.5-turbo'),
        'temperature': float(os.getenv('ENHANCED_AGENT_TEMPERATURE', '0.7')),
        'max_tokens': int(os.getenv('ENHANCED_AGENT_MAX_TOKENS', '1000')),
        'memory_type': os.getenv('ENHANCED_AGENT_MEMORY_TYPE', 'buffer'),
        'tool_timeout': int(os.getenv('ENHANCED_AGENT_TOOL_TIMEOUT', '30'))
    }
}

def get_agent_system() -> str:
    """Get the configured agent system"""
    return AGENT_SYSTEM_CONFIG['default_system']

def should_use_enhanced_agent() -> bool:
    """Check if enhanced agent should be used"""
    return get_agent_system() == 'enhanced'

def should_fallback_to_simple() -> bool:
    """Check if fallback to simple agent is enabled"""
    return AGENT_SYSTEM_CONFIG['fallback_to_simple']

def get_agent_config(system_type: str = None) -> Dict[str, Any]:
    """Get configuration for specific agent system"""
    if system_type is None:
        system_type = get_agent_system()
    
    if system_type == 'simple':
        return AGENT_SYSTEM_CONFIG['simple_agent']
    else:
        return AGENT_SYSTEM_CONFIG['enhanced_agent']

def get_timeout_config() -> Dict[str, int]:
    """Get timeout configuration"""
    return {
        'timeout_seconds': AGENT_SYSTEM_CONFIG['timeout_seconds'],
        'max_retries': AGENT_SYSTEM_CONFIG['max_retries']
    }

def get_agent_settings_from_db(agent_id: str) -> Dict[str, Any]:
    """Get agent settings from database with fallback to environment config"""
    try:
        from database import get_db
        from models import Agent
        
        db = next(get_db())
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        
        if agent:
            # Try to get settings from agent metadata (if stored as JSON)
            # For now, return basic config with agent prompt
            return {
                'model': getattr(agent, 'model', None) or AGENT_SYSTEM_CONFIG['default_model'],
                'temperature': getattr(agent, 'temperature', None) or 0.7,
                'max_tokens': getattr(agent, 'max_tokens', None) or 1000,
                'prompt': agent.prompt
            }
        else:
            return get_agent_config()
            
    except Exception as e:
        print(f"Error getting agent settings from DB: {e}")
        return get_agent_config()
    finally:
        if 'db' in locals():
            db.close()

def create_agent_config_from_env_and_db(agent_id: str = None, system_type: str = None) -> Dict[str, Any]:
    """Create agent configuration combining environment variables and database settings"""
    base_config = get_agent_config(system_type)
    
    if agent_id:
        db_settings = get_agent_settings_from_db(agent_id)
        # Override with database settings if available
        base_config.update(db_settings)
    
    return base_config

def get_model_config() -> Dict[str, str]:
    """Get model configuration"""
    return {
        'default_model': AGENT_SYSTEM_CONFIG['default_model'],
        'fallback_model': AGENT_SYSTEM_CONFIG['fallback_model'],
        'simple_model': AGENT_SYSTEM_CONFIG['simple_agent']['model'],
        'enhanced_model': AGENT_SYSTEM_CONFIG['enhanced_agent']['model']
    }
