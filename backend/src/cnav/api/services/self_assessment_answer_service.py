from typing import List, Optional, Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from cnav.database.models.self_assessment_answer import SelfAssessmentAnswer
from cnav.database.models.organization import Organization
from cnav.database.models.question import Question
from cnav.database.models.clause import Clause
from cnav.api.services import DatabaseService


class SelfAssessmentAnswerService(DatabaseService):
    """Service for managing self-assessment answers using database backend"""
    
    def get_all_answers(self) -> List[SelfAssessmentAnswer]:
        """Get all self-assessment answers from database"""
        with self.get_db_session() as session:
            return session.query(SelfAssessmentAnswer).options(
                joinedload(SelfAssessmentAnswer.clauses),
                joinedload(SelfAssessmentAnswer.organization),
                joinedload(SelfAssessmentAnswer.question)
            ).all()
    
    def get_answer_by_id(self, answer_id: Union[int, str]) -> Optional[SelfAssessmentAnswer]:
        """Get a specific self-assessment answer by ID"""
        with self.get_db_session() as session:
            if isinstance(answer_id, str):
                try:
                    answer_id = int(answer_id)
                except ValueError:
                    return None
            return session.query(SelfAssessmentAnswer).options(
                joinedload(SelfAssessmentAnswer.clauses),
                joinedload(SelfAssessmentAnswer.organization),
                joinedload(SelfAssessmentAnswer.question)
            ).filter(SelfAssessmentAnswer.id == answer_id).first()
    
    def create_answer(self, answer_data) -> SelfAssessmentAnswer:
        """Create a new self-assessment answer"""
        with self.get_db_session() as session:
            try:
                # Convert Pydantic model to dict if needed
                if hasattr(answer_data, 'model_dump'):
                    data = answer_data.model_dump()
                else:
                    data = answer_data if isinstance(answer_data, dict) else answer_data.__dict__
                
                # Validate that organization and question exist
                organization = session.query(Organization).filter(
                    Organization.id == data.get('organization_id')
                ).first()
                if not organization:
                    raise ValueError(f"Organization with ID {data.get('organization_id')} not found")
                
                question = session.query(Question).filter(
                    Question.id == data.get('question_id')
                ).first()
                if not question:
                    raise ValueError(f"Question with ID {data.get('question_id')} not found")
                
                # Create the answer
                db_answer = SelfAssessmentAnswer(
                    organization_id=data.get('organization_id'),
                    question_id=data.get('question_id'),
                    answer=data.get('answer', '')
                )
                
                session.add(db_answer)
                session.flush()  # Flush to get the ID
                
                # Associate clauses if provided
                clause_ids = data.get('clause_ids', [])
                if clause_ids:
                    clauses = session.query(Clause).filter(Clause.id.in_(clause_ids)).all()
                    db_answer.clauses = clauses
                
                session.commit()
                session.refresh(db_answer)
                return db_answer
                
            except IntegrityError as e:
                session.rollback()
                raise ValueError(f"Self-assessment answer creation failed: {str(e)}")
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to create self-assessment answer: {str(e)}")

    def update_answer(self, answer_id: Union[int, str], answer_data) -> Optional[SelfAssessmentAnswer]:
        """Update an existing self-assessment answer"""
        with self.get_db_session() as session:
            try:
                if isinstance(answer_id, str):
                    try:
                        answer_id = int(answer_id)
                    except ValueError:
                        return None
                
                answer = session.query(SelfAssessmentAnswer).filter(
                    SelfAssessmentAnswer.id == answer_id
                ).first()
                if not answer:
                    return None
                
                # Convert Pydantic model to dict if needed
                if hasattr(answer_data, 'model_dump'):
                    data = answer_data.model_dump(exclude_unset=True)
                else:
                    data = answer_data if isinstance(answer_data, dict) else answer_data.__dict__
                
                # Validate organization and question if they're being updated
                if 'organization_id' in data and data['organization_id'] is not None:
                    organization = session.query(Organization).filter(
                        Organization.id == data['organization_id']
                    ).first()
                    if not organization:
                        raise ValueError(f"Organization with ID {data['organization_id']} not found")
                
                if 'question_id' in data and data['question_id'] is not None:
                    question = session.query(Question).filter(
                        Question.id == data['question_id']
                    ).first()
                    if not question:
                        raise ValueError(f"Question with ID {data['question_id']} not found")
                
                # Update basic fields
                for field, value in data.items():
                    if field != 'clause_ids' and hasattr(answer, field) and value is not None:
                        setattr(answer, field, value)
                
                # Update clause associations if provided
                if 'clause_ids' in data and data['clause_ids'] is not None:
                    clause_ids = data['clause_ids']
                    if clause_ids:
                        clauses = session.query(Clause).filter(Clause.id.in_(clause_ids)).all()
                        answer.clauses = clauses
                    else:
                        answer.clauses = []
                
                session.commit()
                session.refresh(answer)
                return answer
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to update self-assessment answer: {str(e)}")
    
    def delete_answer(self, answer_id: Union[int, str]) -> bool:
        """Delete a self-assessment answer"""
        with self.get_db_session() as session:
            try:
                if isinstance(answer_id, str):
                    try:
                        answer_id = int(answer_id)
                    except ValueError:
                        return False
                
                answer = session.query(SelfAssessmentAnswer).filter(
                    SelfAssessmentAnswer.id == answer_id
                ).first()
                if not answer:
                    return False
                
                session.delete(answer)
                session.commit()
                return True
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to delete self-assessment answer: {str(e)}")
    
    def get_answers_by_organization(self, organization_id: Union[int, str]) -> List[SelfAssessmentAnswer]:
        """Get all self-assessment answers for a specific organization"""
        with self.get_db_session() as session:
            if isinstance(organization_id, str):
                try:
                    organization_id = int(organization_id)
                except ValueError:
                    return []
            
            return session.query(SelfAssessmentAnswer).options(
                joinedload(SelfAssessmentAnswer.clauses),
                joinedload(SelfAssessmentAnswer.organization),
                joinedload(SelfAssessmentAnswer.question)
            ).filter(SelfAssessmentAnswer.organization_id == organization_id).all()
    
    def get_answers_by_question(self, question_id: Union[int, str]) -> List[SelfAssessmentAnswer]:
        """Get all self-assessment answers for a specific question"""
        with self.get_db_session() as session:
            if isinstance(question_id, str):
                try:
                    question_id = int(question_id)
                except ValueError:
                    return []
            
            return session.query(SelfAssessmentAnswer).options(
                joinedload(SelfAssessmentAnswer.clauses),
                joinedload(SelfAssessmentAnswer.organization),
                joinedload(SelfAssessmentAnswer.question)
            ).filter(SelfAssessmentAnswer.question_id == question_id).all()
    
    def get_answers_by_clause(self, clause_id: Union[int, str]) -> List[SelfAssessmentAnswer]:
        """Get all self-assessment answers associated with a specific clause"""
        with self.get_db_session() as session:
            if isinstance(clause_id, str):
                try:
                    clause_id = int(clause_id)
                except ValueError:
                    return []
            
            return session.query(SelfAssessmentAnswer).options(
                joinedload(SelfAssessmentAnswer.clauses),
                joinedload(SelfAssessmentAnswer.organization),
                joinedload(SelfAssessmentAnswer.question)
            ).join(SelfAssessmentAnswer.clauses).filter(Clause.id == clause_id).all()
    
    def search_answers_by_text(self, search_text: str) -> List[SelfAssessmentAnswer]:
        """Search self-assessment answers by text content"""
        with self.get_db_session() as session:
            return session.query(SelfAssessmentAnswer).options(
                joinedload(SelfAssessmentAnswer.clauses),
                joinedload(SelfAssessmentAnswer.organization),
                joinedload(SelfAssessmentAnswer.question)
            ).filter(SelfAssessmentAnswer.answer.ilike(f"%{search_text}%")).all()
    
    def get_answers_with_filters(
        self, 
        organization_id: Optional[int] = None,
        question_id: Optional[int] = None,
        clause_id: Optional[int] = None,
        answer_contains: Optional[str] = None
    ) -> List[SelfAssessmentAnswer]:
        """Get self-assessment answers with multiple filters"""
        with self.get_db_session() as session:
            query = session.query(SelfAssessmentAnswer).options(
                joinedload(SelfAssessmentAnswer.clauses),
                joinedload(SelfAssessmentAnswer.organization),
                joinedload(SelfAssessmentAnswer.question)
            )
            
            if organization_id is not None:
                query = query.filter(SelfAssessmentAnswer.organization_id == organization_id)
            
            if question_id is not None:
                query = query.filter(SelfAssessmentAnswer.question_id == question_id)
            
            if clause_id is not None:
                query = query.join(SelfAssessmentAnswer.clauses).filter(Clause.id == clause_id)
            
            if answer_contains is not None:
                query = query.filter(SelfAssessmentAnswer.answer.ilike(f"%{answer_contains}%"))
            
            return query.all()