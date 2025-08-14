"""
Database-backed service layer for CNAV API

This module provides service classes that interact with the SQLAlchemy database models
instead of JSON files, providing proper database CRUD operations.
"""

from typing import List, Optional, Union
from sqlalchemy.exc import IntegrityError

from cnav.database.models import Base
from cnav.database.models.question import Question, AudienceType, question_clause_association
from cnav.database.models.clause import Clause
from cnav.database.connection import get_sync_session, init_sync_database

# Initialize database on module import
init_sync_database()

class DatabaseService:
    """Base class for database services with session management"""
    
    def get_db_session(self):
        """Get a database session using the connection manager"""
        return get_sync_session()


class QuestionService(DatabaseService):
    """Service for managing questions using database backend"""
    
    def get_all_questions(self) -> List[Question]:
        """Get all questions from database"""
        with self.get_db_session() as session:
            return session.query(Question).all()
    
    def get_question_by_id(self, question_id: Union[int, str]) -> Optional[Question]:
        """Get a specific question by ID"""
        with self.get_db_session() as session:
            if isinstance(question_id, str):
                try:
                    question_id = int(question_id)
                except ValueError:
                    return None
            return session.query(Question).filter(Question.id == question_id).first()
    
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


class ProvisionService(DatabaseService):
    """Service for managing provisions (clauses) using database backend"""
    
    def get_all_provisions(self) -> List[Clause]:
        """Get all clauses from database"""
        with self.get_db_session() as session:
            return session.query(Clause).all()
    
    def get_provision_by_id(self, provision_id: Union[int, str]) -> Optional[Clause]:
        """Get a specific clause by ID"""
        with self.get_db_session() as session:
            if isinstance(provision_id, str):
                try:
                    provision_id = int(provision_id)
                except ValueError:
                    # Try to find by full_identifier (e.g., "1.4a")
                    return session.query(Clause).filter(
                        Clause.clause_identifier == provision_id
                    ).first()
            return session.query(Clause).filter(Clause.id == provision_id).first()
    
    def create_provision(self, provision_data) -> Clause:
        """Create a new clause"""
        with self.get_db_session() as session:
            try:
                # Convert Pydantic model to dict if needed
                if hasattr(provision_data, 'model_dump'):
                    data = provision_data.model_dump()
                else:
                    data = provision_data if isinstance(provision_data, dict) else provision_data.__dict__
                
                # Create clause from the data
                db_clause = Clause(
                    category_id=1,  # Default category, you might want to make this configurable
                    clause_identifier=data.get('id', ''), # Changed from _id to id
                    name=data.get('provision', ''),
                    description=data.get('provision', '')
                )
                
                session.add(db_clause)
                session.commit()
                session.refresh(db_clause)
                return db_clause
                
            except IntegrityError as e:
                session.rollback()
                raise ValueError(f"Provision creation failed: {str(e)}")
            except Exception as e:
                session.rollback()
                raise Exception(f"Database error: {str(e)}")
    
    def update_provision(self, provision_id: Union[int, str], provision_data) -> Optional[Clause]:
        """Update an existing clause"""
        with self.get_db_session() as session:
            try:
                if isinstance(provision_id, str):
                    try:
                        provision_id = int(provision_id)
                    except ValueError:
                        # Handle clause_identifier format
                        clause = session.query(Clause).filter(
                            Clause.clause_identifier == provision_id
                        ).first()
                        if not clause:
                            return None
                        provision_id = clause.id
                
                clause = session.query(Clause).filter(Clause.id == provision_id).first()
                if not clause:
                    return None
                
                # Convert Pydantic model to dict if needed
                if hasattr(provision_data, 'model_dump'):
                    data = provision_data.model_dump(exclude_unset=True)
                else:
                    data = provision_data if isinstance(provision_data, dict) else provision_data.__dict__
                
                # Update fields
                if 'provision' in data and data['provision']:
                    clause.name = data['provision']
                    clause.description = data['provision']
                
                session.commit()
                session.refresh(clause)
                return clause
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to update provision: {str(e)}")
    
    def delete_provision(self, provision_id: Union[int, str]) -> bool:
        """Delete a clause"""
        with self.get_db_session() as session:
            try:
                if isinstance(provision_id, str):
                    try:
                        provision_id = int(provision_id)
                    except ValueError:
                        # Handle clause_identifier format
                        clause = session.query(Clause).filter(
                            Clause.clause_identifier == provision_id
                        ).first()
                        if not clause:
                            return False
                        provision_id = clause.id
                
                clause = session.query(Clause).filter(Clause.id == provision_id).first()
                if not clause:
                    return False
                
                session.delete(clause)
                session.commit()
                return True
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to delete provision: {str(e)}")
    
    def add_question_to_provision(self, provision_id: Union[int, str], question_id: Union[int, str]) -> Optional[Clause]:
        """Add a question to a clause's questions list"""
        with self.get_db_session() as session:
            try:
                if isinstance(provision_id, str):
                    try:
                        provision_id = int(provision_id)
                    except ValueError:
                        clause = session.query(Clause).filter(
                            Clause.clause_identifier == provision_id
                        ).first()
                        if not clause:
                            return None
                        provision_id = clause.id
                
                if isinstance(question_id, str):
                    question_id = int(question_id)
                
                clause = session.query(Clause).filter(Clause.id == provision_id).first()
                question = session.query(Question).filter(Question.id == question_id).first()
                
                if not clause or not question:
                    return None
                
                clause.add_question(question)
                session.commit()
                session.refresh(clause)
                return clause
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to add question to provision: {str(e)}")
    
    def remove_question_from_provision(self, provision_id: Union[int, str], question_id: Union[int, str]) -> Optional[Clause]:
        """Remove a question from a clause's questions list"""
        with self.get_db_session() as session:
            try:
                if isinstance(provision_id, str):
                    try:
                        provision_id = int(provision_id)
                    except ValueError:
                        clause = session.query(Clause).filter(
                            Clause.clause_identifier == provision_id
                        ).first()
                        if not clause:
                            return None
                        provision_id = clause.id
                
                if isinstance(question_id, str):
                    question_id = int(question_id)
                
                clause = session.query(Clause).filter(Clause.id == provision_id).first()
                question = session.query(Question).filter(Question.id == question_id).first()
                
                if not clause or not question:
                    return None
                
                clause.remove_question(question)
                session.commit()
                session.refresh(clause)
                return clause
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to remove question from provision: {str(e)}")


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