"""
Shared OpenAI Configuration
Centralized OpenAI setup and configuration with error handling and validation
"""
import openai
import os
import sys
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import asyncio
from .config import get_openai_config
from .logging_config import get_shared_logger

# Initialize logger
logger = get_shared_logger()

class OpenAIError(Exception):
    """Custom OpenAI error with additional context"""
    def __init__(self, message: str, error_code: Optional[str] = None, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.error_code = error_code
        self.original_error = original_error

class OpenAIClient:
    """Centralized OpenAI client with configuration and error handling"""
    
    def __init__(self):
        self.config = get_openai_config()
        self.api_key = self.config["api_key"]
        self.model = self.config["model"]
        self.temperature = self.config["temperature"]
        self.max_tokens = self.config["max_tokens"]
        
        # Configure OpenAI client
        openai.api_key = self.api_key
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate OpenAI configuration"""
        if not self.api_key or self.api_key == "sk-default":
            logger.warning("OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable.")
            return False
        
        if not self.model:
            logger.warning("OpenAI model is not configured.")
            return False
        
        if not 0 <= self.temperature <= 2:
            logger.warning("Temperature must be between 0 and 2.")
            return False
        
        if not 1 <= self.max_tokens <= 4000:
            logger.warning("Max tokens must be between 1 and 4000.")
            return False
        
        return True
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        try:
            models = openai.Model.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create chat completion with error handling and logging"""
        try:
            # Use provided parameters or defaults
            model = model or self.model
            temperature = temperature or self.temperature
            max_tokens = max_tokens or self.max_tokens
            
            # Log the request
            logger.info(
                f"Creating chat completion with model {model}",
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                user_id=user_id,
                message_count=len(messages)
            )
            
            # Make the API call
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response data
            result = {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
            # Log the response
            logger.info(
                f"Chat completion successful",
                model=model,
                tokens_used=result["usage"]["total_tokens"],
                user_id=user_id
            )
            
            return result
            
        except openai.error.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise OpenAIError("Rate limit exceeded. Please try again later.", "rate_limit", e)
        
        except openai.error.InvalidRequestError as e:
            logger.error(f"Invalid OpenAI request: {e}")
            raise OpenAIError("Invalid request parameters.", "invalid_request", e)
        
        except openai.error.AuthenticationError as e:
            logger.error(f"OpenAI authentication failed: {e}")
            raise OpenAIError("Authentication failed. Please check your API key.", "auth_error", e)
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise OpenAIError(f"OpenAI API error: {str(e)}", "api_error", e)
    
    def create_embedding(
        self,
        text: str,
        model: str = "text-embedding-ada-002",
        user_id: Optional[str] = None
    ) -> List[float]:
        """Create embedding with error handling and logging"""
        try:
            logger.info(
                f"Creating embedding for text",
                model=model,
                text_length=len(text),
                user_id=user_id
            )
            
            response = openai.Embedding.create(
                model=model,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            logger.info(
                f"Embedding created successfully",
                model=model,
                embedding_dimension=len(embedding),
                user_id=user_id
            )
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            raise OpenAIError(f"Failed to create embedding: {str(e)}", "embedding_error", e)
    
    def create_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create text completion with error handling and logging"""
        try:
            model = model or self.model
            temperature = temperature or self.temperature
            max_tokens = max_tokens or self.max_tokens
            
            logger.info(
                f"Creating text completion",
                model=model,
                prompt_length=len(prompt),
                user_id=user_id
            )
            
            response = openai.Completion.create(
                model=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            result = {
                "text": response.choices[0].text,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.info(
                f"Text completion successful",
                model=model,
                tokens_used=result["usage"]["total_tokens"],
                user_id=user_id
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create text completion: {e}")
            raise OpenAIError(f"Failed to create text completion: {str(e)}", "completion_error", e)
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        try:
            model_info = openai.Model.retrieve(model)
            return {
                "id": model_info.id,
                "object": model_info.object,
                "created": model_info.created,
                "owned_by": model_info.owned_by
            }
        except Exception as e:
            logger.error(f"Failed to get model info for {model}: {e}")
            return {}
    
    def validate_model(self, model: str) -> bool:
        """Validate if a model is available and accessible"""
        try:
            available_models = self.get_available_models()
            return model in available_models
        except Exception as e:
            logger.error(f"Failed to validate model {model}: {e}")
            return False

class OpenAIEmbeddingService:
    """Service for creating and managing embeddings"""
    
    def __init__(self):
        self.client = OpenAIClient()
        self.default_model = "text-embedding-ada-002"
    
    def create_embedding(self, text: str, model: Optional[str] = None, user_id: Optional[str] = None) -> List[float]:
        """Create embedding for text"""
        return self.client.create_embedding(text, model or self.default_model, user_id)
    
    def create_embeddings_batch(self, texts: List[str], model: Optional[str] = None, user_id: Optional[str] = None) -> List[List[float]]:
        """Create embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            try:
                embedding = self.create_embedding(text, model, user_id)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to create embedding for text: {e}")
                embeddings.append([])  # Add empty embedding for failed texts
        return embeddings
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            import numpy as np
            
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0

class OpenAIChatService:
    """Service for chat completions and conversations"""
    
    def __init__(self):
        self.client = OpenAIClient()
    
    def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create chat completion"""
        return self.client.create_chat_completion(messages, model, temperature, max_tokens, user_id)
    
    def create_conversation(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a conversation with system prompt and history"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return self.create_chat_completion(messages, model, user_id=user_id)
    
    def create_simple_chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Create a simple chat completion and return just the content"""
        messages = [{"role": "user", "content": prompt}]
        response = self.create_chat_completion(messages, model, user_id=user_id)
        return response["content"]

# Global instances
openai_client = OpenAIClient()
embedding_service = OpenAIEmbeddingService()
chat_service = OpenAIChatService()

# Convenience functions
def create_chat_completion(messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
    """Create chat completion using global client"""
    return openai_client.create_chat_completion(messages, **kwargs)

def create_embedding(text: str, model: str = "text-embedding-ada-002", **kwargs) -> List[float]:
    """Create embedding using global service"""
    return embedding_service.create_embedding(text, model, **kwargs)

def create_simple_chat(prompt: str, **kwargs) -> str:
    """Create simple chat completion using global service"""
    return chat_service.create_simple_chat(prompt, **kwargs)

def validate_model(model: str) -> bool:
    """Validate if a model is available"""
    return openai_client.validate_model(model)

def get_available_models() -> List[str]:
    """Get list of available models"""
    return openai_client.get_available_models()
