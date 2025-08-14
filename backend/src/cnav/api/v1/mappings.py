from fastapi import APIRouter, HTTPException, status
from typing import List

from ..models import (
    QuestionResponse, ProvisionResponse, MappingResponse, MappingCreate, 
    MappingStatsResponse, QuestionProvisionMappingResponse, ProvisionQuestionMappingResponse
)
from ..dependencies import MappingServiceDep, QuestionServiceDep, ProvisionServiceDep
from ..adapters import db_questions_to_api, db_clauses_to_api

router = APIRouter()

@router.post("/mappings", response_model=MappingResponse)
async def create_mapping(
    mapping_data: MappingCreate,
    mapping_service: MappingServiceDep
):
    """Create a bidirectional mapping between question and provision"""
    try:
        success = mapping_service.create_mapping(mapping_data.question_id, mapping_data.provision_id)
        if success:
            return MappingResponse(
                question_id=mapping_data.question_id,
                provision_id=mapping_data.provision_id,
                created_at=None  # You can add timestamp logic here if needed
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create mapping"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create mapping: {str(e)}"
        )

@router.delete("/mappings")
async def delete_mapping(question_id: str, provision_id: str):
    """Delete a bidirectional mapping between question and provision"""
    try:
        success = mapping_service.delete_mapping(question_id, provision_id)
        if success:
            return {"message": f"Successfully removed mapping between question {question_id} and provision {provision_id}"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete mapping"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete mapping: {str(e)}"
        )

@router.get("/questions/{question_id}/provisions", response_model=List[ProvisionResponse])
async def get_provisions_for_question(
    question_id: str,
    mapping_service: MappingServiceDep
):
    """Get all provisions mapped to a question"""
    try:
        db_clauses = mapping_service.get_provisions_for_question(question_id)
        return db_clauses_to_api(db_clauses)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get provisions for question: {str(e)}"
        )

@router.get("/provisions/{provision_id}/questions", response_model=List[QuestionResponse])
async def get_questions_for_provision(
    provision_id: str,
    mapping_service: MappingServiceDep
):
    """Get all questions mapped to a provision"""
    try:
        db_questions = mapping_service.get_questions_for_provision(provision_id)
        return db_questions_to_api(db_questions)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get questions for provision: {str(e)}"
        )

@router.get("/analytics/mapping-stats", response_model=MappingStatsResponse)
async def get_mapping_statistics(
    question_service: QuestionServiceDep,
    provision_service: ProvisionServiceDep
):
    """Get statistics about question-provision mappings"""
    try:
        all_db_questions = question_service.get_all_questions()
        all_db_provisions = provision_service.get_all_provisions()
        
        # Count questions with mappings
        questions_with_provisions = sum(1 for q in all_db_questions if hasattr(q, 'clauses') and q.clauses and len(q.clauses) > 0)
        
        # Count provisions with mappings
        provisions_with_questions = sum(1 for p in all_db_provisions if hasattr(p, 'questions') and p.questions and len(p.questions) > 0)
        
        # Count total mappings
        total_mappings = sum(len(q.clauses) for q in all_db_questions if hasattr(q, 'clauses') and q.clauses)
        
        return MappingStatsResponse(
            total_mappings=total_mappings,
            questions={
                "total": len(all_db_questions),
                "mapped": questions_with_provisions,
                "unmapped": len(all_db_questions) - questions_with_provisions
            },
            provisions={
                "total": len(all_db_provisions),
                "mapped": provisions_with_questions,
                "unmapped": len(all_db_provisions) - provisions_with_questions
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get mapping statistics: {str(e)}"
        ) 