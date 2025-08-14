from cnav.database.models import Base
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.ext.hybrid import hybrid_property

class Clause(Base):
    __tablename__ = "clauses"

    # Primary key - auto-incrementing integer
    id = Column(Integer, primary_key=True)
    
    # Foreign key to requirement category
    category_id = Column(Integer, ForeignKey("requirement_categories.id"), nullable=False)
    
    # Clause identifier within the category (e.g., "4a", "1b", "2c")
    clause_identifier = Column(String(10), nullable=False)
    
    # Basic clause information
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationship to category
    category = relationship("RequirementCategory", back_populates="clauses")
    
    # Many-to-many relationship with questions
    questions = relationship(
        "Question",
        secondary="question_clause_mapping",
        back_populates="clauses"
    )
    
    # Many-to-many relationship with self assessment answers
    self_assessment_answers = relationship(
        "SelfAssessmentAnswer",
        secondary="self_assessment_answer_clause_mapping",
        back_populates="clauses"
    )
    
    # One-to-many relationship with clause system prompts
    clause_system_prompts = relationship("ClauseSystemPrompt", back_populates="clause")
    
    # One-to-many relationship with clause evaluations
    clause_evaluations = relationship("ClauseEvaluation", back_populates="clause")
    
    # Ensure uniqueness of clause_identifier within each category
    __table_args__ = (
        UniqueConstraint('category_id', 'clause_identifier', name='unique_clause_per_category'),
    )
    
    @hybrid_property
    def full_identifier(self):
        """
        Generate the full identifier in format: category_id.clause_identifier
        Example: "1.4a", "2.1b", "3.2c"
        """
        return f"{self.category_id}.{self.clause_identifier}"
    
    @full_identifier.expression
    def full_identifier_expr(cls):
        """
        SQL expression for full_identifier - allows querying by full identifier
        """
        return func.concat(func.cast(cls.category_id, String), '.', cls.clause_identifier)
    
    def __repr__(self):
        return f"<Clause(id={self.id}, full_identifier='{self.full_identifier}', name='{self.name}')>"
    
    @classmethod
    def get_by_full_identifier(cls, session, full_identifier):
        """
        Get a clause by its full identifier (e.g., "1.4a")
        """
        try:
            category_id, clause_id = full_identifier.split('.', 1)
            return session.query(cls).filter(
                cls.category_id == int(category_id),
                cls.clause_identifier == clause_id
            ).first()
        except ValueError:
            return None
    
    @classmethod
    def create_from_identifier(cls, session, full_identifier, name, description):
        """
        Create a clause from a full identifier string
        """
        try:
            category_id, clause_id = full_identifier.split('.', 1)
            return cls(
                category_id=int(category_id),
                clause_identifier=clause_id,
                name=name,
                description=description
            )
        except ValueError:
            raise ValueError(f"Invalid identifier format: {full_identifier}. Expected format: 'category_id.clause_id'")
    
    def add_question(self, question):
        """Add a question to this clause"""
        if question not in self.questions:
            self.questions.append(question)
    
    def remove_question(self, question):
        """Remove a question from this clause"""
        if question in self.questions:
            self.questions.remove(question)
    
    def get_questions_by_audience(self, audience_type):
        """Get all questions for this clause filtered by audience type"""
        from .question import AudienceType
        if isinstance(audience_type, str):
            audience_type = AudienceType(audience_type)
        return [q for q in self.questions if q.audience == audience_type]