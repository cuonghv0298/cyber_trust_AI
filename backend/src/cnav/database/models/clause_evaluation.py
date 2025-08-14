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
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.ext.hybrid import hybrid_property

class ClauseEvaluation(Base):
    __tablename__ = "clause_evaluations"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    clause_id = Column(Integer, ForeignKey("clauses.id"), nullable=False)
    evaluation_run_id = Column(Integer, ForeignKey("evaluation_runs.id"), nullable=False)

    compliance_rationale = Column(String, nullable=False)
    compliance_confident_score = Column(Float, nullable=False)
    compliance_result = Column(Boolean, nullable=False)

    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Many-to-one relationship to the Organization
    organization = relationship("Organization", back_populates="clause_evaluations")

    # Many-to-one relationship to the Clause
    clause = relationship("Clause", back_populates="clause_evaluations")
    
    # Many-to-one relationship to the EvaluationRun
    evaluation_run = relationship("EvaluationRun", back_populates="clause_evaluations")

    # One-to-many relationship to the QuestionEvaluation
    question_evaluations = relationship("QuestionEvaluation", back_populates="clause_evaluation")