from cnav.database.models import Base
from sqlalchemy import (
    Column,
    Boolean,
    Float,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.ext.hybrid import hybrid_property

class QuestionEvaluation(Base):
    __tablename__ = "question_evaluations"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    self_assessment_answer_id = Column(Integer, ForeignKey("self_assessment_answers.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    clause_evaluation_id = Column(Integer, ForeignKey("clause_evaluations.id"), nullable=False)
    evaluation_run_id = Column(Integer, ForeignKey("evaluation_runs.id"), nullable=False)

    compliance_rationale = Column(String, nullable=False)
    compliance_confident_score = Column(Float, nullable=False)
    compliance_result = Column(Boolean, nullable=False)

    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Many-to-one relationship to the Question
    question = relationship("Question", back_populates="question_evaluations")

    # Many-to-one relationship to the Organization
    organization = relationship("Organization", back_populates="question_evaluations")

    # Many-to-one relationship to the SelfAssessmentAnswer
    self_assessment_answer = relationship("SelfAssessmentAnswer", back_populates="question_evaluations")

    # Many-to-one relationship to the ClauseEvaluation
    clause_evaluation = relationship("ClauseEvaluation", back_populates="question_evaluations")
    
    # Many-to-one relationship to the EvaluationRun
    evaluation_run = relationship("EvaluationRun", back_populates="question_evaluations")

    def __repr__(self):
        return f"<QuestionEvaluation(id={self.id}, question_id={self.question_id}, evaluation={self.evaluation})>"