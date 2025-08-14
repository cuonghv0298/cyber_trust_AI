"""
Adapter functions to convert between database models and API response models

This module handles the conversion between SQLAlchemy database models and 
Pydantic API models, bridging the different field naming and structure conventions.
"""

from typing import List, Optional
from cnav.database.models import Question as DBQuestion, Clause as DBClause
from cnav.database.models.organization import Organization as DBOrganization
from cnav.database.models.self_assessment_answer import SelfAssessmentAnswer as DBSelfAssessmentAnswer
from cnav.database.models.question import AudienceType
from .models import QuestionResponse, ProvisionResponse, OrganizationResponse, SelfAssessmentAnswerResponse


def db_question_to_api(db_question: DBQuestion) -> QuestionResponse:
    """Convert database Question model to API QuestionResponse model"""
    
    # Convert audience enum to list of strings (API expects list)
    audience_list = [db_question.audience.value] if hasattr(db_question, 'audience') and db_question.audience is not None else []
    
    # Get clause IDs (provisions in API terminology)
    provision_ids = [str(clause.id) for clause in db_question.clauses] if hasattr(db_question, 'clauses') and db_question.clauses is not None else []
    
    return QuestionResponse(
        id=str(db_question.id),  # type: ignore
        question=str(db_question.name),  # Map 'name' to 'question'
        audience=audience_list,
        cyberessentials_requirement=None,  # Not mapped in current DB schema
        group_tag=None,  # Not mapped in current DB schema
        provisions=provision_ids  # type: ignore
    )


def db_questions_to_api(db_questions: List[DBQuestion]) -> List[QuestionResponse]:
    """Convert list of database Question models to API QuestionResponse models"""
    return [db_question_to_api(q) for q in db_questions]


def db_clause_to_api(db_clause: DBClause) -> ProvisionResponse:
    """Convert database Clause model to API ProvisionResponse model"""
    
    # Get question IDs
    question_ids = [str(question.id) for question in db_clause.questions] if hasattr(db_clause, 'questions') and db_clause.questions is not None else []
    
    return ProvisionResponse(
        id=str(db_clause.id),
        section=str(db_clause.category_id),  # Map category_id to section
        subsection=str(db_clause.category_id),  # Use same for subsection
        clause=str(db_clause.clause_identifier),
        subclause=str(db_clause.clause_identifier),  # Use same for subclause
        provision=str(db_clause.name),  # Map 'name' to 'provision'
        questions=question_ids,
        keywords=None  # Not mapped in current DB schema
    )


def db_clauses_to_api(db_clauses: List[DBClause]) -> List[ProvisionResponse]:
    """Convert list of database Clause models to API ProvisionResponse models"""
    return [db_clause_to_api(c) for c in db_clauses]


def api_audience_to_db(audience_list: Optional[List[str]]) -> AudienceType:
    """Convert API audience list to database AudienceType enum"""
    if not audience_list:
        return AudienceType.IT  # Default
    
    # Take the first audience from the list
    audience_str = audience_list[0]
    
    # Map audience strings to enum values
    audience_mapping = {
        "HR": AudienceType.HR,
        "IT": AudienceType.IT,
        "Owner": AudienceType.OWNER,
        "OWNER": AudienceType.OWNER,
    }
    
    return audience_mapping.get(audience_str, AudienceType.IT)


def db_audience_to_api(audience: AudienceType) -> List[str]:
    """Convert database AudienceType enum to API audience list"""
    return [audience.value] if audience else ["IT"]


# Validation helpers
def validate_question_id(question_id: str) -> Optional[int]:
    """Validate and convert question ID string to integer"""
    try:
        return int(question_id)
    except (ValueError, TypeError):
        return None


def validate_provision_id(provision_id: str) -> Optional[int]:
    """Validate and convert provision ID string to integer"""
    try:
        return int(provision_id)
    except (ValueError, TypeError):
        return None


def db_organization_to_api(db_organization: DBOrganization) -> OrganizationResponse:
    """Convert database Organization model to API OrganizationResponse model"""
    
    # Safely extract values from SQLAlchemy model
    try:
        annual_turnover_val = db_organization.annual_turnover
    except Exception:
        annual_turnover_val = None
        
    try:
        num_employees_val = db_organization.number_of_employees  
    except Exception:
        num_employees_val = None
        
    try:
        assessment_date_val = db_organization.date_of_self_assessment
    except Exception:
        assessment_date_val = None
    
    return OrganizationResponse(
        id=str(db_organization.id),
        organisation_name=str(db_organization.organisation_name),
        acra_number_uen=str(db_organization.acra_number_uen) if db_organization.acra_number_uen is not None else None,
        annual_turnover=annual_turnover_val,  # type: ignore
        number_of_employees=num_employees_val,  # type: ignore
        date_of_self_assessment=assessment_date_val,  # type: ignore
        scope_of_certification=str(db_organization.scope_of_certification) if db_organization.scope_of_certification is not None else None,
        created_at=db_organization.created_at.isoformat() if db_organization.created_at is not None else "",
        updated_at=db_organization.updated_at.isoformat() if db_organization.updated_at is not None else ""
    )


def db_organizations_to_api(db_organizations: List[DBOrganization]) -> List[OrganizationResponse]:
    """Convert list of database Organization models to API OrganizationResponse models"""
    return [db_organization_to_api(org) for org in db_organizations]


# Validation helpers for organizations
def validate_organization_id(organization_id: str) -> Optional[int]:
    """Validate and convert organization ID string to integer"""
    try:
        return int(organization_id)
    except (ValueError, TypeError):
        return None


def db_self_assessment_answer_to_api(db_answer: DBSelfAssessmentAnswer) -> SelfAssessmentAnswerResponse:
    """Convert database SelfAssessmentAnswer model to API SelfAssessmentAnswerResponse model"""
    
    # Safely extract clause IDs
    clause_ids = []
    try:
        if hasattr(db_answer, 'clauses') and db_answer.clauses is not None:
            clause_ids = [str(clause.id) for clause in db_answer.clauses]
    except Exception:
        clause_ids = []
    
    # Safely extract organization name
    organization_name = None
    try:
        if hasattr(db_answer, 'organization') and db_answer.organization is not None:
            organization_name = str(db_answer.organization.organisation_name)
    except Exception:
        organization_name = None
    
    # Safely extract question text
    question_text = None
    try:
        if hasattr(db_answer, 'question') and db_answer.question is not None:
            question_text = str(db_answer.question.name)
    except Exception:
        question_text = None
    
    return SelfAssessmentAnswerResponse(
        id=str(db_answer.id),
        organization_id=int(db_answer.organization_id),  # type: ignore
        question_id=int(db_answer.question_id),  # type: ignore
        answer=str(db_answer.answer),
        created_at=db_answer.created_at.isoformat() if db_answer.created_at is not None else "",
        updated_at=db_answer.updated_at.isoformat() if db_answer.updated_at is not None else "",
        clause_ids=clause_ids,
        organization_name=organization_name,
        question_text=question_text
    )


def db_self_assessment_answers_to_api(db_answers: List[DBSelfAssessmentAnswer]) -> List[SelfAssessmentAnswerResponse]:
    """Convert list of database SelfAssessmentAnswer models to API SelfAssessmentAnswerResponse models"""
    return [db_self_assessment_answer_to_api(answer) for answer in db_answers]


# Validation helpers for self-assessment answers
def validate_self_assessment_answer_id(answer_id: str) -> Optional[int]:
    """Validate and convert self-assessment answer ID string to integer"""
    try:
        return int(answer_id)
    except (ValueError, TypeError):
        return None 