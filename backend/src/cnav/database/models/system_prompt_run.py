from cnav.database.models import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func
)
from sqlalchemy.orm import relationship

class SystemPromptRun(Base):
    __tablename__ = "system_prompt_runs"

    id = Column(Integer, primary_key=True)
    
    # Run metadata
    run_name = Column(String, nullable=True)  # Optional human-readable name
    description = Column(String, nullable=True)
    version = Column(String, nullable=True)  # e.g., "prompts-v2.1"
    
    # Execution metadata
    status = Column(String, nullable=False, default="running")  # running, completed, failed
    started_at = Column(DateTime, nullable=False, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Optional: Generation configuration (could be JSON field later)
    # model_name = Column(String, nullable=True)
    # temperature = Column(Float, nullable=True)
    # generation_config = Column(JSON, nullable=True)
    
    # Relationships
    clause_system_prompts = relationship("ClauseSystemPrompt", back_populates="system_prompt_run")
    evaluation_runs = relationship("EvaluationRun", back_populates="system_prompt_run")
    
    def __repr__(self):
        return f"<SystemPromptRun(id={self.id}, version='{self.version}', status='{self.status}')>"
    
    @classmethod
    def create_new_run(cls, run_name=None, description=None, version=None):
        """Helper to create a new system prompt generation run"""
        return cls(
            run_name=run_name,
            description=description,
            version=version,
            status="running"
        )
    
    def mark_completed(self):
        """Mark the run as completed"""
        self.status = "completed"
        self.completed_at = func.now()
    
    def mark_failed(self):
        """Mark the run as failed"""
        self.status = "failed"
        self.completed_at = func.now()
        
    @property
    def prompt_count(self):
        """Get the number of prompts generated in this run"""
        return len(self.clause_system_prompts)
        
    @property  
    def evaluation_count(self):
        """Get the number of evaluation runs that used these prompts"""
        return len(self.evaluation_runs) 