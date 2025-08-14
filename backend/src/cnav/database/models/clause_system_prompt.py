from cnav.database.models import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.orm import relationship

class ClauseSystemPrompt(Base):
    __tablename__ = "clause_system_prompts"

    id = Column(Integer, primary_key=True)
    clause_id = Column(Integer, ForeignKey("clauses.id"), nullable=False)
    system_prompt_run_id = Column(Integer, ForeignKey("system_prompt_runs.id"), nullable=False)

    system_prompt = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Many-to-one relationship to the Clause
    clause = relationship("Clause", back_populates="clause_system_prompts")
    
    # Many-to-one relationship to the SystemPromptRun
    system_prompt_run = relationship("SystemPromptRun", back_populates="clause_system_prompts")