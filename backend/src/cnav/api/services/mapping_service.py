from typing import List, Optional, Union
from sqlalchemy.exc import IntegrityError

from cnav.database.models import Base
from cnav.database.models.question import Question, AudienceType, question_clause_association
from cnav.database.models.clause import Clause
from cnav.api.services import DatabaseService, QuestionService, ProvisionService

class MappingService(DatabaseService):
    """Service to manage the many-to-many relationship between questions and clauses"""
    
    def __init__(self):
        self.question_service = QuestionService()
        self.provision_service = ProvisionService()
    
    def create_mapping(self, question_id: Union[int, str], provision_id: Union[int, str]) -> bool:
        """Create a bidirectional mapping between question and clause"""
        try:
            # Add clause to question
            question = self.question_service.add_clause_to_question(question_id, provision_id)
            if not question:
                raise ValueError(f"Question with ID {question_id} or Provision with ID {provision_id} not found")
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to create mapping: {str(e)}")
    
    def delete_mapping(self, question_id: Union[int, str], provision_id: Union[int, str]) -> bool:
        """Delete a bidirectional mapping between question and clause"""
        try:
            # Remove clause from question (this automatically handles the bidirectional relationship)
            question = self.question_service.remove_clause_from_question(question_id, provision_id)
            return question is not None
            
        except Exception as e:
            raise Exception(f"Failed to delete mapping: {str(e)}")
    
    def get_provisions_for_question(self, question_id: Union[int, str]) -> List[Clause]:
        """Get all clauses mapped to a question"""
        question = self.question_service.get_question_by_id(question_id)
        if not question:
            return []
        
        return question.clauses
    
    def get_questions_for_provision(self, provision_id: Union[int, str]) -> List[Question]:
        """Get all questions mapped to a clause"""
        provision = self.provision_service.get_provision_by_id(provision_id)
        if not provision:
            return []
        
        return provision.questions 