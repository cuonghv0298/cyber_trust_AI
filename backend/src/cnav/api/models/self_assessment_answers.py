"""
Self-Assessment Answer API response models
"""

from typing import Optional, List
from pydantic import BaseModel, Field

class SelfAssessmentAnswerBase(BaseModel):
    """Base model for self-assessment answer data"""
    organization_id: int = Field(..., description="ID of the organization")
    question_id: int = Field(..., description="ID of the question being answered")
    answer: str = Field(..., description="The answer text")

class SelfAssessmentAnswerCreate(SelfAssessmentAnswerBase):
    """Model for creating a new self-assessment answer"""
    clause_ids: Optional[List[int]] = Field(None, description="List of clause IDs to associate with this answer")

class SelfAssessmentAnswerUpdate(BaseModel):
    """Model for updating an existing self-assessment answer"""
    organization_id: Optional[int] = Field(None, description="ID of the organization")
    question_id: Optional[int] = Field(None, description="ID of the question being answered")
    answer: Optional[str] = Field(None, description="The answer text")
    clause_ids: Optional[List[int]] = Field(None, description="List of clause IDs to associate with this answer")

class SelfAssessmentAnswerResponse(SelfAssessmentAnswerBase):
    """Model for self-assessment answer response data"""
    id: str = Field(..., description="Unique identifier for the self-assessment answer")
    created_at: str = Field(..., description="Answer creation timestamp")
    updated_at: str = Field(..., description="Answer last update timestamp")
    clause_ids: Optional[List[str]] = Field(None, description="List of associated clause IDs")
    organization_name: Optional[str] = Field(None, description="Name of the organization")
    question_text: Optional[str] = Field(None, description="Text of the question")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "organization_id": 1,
                "question_id": 1,
                "answer": "Yes, we have implemented a comprehensive information security policy that covers all aspects of data protection and is reviewed annually by senior management.",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "clause_ids": ["1", "2", "3"],
                "organization_name": "Tech Solutions Pte Ltd",
                "question_text": "Does your organization have a documented information security policy?"
            }
        }

class SelfAssessmentAnswerList(BaseModel):
    """Model for paginated self-assessment answer list responses"""
    answers: List[SelfAssessmentAnswerResponse] = Field(..., description="List of self-assessment answers")
    total: int = Field(..., description="Total number of self-assessment answers")
    offset: int = Field(0, description="Offset used for pagination")
    limit: Optional[int] = Field(None, description="Limit used for pagination")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answers": [
                    {
                        "id": "1",
                        "organization_id": 1,
                        "question_id": 1,
                        "answer": "Yes, we have implemented a comprehensive information security policy.",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z",
                        "clause_ids": ["1", "2"],
                        "organization_name": "Tech Solutions Pte Ltd",
                        "question_text": "Does your organization have a documented information security policy?"
                    }
                ],
                "total": 25,
                "offset": 0,
                "limit": 10
            }
        }

# Additional filter models
class SelfAssessmentAnswersByOrganization(BaseModel):
    """Model for filtering answers by organization"""
    organization_id: int = Field(..., description="Organization ID to filter by")

class SelfAssessmentAnswersByQuestion(BaseModel):
    """Model for filtering answers by question"""  
    question_id: int = Field(..., description="Question ID to filter by")

class SelfAssessmentAnswersFilter(BaseModel):
    """Model for complex filtering of self-assessment answers"""
    organization_id: Optional[int] = Field(None, description="Filter by organization ID")
    question_id: Optional[int] = Field(None, description="Filter by question ID")
    answer_contains: Optional[str] = Field(None, description="Filter by text contained in answer")
    clause_id: Optional[int] = Field(None, description="Filter by associated clause ID")