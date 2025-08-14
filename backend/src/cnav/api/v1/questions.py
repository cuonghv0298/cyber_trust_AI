from fastapi import APIRouter, HTTPException, status
from typing import List, Optional

from ..models import QuestionResponse, QuestionCreate, QuestionUpdate, QuestionList
from ..dependencies import QuestionServiceDep
from ..adapters import db_questions_to_api, db_question_to_api

router = APIRouter()

@router.get("/", response_model=List[QuestionResponse])
async def get_questions(
    question_service: QuestionServiceDep,
    limit: Optional[int] = None, 
    offset: Optional[int] = None
):
    """Get all questions"""
    db_questions = question_service.get_all_questions()
    questions = db_questions_to_api(db_questions)
    
    if limit and offset and offset >= len(questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Offset is greater than the number of questions"
        )
    if limit:
        questions = questions[:limit]
    if offset:
        if offset >= len(questions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Offset is greater than the number of questions"
            )
        questions = questions[offset:]
    return questions

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    question_service: QuestionServiceDep
):
    """Get a specific question by ID"""
    db_question = question_service.get_question_by_id(question_id)
    if db_question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Question with ID {question_id} not found"
        )
    return db_question_to_api(db_question)

@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question: QuestionCreate,
    question_service: QuestionServiceDep
):
    """Create a new question"""
    try:
        db_question = question_service.create_question(question)
        return db_question_to_api(db_question)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create question: {str(e)}"
        )

@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str, 
    question: QuestionUpdate,
    question_service: QuestionServiceDep
):
    """Update an existing question"""
    try:
        db_question = question_service.update_question(question_id, question)
        if db_question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {question_id} not found"
            )
        return db_question_to_api(db_question)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update question: {str(e)}"
        )

@router.delete("/{question_id}")
async def delete_question(
    question_id: str,
    question_service: QuestionServiceDep
):
    """Delete a question"""
    try:
        success = question_service.delete_question(question_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {question_id} not found"
            )
        return {"message": f"Question with ID {question_id} has been deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete question: {str(e)}"
        ) 