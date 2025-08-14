from fastapi import Depends, HTTPException
from typing import Optional, Annotated
from functools import lru_cache

from .services import QuestionService, OrganizationService, ProvisionService, MappingService, SelfAssessmentAnswerService

# Service Dependencies
@lru_cache()
def get_question_service() -> QuestionService:
    """Get QuestionService instance (cached)"""
    return QuestionService()

@lru_cache()
def get_organization_service() -> OrganizationService:
    """Get OrganizationService instance (cached)"""
    return OrganizationService()

@lru_cache()  
def get_provision_service() -> ProvisionService:
    """Get ProvisionService instance (cached)"""
    return ProvisionService()

@lru_cache()
def get_mapping_service() -> MappingService:
    """Get MappingService instance (cached)"""
    return MappingService()

@lru_cache()
def get_self_assessment_answer_service() -> SelfAssessmentAnswerService:
    """Get SelfAssessmentAnswerService instance (cached)"""
    return SelfAssessmentAnswerService()

# Type aliases for cleaner endpoint signatures
QuestionServiceDep = Annotated[QuestionService, Depends(get_question_service)]
OrganizationServiceDep = Annotated[OrganizationService, Depends(get_organization_service)]
ProvisionServiceDep = Annotated[ProvisionService, Depends(get_provision_service)]
MappingServiceDep = Annotated[MappingService, Depends(get_mapping_service)]
SelfAssessmentAnswerServiceDep = Annotated[SelfAssessmentAnswerService, Depends(get_self_assessment_answer_service)]

# TODO: Add authentication dependencies
async def get_current_user():
    """Get current authenticated user"""
    # TODO: Implement authentication logic
    pass

# TODO: Add database dependencies
async def get_db():
    """Get database session"""
    # TODO: Implement database connection logic
    pass

# TODO: Add pagination dependencies
async def get_pagination_params(skip: int = 0, limit: int = 100):
    """Get pagination parameters"""
    return {"skip": skip, "limit": limit} 