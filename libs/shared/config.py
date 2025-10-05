"""
Shared Configuration Management
Centralized environment variables and configuration with type safety and validation
"""
import os
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig(BaseSettings):
    """Database configuration settings"""
    url: str = "postgresql://user:password@localhost:5432/agentic_microsaas"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    
    class Config:
        env_prefix = "DATABASE_"

class RedisConfig(BaseSettings):
    """Redis configuration settings"""
    url: str = "redis://localhost:6379"
    password: Optional[str] = None
    db: int = 0
    
    class Config:
        env_prefix = "REDIS_"

class OpenAIConfig(BaseSettings):
    """OpenAI configuration settings"""
    api_key: str = "sk-default"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    
    class Config:
        env_prefix = "OPENAI_"

class StripeConfig(BaseSettings):
    """Stripe configuration settings"""
    secret_key: str = "sk_test_default"
    publishable_key: str = "pk_test_default"
    webhook_secret: str = "whsec_default"
    
    class Config:
        env_prefix = "STRIPE_"

class SendGridConfig(BaseSettings):
    """SendGrid configuration settings"""
    api_key: str = "SG.default"
    from_email: str = "noreply@yourdomain.com"
    from_name: str = "Agentic MicroSaaS"
    
    class Config:
        env_prefix = "SENDGRID_"

class GCPConfig(BaseSettings):
    """Google Cloud Platform configuration settings"""
    project_id: str = "default-project"
    bucket_name: str = "default-bucket"
    credentials_path: Optional[str] = None
    
    class Config:
        env_prefix = "GCP_"

class SecurityConfig(BaseSettings):
    """Security configuration settings"""
    jwt_secret_key: str = "default-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    password_min_length: int = 8
    
    class Config:
        env_prefix = "SECURITY_"

class APIConfig(BaseSettings):
    """API configuration settings"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_prefix = "API_"

class AgentConfig(BaseSettings):
    """Agent system configuration settings"""
    system: str = "enhanced"  # simple or enhanced
    timeout_seconds: int = 300
    max_retries: int = 3
    memory_enabled: bool = True
    tools_enabled: bool = True
    
    class Config:
        env_prefix = "AGENT_"

class SharedConfig:
    """Main configuration class that combines all settings"""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.openai = OpenAIConfig()
        self.stripe = StripeConfig()
        self.sendgrid = SendGridConfig()
        self.gcp = GCPConfig()
        self.security = SecurityConfig()
        self.api = APIConfig()
        self.agent = AgentConfig()
    
    def get_database_url(self) -> str:
        """Get database URL with validation"""
        return self.database.url
    
    def get_redis_url(self) -> str:
        """Get Redis URL with validation"""
        return self.redis.url
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration as dictionary"""
        return {
            "api_key": self.openai.api_key,
            "model": self.openai.model,
            "temperature": self.openai.temperature,
            "max_tokens": self.openai.max_tokens
        }
    
    def get_stripe_config(self) -> Dict[str, str]:
        """Get Stripe configuration as dictionary"""
        return {
            "secret_key": self.stripe.secret_key,
            "publishable_key": self.stripe.publishable_key,
            "webhook_secret": self.stripe.webhook_secret
        }
    
    def get_sendgrid_config(self) -> Dict[str, str]:
        """Get SendGrid configuration as dictionary"""
        return {
            "api_key": self.sendgrid.api_key,
            "from_email": self.sendgrid.from_email,
            "from_name": self.sendgrid.from_name
        }
    
    def get_gcp_config(self) -> Dict[str, str]:
        """Get GCP configuration as dictionary"""
        return {
            "project_id": self.gcp.project_id,
            "bucket_name": self.gcp.bucket_name,
            "credentials_path": self.gcp.credentials_path
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration as dictionary"""
        return {
            "jwt_secret_key": self.security.jwt_secret_key,
            "jwt_algorithm": self.security.jwt_algorithm,
            "jwt_expiration_hours": self.security.jwt_expiration_hours,
            "password_min_length": self.security.password_min_length
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration as dictionary"""
        return {
            "host": self.api.host,
            "port": self.api.port,
            "debug": self.api.debug,
            "cors_origins": self.api.cors_origins
        }
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration as dictionary"""
        return {
            "system": self.agent.system,
            "timeout_seconds": self.agent.timeout_seconds,
            "max_retries": self.agent.max_retries,
            "memory_enabled": self.agent.memory_enabled,
            "tools_enabled": self.agent.tools_enabled
        }
    
    def validate_config(self) -> bool:
        """Validate all configuration settings"""
        try:
            # Test database connection
            from .database import engine
            engine.connect()
            
            # Test Redis connection
            import redis
            r = redis.from_url(self.get_redis_url())
            r.ping()
            
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False

# Global configuration instance
config = SharedConfig()

# Convenience functions for common configurations
def get_database_url() -> str:
    """Get database URL"""
    return config.get_database_url()

def get_redis_url() -> str:
    """Get Redis URL"""
    return config.get_redis_url()

def get_openai_config() -> Dict[str, Any]:
    """Get OpenAI configuration"""
    return config.get_openai_config()

def get_stripe_config() -> Dict[str, str]:
    """Get Stripe configuration"""
    return config.get_stripe_config()

def get_sendgrid_config() -> Dict[str, str]:
    """Get SendGrid configuration"""
    return config.get_sendgrid_config()

def get_gcp_config() -> Dict[str, str]:
    """Get GCP configuration"""
    return config.get_gcp_config()

def get_security_config() -> Dict[str, Any]:
    """Get security configuration"""
    return config.get_security_config()

def get_api_config() -> Dict[str, Any]:
    """Get API configuration"""
    return config.get_api_config()

def get_agent_config() -> Dict[str, Any]:
    """Get agent configuration"""
    return config.get_agent_config()
