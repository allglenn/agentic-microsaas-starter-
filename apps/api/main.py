from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel
from database import get_db, engine, Base
from models import User, Agent, Task, ApiCall
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agentic MicroSaaS API",
    description="API for AI-powered microsaas platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    email: str
    name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    prompt: str
    agent_type: Optional[str] = "basic"
    model_type: Optional[str] = "gpt-3.5-turbo"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    specialties: Optional[List[str]] = []

class AgentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    prompt: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    agent_id: str

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    result: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auth functions
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, os.getenv("API_SECRET_KEY", "secret"), algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(user_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Routes
@app.get("/")
async def root():
    return {"message": "Agentic MicroSaaS API", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# User routes
@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Agent routes
@app.post("/agents", response_model=AgentResponse)
async def create_agent(agent: AgentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_agent = Agent(
        name=agent.name,
        description=agent.description,
        prompt=agent.prompt,
        user_id=current_user.id
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

# Get available agent types
@app.get("/agents/types")
async def get_agent_types():
    from agent_configs import get_available_agent_types, get_agent_config
    agent_types = get_available_agent_types()
    return {
        "agent_types": agent_types,
        "configs": {agent_type: get_agent_config(agent_type) for agent_type in agent_types}
    }

@app.get("/agents", response_model=List[AgentResponse])
async def get_agents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agents = db.query(Agent).filter(Agent.user_id == current_user.id).all()
    return agents

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == current_user.id).first()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

# Task routes
@app.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify agent belongs to user
    agent = db.query(Agent).filter(Agent.id == task.agent_id, Agent.user_id == current_user.id).first()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db_task = Task(
        title=task.title,
        description=task.description,
        agent_id=task.agent_id,
        user_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).order_by(Task.created_at.desc()).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Analytics routes
@app.get("/analytics/api-calls")
async def get_api_calls_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    since = datetime.utcnow() - timedelta(days=days)
    calls = db.query(ApiCall).filter(
        ApiCall.user_id == current_user.id,
        ApiCall.created_at >= since
    ).all()
    
    total_calls = len(calls)
    successful_calls = len([c for c in calls if 200 <= c.status < 300])
    avg_duration = sum(c.duration for c in calls) / total_calls if total_calls > 0 else 0
    
    return {
        "total_calls": total_calls,
        "successful_calls": successful_calls,
        "success_rate": (successful_calls / total_calls * 100) if total_calls > 0 else 0,
        "average_duration_ms": round(avg_duration, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)