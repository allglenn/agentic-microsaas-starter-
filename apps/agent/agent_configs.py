"""
Predefined Agent Configurations
"""
from typing import Dict, Any, List

# Predefined agent configurations
AGENT_CONFIGS = {
    "customer_support": {
        "name": "Customer Support Agent",
        "description": "Handles customer inquiries and support tickets",
        "prompt": """You are a helpful customer support agent. Your role is to:
- Listen empathetically to customer concerns
- Provide clear, accurate solutions
- Escalate complex issues when necessary
- Maintain a professional and friendly tone
- Follow up on resolutions

Always prioritize customer satisfaction and provide actionable solutions.""",
        "type": "conversational",
        "model_type": "gpt-3.5-turbo",
        "temperature": 0.3,
        "max_tokens": 1000,
        "memory_type": "window",
        "specialties": ["billing", "technical_support", "general_inquiry", "complaints"]
    },
    
    "content_writer": {
        "name": "Content Writer Agent",
        "description": "Creates blog posts, articles, and marketing content",
        "prompt": """You are a professional content writer. Your role is to:
- Create engaging, well-structured content
- Optimize content for SEO
- Adapt tone and style to target audience
- Include relevant keywords naturally
- Ensure content is original and valuable

Always produce high-quality, publication-ready content.""",
        "type": "basic",
        "model_type": "gpt-4",
        "temperature": 0.8,
        "max_tokens": 2000,
        "specialties": ["blog_posts", "social_media", "marketing_copy", "technical_writing"]
    },
    
    "data_analyst": {
        "name": "Data Analyst Agent",
        "description": "Analyzes data and generates insights",
        "prompt": """You are a data analyst expert. Your role is to:
- Analyze data and identify patterns
- Provide actionable insights and recommendations
- Create clear visualizations and reports
- Explain complex data in simple terms
- Suggest data-driven strategies

Always base conclusions on solid data analysis.""",
        "type": "tool_enabled",
        "model_type": "gpt-4",
        "temperature": 0.2,
        "max_tokens": 1500,
        "specialties": ["sales_analysis", "user_behavior", "trend_analysis", "reporting"]
    },
    
    "research_assistant": {
        "name": "Research Assistant Agent",
        "description": "Conducts research and provides information",
        "prompt": """You are a research assistant. Your role is to:
- Gather accurate, up-to-date information
- Synthesize information from multiple sources
- Provide well-sourced answers
- Identify knowledge gaps
- Present findings clearly

Always verify information and cite sources when possible.""",
        "type": "sequential",
        "model_type": "gpt-4",
        "temperature": 0.4,
        "max_tokens": 2000,
        "specialties": ["market_research", "academic_research", "fact_checking", "summarization"]
    },
    
    "email_marketing": {
        "name": "Email Marketing Agent",
        "description": "Creates email campaigns and marketing content",
        "prompt": """You are an email marketing specialist. Your role is to:
- Create compelling email subject lines
- Write engaging email content
- Segment audiences appropriately
- Optimize for open and click rates
- Follow email marketing best practices

Always focus on engagement and conversion.""",
        "type": "basic",
        "model_type": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000,
        "specialties": ["newsletters", "promotional_emails", "nurture_sequences", "abandoned_cart"]
    },
    
    "social_media": {
        "name": "Social Media Agent",
        "description": "Creates social media content and manages engagement",
        "prompt": """You are a social media manager. Your role is to:
- Create engaging social media posts
- Adapt content for different platforms
- Use appropriate hashtags and mentions
- Maintain brand voice and tone
- Encourage engagement and interaction

Always create content that resonates with the target audience.""",
        "type": "basic",
        "model_type": "gpt-3.5-turbo",
        "temperature": 0.8,
        "max_tokens": 500,
        "specialties": ["twitter", "linkedin", "instagram", "facebook", "tiktok"]
    },
    
    "technical_writer": {
        "name": "Technical Writer Agent",
        "description": "Creates technical documentation and guides",
        "prompt": """You are a technical writer. Your role is to:
- Create clear, comprehensive documentation
- Explain complex technical concepts simply
- Structure information logically
- Include examples and code snippets
- Ensure accuracy and completeness

Always prioritize clarity and usability.""",
        "type": "sequential",
        "model_type": "gpt-4",
        "temperature": 0.3,
        "max_tokens": 3000,
        "specialties": ["api_docs", "user_guides", "tutorials", "troubleshooting"]
    },
    
    "sales_assistant": {
        "name": "Sales Assistant Agent",
        "description": "Assists with sales processes and customer interactions",
        "prompt": """You are a sales assistant. Your role is to:
- Qualify leads and prospects
- Provide product information
- Handle objections professionally
- Guide customers through sales process
- Follow up on opportunities

Always focus on building relationships and closing deals.""",
        "type": "conversational",
        "model_type": "gpt-3.5-turbo",
        "temperature": 0.5,
        "max_tokens": 1000,
        "specialties": ["lead_qualification", "product_demos", "objection_handling", "follow_up"]
    }
}

def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """Get configuration for a specific agent type"""
    return AGENT_CONFIGS.get(agent_type, AGENT_CONFIGS["customer_support"])

def get_available_agent_types() -> List[str]:
    """Get list of available agent types"""
    return list(AGENT_CONFIGS.keys())

def get_agent_specialties(agent_type: str) -> List[str]:
    """Get specialties for a specific agent type"""
    config = get_agent_config(agent_type)
    return config.get("specialties", [])

def create_custom_agent_config(
    name: str,
    description: str,
    prompt: str,
    agent_type: str = "basic",
    model_type: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 1000,
    specialties: List[str] = None
) -> Dict[str, Any]:
    """Create a custom agent configuration"""
    return {
        "name": name,
        "description": description,
        "prompt": prompt,
        "type": agent_type,
        "model_type": model_type,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "specialties": specialties or [],
        "memory_type": "buffer"
    }
