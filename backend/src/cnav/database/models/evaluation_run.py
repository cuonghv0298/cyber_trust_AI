from cnav.database.models import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.orm import relationship

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True)
    
    # Reference to the system prompt run used
    system_prompt_run_id = Column(Integer, ForeignKey("system_prompt_runs.id"), nullable=False)
    
    # Run metadata
    run_name = Column(String, nullable=True)  # Optional human-readable name
    description = Column(String, nullable=True)
    version = Column(String, nullable=True)  # e.g., "eval-v3.0"
    
    # Execution metadata
    status = Column(String, nullable=False, default="running")  # running, completed, failed
    started_at = Column(DateTime, nullable=False, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Optional: Evaluation configuration (could be JSON field later)
    # evaluation_metrics = Column(JSON, nullable=True)
    # comparison_baseline_run_id = Column(Integer, ForeignKey("evaluation_runs.id"), nullable=True)
    # performance_thresholds = Column(JSON, nullable=True)
    
    # Relationships
    system_prompt_run = relationship("SystemPromptRun", back_populates="evaluation_runs")
    clause_evaluations = relationship("ClauseEvaluation", back_populates="evaluation_run")
    question_evaluations = relationship("QuestionEvaluation", back_populates="evaluation_run")
    
    def __repr__(self):
        return f"<EvaluationRun(id={self.id}, version='{self.version}', status='{self.status}')>"
    
    @classmethod
    def create_new_run(cls, system_prompt_run_id, run_name=None, description=None, version=None):
        """Helper to create a new evaluation run"""
        return cls(
            system_prompt_run_id=system_prompt_run_id,
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
    def clause_evaluation_count(self):
        """Get the number of clause evaluations in this run"""
        return len(self.clause_evaluations)
        
    @property
    def question_evaluation_count(self):
        """Get the number of question evaluations in this run"""
        return len(self.question_evaluations)
        
    @property
    def total_evaluation_count(self):
        """Get the total number of evaluations in this run"""
        return self.clause_evaluation_count + self.question_evaluation_count
        
    def get_used_prompts(self):
        """Get all system prompts used in this evaluation run"""
        return self.system_prompt_run.clause_system_prompts 