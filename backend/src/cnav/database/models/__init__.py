from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models to ensure proper relationship resolution
from .requirement_category import RequirementCategory
from .question import Question, question_clause_association
from .clause import Clause
from .organization import Organization
from .self_assessment_answer import SelfAssessmentAnswer, self_assessment_answer_clause_mapping
from .system_prompt_run import SystemPromptRun
from .evaluation_run import EvaluationRun
from .question_evaluation import QuestionEvaluation
from .clause_evaluation import ClauseEvaluation
from .clause_system_prompt import ClauseSystemPrompt

__all__ = [
    'Base',
    'RequirementCategory',
    'Question',
    'Clause',
    'Organization',
    'SelfAssessmentAnswer',
    'SystemPromptRun',
    'EvaluationRun',
    'QuestionEvaluation',
    'ClauseEvaluation', 
    'ClauseSystemPrompt',
    'question_clause_association',
    'self_assessment_answer_clause_mapping'
]