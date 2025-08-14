from typing import List, Optional, Union
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from cnav.database.models import Base
from cnav.database.models.question import Question, AudienceType, question_clause_association
from cnav.database.models.clause import Clause
from cnav.api.services import DatabaseService

class ProvisionService(DatabaseService):
    """Service for managing provisions (clauses) using database backend"""
    
    def get_all_provisions(self) -> List[Clause]:
        """Get all clauses from database"""
        with self.get_db_session() as session:
            return session.query(Clause).options(joinedload(Clause.questions)).all()
    
    def get_provision_by_id(self, provision_id: Union[int, str]) -> Optional[Clause]:
        """Get a specific clause by ID"""
        with self.get_db_session() as session:
            if isinstance(provision_id, str):
                try:
                    provision_id = int(provision_id)
                except ValueError:
                    # Try to find by full_identifier (e.g., "1.4a")
                    return session.query(Clause).options(joinedload(Clause.questions)).filter(
                        Clause.clause_identifier == provision_id
                    ).first()
            return session.query(Clause).options(joinedload(Clause.questions)).filter(Clause.id == provision_id).first()
    
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