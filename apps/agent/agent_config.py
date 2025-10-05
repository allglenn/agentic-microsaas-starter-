"""
Agent Configuration - Choose between Simple and Enhanced Agents
DEPRECATED: Use libs.shared.agent_config instead
"""
import sys
import os
from typing import Dict, Any
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import from shared agent configuration
from libs.shared.agent_config import (
    get_agent_system as shared_get_agent_system,
    should_use_enhanced_agent as shared_should_use_enhanced_agent,
    should_fallback_to_simple as shared_should_fallback_to_simple,
    get_agent_config_for_system,
    get_timeout_config as shared_get_timeout_config,
    get_agent_settings_from_db as shared_get_agent_settings_from_db,
    create_agent_config_from_env_and_db as shared_create_agent_config_from_env_and_db,
    get_model_config as shared_get_model_config
)

# Legacy compatibility - redirect to shared functions
def get_agent_system() -> str:
    """Get the configured agent system"""
    return shared_get_agent_system()

def should_use_enhanced_agent() -> bool:
    """Check if enhanced agent should be used"""
    return shared_should_use_enhanced_agent()

def should_fallback_to_simple() -> bool:
    """Check if fallback to simple agent is enabled"""
    return shared_should_fallback_to_simple()

def get_agent_config(system_type: str = None) -> Dict[str, Any]:
    """Get configuration for specific agent system"""
    return get_agent_config_for_system(system_type)

def get_timeout_config() -> Dict[str, int]:
    """Get timeout configuration"""
    return shared_get_timeout_config()

def get_agent_settings_from_db(agent_id: str) -> Dict[str, Any]:
    """Get agent settings from database with fallback to environment config"""
    return shared_get_agent_settings_from_db(agent_id)

def create_agent_config_from_env_and_db(agent_id: str = None, system_type: str = None) -> Dict[str, Any]:
    """Create agent configuration combining environment variables and database settings"""
    return shared_create_agent_config_from_env_and_db(agent_id, system_type)

def get_model_config() -> Dict[str, str]:
    """Get model configuration"""
    return shared_get_model_config()