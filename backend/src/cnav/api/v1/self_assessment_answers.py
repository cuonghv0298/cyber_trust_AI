from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional

from ..models import (
    SelfAssessmentAnswerResponse, 
    SelfAssessmentAnswerCreate, 
    SelfAssessmentAnswerUpdate, 
    SelfAssessmentAnswerList
)
from ..dependencies import SelfAssessmentAnswerServiceDep
from ..adapters import db_self_assessment_answers_to_api, db_self_assessment_answer_to_api

router = APIRouter()

@router.get("/", response_model=List[SelfAssessmentAnswerResponse])
async def get_self_assessment_answers(
    answer_service: SelfAssessmentAnswerServiceDep,
    limit: Optional[int] = None, 
    offset: Optional[int] = None
):
    """Get all self-assessment answers"""
    db_answers = answer_service.get_all_answers()
    answers = db_self_assessment_answers_to_api(db_answers)
    
    if limit and offset and offset >= len(answers):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Offset is greater than the number of answers"
        )
    if limit:
        answers = answers[:limit]
    if offset:
        if offset >= len(answers):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Offset is greater than the number of answers"
            )
        answers = answers[offset:]
    return answers

@router.get("/{answer_id}", response_model=SelfAssessmentAnswerResponse)
async def get_self_assessment_answer(
    answer_id: str,
    answer_service: SelfAssessmentAnswerServiceDep
):
    """Get a specific self-assessment answer by ID"""
    db_answer = answer_service.get_answer_by_id(answer_id)
    if db_answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Self-assessment answer with ID {answer_id} not found"
        )
    return db_self_assessment_answer_to_api(db_answer)

@router.post("/", response_model=SelfAssessmentAnswerResponse, status_code=status.HTTP_201_CREATED)
async def create_self_assessment_answer(
    answer: SelfAssessmentAnswerCreate,
    answer_service: SelfAssessmentAnswerServiceDep
):
    """Create a new self-assessment answer"""
    try:
        db_answer = answer_service.create_answer(answer)
        return db_self_assessment_answer_to_api(db_answer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create self-assessment answer: {str(e)}"
        )

@router.put("/{answer_id}", response_model=SelfAssessmentAnswerResponse)
async def update_self_assessment_answer(
    answer_id: str, 
    answer: SelfAssessmentAnswerUpdate,
    answer_service: SelfAssessmentAnswerServiceDep
):
    """Update an existing self-assessment answer"""
    try:
        db_answer = answer_service.update_answer(answer_id, answer)
        if db_answer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Self-assessment answer with ID {answer_id} not found"
            )
        return db_self_assessment_answer_to_api(db_answer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update self-assessment answer: {str(e)}"
        )

@router.delete("/{answer_id}")
async def delete_self_assessment_answer(
    answer_id: str,
    answer_service: SelfAssessmentAnswerServiceDep
):
    """Delete a self-assessment answer"""
    try:
        success = answer_service.delete_answer(answer_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Self-assessment answer with ID {answer_id} not found"
            )
        return {"message": f"Self-assessment answer with ID {answer_id} has been deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete self-assessment answer: {str(e)}"
        )

# Filter and search endpoints
@router.get("/by-organization/{organization_id}", response_model=List[SelfAssessmentAnswerResponse])
async def get_answers_by_organization(
    organization_id: str,
    answer_service: SelfAssessmentAnswerServiceDep
):
    """Get all self-assessment answers for a specific organization"""
    try:
        db_answers = answer_service.get_answers_by_organization(organization_id)
        return db_self_assessment_answers_to_api(db_answers)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get answers by organization: {str(e)}"
        )

@router.get("/by-question/{question_id}", response_model=List[SelfAssessmentAnswerResponse])
async def get_answers_by_question(
    question_id: str,
    answer_service: SelfAssessmentAnswerServiceDep
):
    """Get all self-assessment answers for a specific question"""
    try:
        db_answers = answer_service.get_answers_by_question(question_id)
        return db_self_assessment_answers_to_api(db_answers)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get answers by question: {str(e)}"
        )

@router.get("/by-clause/{clause_id}", response_model=List[SelfAssessmentAnswerResponse])
async def get_answers_by_clause(
    clause_id: str,
    answer_service: SelfAssessmentAnswerServiceDep
):
    """Get all self-assessment answers associated with a specific clause"""
    try:
        db_answers = answer_service.get_answers_by_clause(clause_id)
        return db_self_assessment_answers_to_api(db_answers)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get answers by clause: {str(e)}"
        )

@router.get("/search/text", response_model=List[SelfAssessmentAnswerResponse])
async def search_answers_by_text(
    answer_service: SelfAssessmentAnswerServiceDep,
    search_text: str = Query(..., description="Text to search for in answers")
):
    """Search self-assessment answers by text content"""
    try:
        db_answers = answer_service.search_answers_by_text(search_text)
        return db_self_assessment_answers_to_api(db_answers)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search answers: {str(e)}"
        )

@router.get("/filter", response_model=List[SelfAssessmentAnswerResponse])
async def filter_answers(
    answer_service: SelfAssessmentAnswerServiceDep,
    organization_id: Optional[int] = Query(None, description="Filter by organization ID"),
    question_id: Optional[int] = Query(None, description="Filter by question ID"),
    clause_id: Optional[int] = Query(None, description="Filter by clause ID"),
    answer_contains: Optional[str] = Query(None, description="Filter by text contained in answer")
):
    """Get self-assessment answers with multiple filters"""
    try:
        db_answers = answer_service.get_answers_with_filters(
            organization_id=organization_id,
            question_id=question_id,
            clause_id=clause_id,
            answer_contains=answer_contains
        )
        return db_self_assessment_answers_to_api(db_answers)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to filter answers: {str(e)}"
        )