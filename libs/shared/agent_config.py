"""
Shared Agent Configuration
Centralized agent system configuration with environment variables and database fallback
"""
import os
from typing import Dict, Any, Optional
from .config import get_agent_config, get_openai_config
from .database import get_db
from .models import Agent

class AgentSystemConfig:
    """Agent system configuration class"""
    
    def __init__(self):
        self.config = get_agent_config()
        self.openai_config = get_openai_config()
        
        # Agent system configuration
        self.system = self.config.get("system", "enhanced")
        self.timeout_seconds = self.config.get("timeout_seconds", 300)
        self.max_retries = self.config.get("max_retries", 3)
        self.memory_enabled = self.config.get("memory_enabled", True)
        self.tools_enabled = self.config.get("tools_enabled", True)
        
        # Model configuration
        self.default_model = self.openai_config.get("model", "gpt-4")
        self.temperature = self.openai_config.get("temperature", 0.7)
        self.max_tokens = self.openai_config.get("max_tokens", 2000)
        
        # Simple agent settings
        self.simple_agent_config = {
            "model": os.getenv("SIMPLE_AGENT_MODEL", self.default_model),
            "temperature": float(os.getenv("SIMPLE_AGENT_TEMPERATURE", str(self.temperature))),
            "max_tokens": int(os.getenv("SIMPLE_AGENT_MAX_TOKENS", str(self.max_tokens))),
            "timeout": int(os.getenv("SIMPLE_AGENT_TIMEOUT", "30"))
        }
        
        # Enhanced agent settings
        self.enhanced_agent_config = {
            "model": os.getenv("ENHANCED_AGENT_MODEL", self.default_model),
            "temperature": float(os.getenv("ENHANCED_AGENT_TEMPERATURE", str(self.temperature))),
            "max_tokens": int(os.getenv("ENHANCED_AGENT_MAX_TOKENS", str(self.max_tokens))),
            "memory_type": os.getenv("ENHANCED_AGENT_MEMORY_TYPE", "buffer"),
            "tool_timeout": int(os.getenv("ENHANCED_AGENT_TOOL_TIMEOUT", "30"))
        }
    
    def get_agent_system(self) -> str:
        """Get the configured agent system"""
        return self.system
    
    def should_use_enhanced_agent(self) -> bool:
        """Check if enhanced agent should be used"""
        return self.system == "enhanced"
    
    def should_fallback_to_simple(self) -> bool:
        """Check if fallback to simple agent is enabled"""
        return os.getenv("AGENT_FALLBACK_TO_SIMPLE", "true").lower() == "true"
    
    def get_agent_config(self, system_type: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for specific agent system"""
        if system_type is None:
            system_type = self.get_agent_system()
        
        if system_type == "simple":
            return self.simple_agent_config.copy()
        else:
            return self.enhanced_agent_config.copy()
    
    def get_timeout_config(self) -> Dict[str, int]:
        """Get timeout configuration"""
        return {
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries
        }
    
    def get_agent_settings_from_db(self, agent_id: str) -> Dict[str, Any]:
        """Get agent settings from database with fallback to environment config"""
        try:
            db = next(get_db())
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            
            if agent:
                # Try to get settings from agent metadata (if stored as JSON)
                # For now, return basic config with agent prompt
                return {
                    "model": getattr(agent, "model", None) or self.default_model,
                    "temperature": getattr(agent, "temperature", None) or self.temperature,
                    "max_tokens": getattr(agent, "max_tokens", None) or self.max_tokens,
                    "prompt": agent.prompt
                }
            else:
                return self.get_agent_config()
                
        except Exception as e:
            print(f"Error getting agent settings from DB: {e}")
            return self.get_agent_config()
        finally:
            if "db" in locals():
                db.close()
    
    def create_agent_config_from_env_and_db(self, agent_id: Optional[str] = None, system_type: Optional[str] = None) -> Dict[str, Any]:
        """Create agent configuration combining environment variables and database settings"""
        base_config = self.get_agent_config(system_type)
        
        if agent_id:
            db_settings = self.get_agent_settings_from_db(agent_id)
            # Override with database settings if available
            base_config.update(db_settings)
        
        return base_config
    
    def get_model_config(self) -> Dict[str, str]:
        """Get model configuration"""
        return {
            "default_model": self.default_model,
            "fallback_model": os.getenv("FALLBACK_MODEL", self.default_model),
            "simple_model": self.simple_agent_config["model"],
            "enhanced_model": self.enhanced_agent_config["model"]
        }
    
    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory configuration for enhanced agents"""
        return {
            "enabled": self.memory_enabled,
            "type": self.enhanced_agent_config.get("memory_type", "buffer"),
            "max_tokens": self.enhanced_agent_config.get("max_tokens", 2000)
        }
    
    def get_tools_config(self) -> Dict[str, Any]:
        """Get tools configuration for enhanced agents"""
        return {
            "enabled": self.tools_enabled,
            "timeout": self.enhanced_agent_config.get("tool_timeout", 30)
        }
    
    def validate_agent_config(self, config: Dict[str, Any]) -> bool:
        """Validate agent configuration"""
        required_fields = ["model", "temperature", "max_tokens"]
        
        for field in required_fields:
            if field not in config:
                return False
        
        # Validate temperature range
        if not 0 <= config["temperature"] <= 2:
            return False
        
        # Validate max_tokens
        if not 1 <= config["max_tokens"] <= 4000:
            return False
        
        return True
    
    def get_agent_system_info(self) -> Dict[str, Any]:
        """Get comprehensive agent system information"""
        return {
            "system": self.get_agent_system(),
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "memory_enabled": self.memory_enabled,
            "tools_enabled": self.tools_enabled,
            "models": self.get_model_config(),
            "simple_config": self.simple_agent_config,
            "enhanced_config": self.enhanced_agent_config
        }

# Global agent configuration instance
agent_config = AgentSystemConfig()

# Convenience functions
def get_agent_system() -> str:
    """Get the configured agent system"""
    return agent_config.get_agent_system()

def should_use_enhanced_agent() -> bool:
    """Check if enhanced agent should be used"""
    return agent_config.should_use_enhanced_agent()

def should_fallback_to_simple() -> bool:
    """Check if fallback to simple agent is enabled"""
    return agent_config.should_fallback_to_simple()

def get_agent_config_for_system(system_type: Optional[str] = None) -> Dict[str, Any]:
    """Get configuration for specific agent system"""
    return agent_config.get_agent_config(system_type)

def get_timeout_config() -> Dict[str, int]:
    """Get timeout configuration"""
    return agent_config.get_timeout_config()

def get_agent_settings_from_db(agent_id: str) -> Dict[str, Any]:
    """Get agent settings from database with fallback to environment config"""
    return agent_config.get_agent_settings_from_db(agent_id)

def create_agent_config_from_env_and_db(agent_id: Optional[str] = None, system_type: Optional[str] = None) -> Dict[str, Any]:
    """Create agent configuration combining environment variables and database settings"""
    return agent_config.create_agent_config_from_env_and_db(agent_id, system_type)

def get_model_config() -> Dict[str, str]:
    """Get model configuration"""
    return agent_config.get_model_config()

def get_memory_config() -> Dict[str, Any]:
    """Get memory configuration for enhanced agents"""
    return agent_config.get_memory_config()

def get_tools_config() -> Dict[str, Any]:
    """Get tools configuration for enhanced agents"""
    return agent_config.get_tools_config()

def validate_agent_config(config: Dict[str, Any]) -> bool:
    """Validate agent configuration"""
    return agent_config.validate_agent_config(config)

def get_agent_system_info() -> Dict[str, Any]:
    """Get comprehensive agent system information"""
    return agent_config.get_agent_system_info()
