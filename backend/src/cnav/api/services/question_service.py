from typing import List, Optional, Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from cnav.database.models.question import Question, AudienceType
from cnav.database.models.clause import Clause
from cnav.api.services import DatabaseService

class QuestionService(DatabaseService):
    """Service for managing questions using database backend"""
    
    def get_all_questions(self) -> List[Question]:
        """Get all questions from database"""
        with self.get_db_session() as session:
            return session.query(Question).options(joinedload(Question.clauses)).all()
    
    def get_question_by_id(self, question_id: Union[int, str]) -> Optional[Question]:
        """Get a specific question by ID"""
        with self.get_db_session() as session:
            if isinstance(question_id, str):
                try:
                    question_id = int(question_id)
                except ValueError:
                    return None
            return session.query(Question).options(joinedload(Question.clauses)).filter(Question.id == question_id).first()
    
    def create_question(self, question_data) -> Question:
        """Create a new question"""
        with self.get_db_session() as session:
            try:
                # Convert Pydantic model to dict if needed
                if hasattr(question_data, 'model_dump'):
                    data = question_data.model_dump()
                else:
                    data = question_data if isinstance(question_data, dict) else question_data.__dict__
                
                # Map API model fields to database model fields
                db_question = Question(
                    name=data.get('question', ''),  # Map 'question' field to 'name'
                    description=data.get('question', ''),  # Use question text as description
                    audience=self._convert_audience(data.get('audience'))
                )
                
                session.add(db_question)
                session.commit()
                session.refresh(db_question)
                return db_question
                
            except IntegrityError as e:
                session.rollback()
                raise ValueError(f"Question creation failed: {str(e)}")
            except Exception as e:
                session.rollback()
                raise Exception(f"Database error: {str(e)}")
    
    def update_question(self, question_id: Union[int, str], question_data) -> Optional[Question]:
        """Update an existing question"""
        with self.get_db_session() as session:
            try:
                if isinstance(question_id, str):
                    question_id = int(question_id)
                
                question = session.query(Question).filter(Question.id == question_id).first()
                if not question:
                    return None
                
                # Convert Pydantic model to dict if needed
                if hasattr(question_data, 'model_dump'):
                    data = question_data.model_dump(exclude_unset=True)
                else:
                    data = question_data if isinstance(question_data, dict) else question_data.__dict__
                
                # Update fields
                if 'question' in data and data['question']:
                    question.name = data['question']
                    question.description = data['question']
                
                if 'audience' in data and data['audience']:
                    # Convert audience to proper format for database
                    audience_enum = self._convert_audience(data['audience'])
                    # Update the audience field directly
                    session.query(Question).filter(Question.id == question_id).update({
                        'audience': audience_enum
                    })
                
                session.commit()
                session.refresh(question)
                return question
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to update question: {str(e)}")
    
    def delete_question(self, question_id: Union[int, str]) -> bool:
        """Delete a question"""
        with self.get_db_session() as session:
            try:
                if isinstance(question_id, str):
                    question_id = int(question_id)
                
                question = session.query(Question).filter(Question.id == question_id).first()
                if not question:
                    return False
                
                session.delete(question)
                session.commit()
                return True
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to delete question: {str(e)}")
    
    def get_questions_by_audience(self, audience: str) -> List[Question]:
        """Get questions filtered by audience"""
        with self.get_db_session() as session:
            audience_enum = self._convert_audience([audience])
            return session.query(Question).filter(Question.audience == audience_enum).all()
    
    def add_clause_to_question(self, question_id: Union[int, str], clause_id: Union[int, str]) -> Optional[Question]:
        """Add a clause to a question's clauses list"""
        with self.get_db_session() as session:
            try:
                if isinstance(question_id, str):
                    question_id = int(question_id)
                if isinstance(clause_id, str):
                    clause_id = int(clause_id)
                
                question = session.query(Question).filter(Question.id == question_id).first()
                clause = session.query(Clause).filter(Clause.id == clause_id).first()
                
                if not question or not clause:
                    return None
                
                question.add_clause(clause)
                session.commit()
                session.refresh(question)
                return question
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to add clause to question: {str(e)}")
    
    def remove_clause_from_question(self, question_id: Union[int, str], clause_id: Union[int, str]) -> Optional[Question]:
        """Remove a clause from a question's clauses list"""
        with self.get_db_session() as session:
            try:
                if isinstance(question_id, str):
                    question_id = int(question_id)
                if isinstance(clause_id, str):
                    clause_id = int(clause_id)
                
                question = session.query(Question).filter(Question.id == question_id).first()
                clause = session.query(Clause).filter(Clause.id == clause_id).first()
                
                if not question or not clause:
                    return None
                
                question.remove_clause(clause)
                session.commit()
                session.refresh(question)
                return question
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to remove clause from question: {str(e)}")
    
    def _convert_audience(self, audience_data) -> AudienceType:
        """Convert audience data to AudienceType enum"""
        if isinstance(audience_data, list) and audience_data:
            # Take the first audience if it's a list
            audience_str = audience_data[0]
        elif isinstance(audience_data, str):
            audience_str = audience_data
        else:
            audience_str = "IT"  # Default fallback
        
        # Map audience strings to enum values
        audience_mapping = {
            "HR": AudienceType.HR,
            "IT": AudienceType.IT,
            "Owner": AudienceType.OWNER,
            "OWNER": AudienceType.OWNER,
        }
        
        return audience_mapping.get(audience_str, AudienceType.IT)
