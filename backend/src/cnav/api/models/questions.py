"""
Question API response models
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from .common import GroupTagOptions

class QuestionBase(BaseModel):
    """Base model for question data"""
    question: str = Field(..., description="The question text")
    audience: Optional[List[str]] = Field(None, description="Target audience for this question")
    cyberessentials_requirement: Optional[str] = Field(None, description="Related cyber essentials requirement")
    group_tag: Optional[GroupTagOptions] = Field(None, description="Category/group tag for the question")

class QuestionCreate(QuestionBase):
    """Model for creating a new question"""
    id: str = Field(..., description="Unique identifier for the question")

class QuestionUpdate(BaseModel):
    """Model for updating an existing question"""
    question: Optional[str] = Field(None, description="The question text")
    audience: Optional[List[str]] = Field(None, description="Target audience for this question")
    cyberessentials_requirement: Optional[str] = Field(None, description="Related cyber essentials requirement")
    group_tag: Optional[GroupTagOptions] = Field(None, description="Category/group tag for the question")
    provisions: Optional[List[str]] = Field(None, description="List of provision IDs")

class QuestionResponse(QuestionBase):
    """Model for question response data"""
    id: str = Field(..., description="Unique identifier for the question")
    provisions: Optional[List[str]] = Field(None, description="List of provision IDs")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "question": "Does your organization have a documented information security policy?",
                "audience": ["IT", "Owner"],
                "cyberessentials_requirement": "A.5 Information security policies",
                "group_tag": "POLICY",
                "provisions": ["1", "2"]
            }
        }

class QuestionList(BaseModel):
    """Model for paginated question list responses"""
    questions: List[QuestionResponse] = Field(..., description="List of questions")
    total: int = Field(..., description="Total number of questions")
    offset: int = Field(0, description="Offset used for pagination")
    limit: Optional[int] = Field(None, description="Limit used for pagination")
    
    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    {
                        "id": "1",
                        "question": "Does your organization have a documented information security policy?",
                        "audience": ["IT", "Owner"],
                        "cyberessentials_requirement": "A.5 Information security policies",
                        "group_tag": "POLICY",
                        "provisions": ["1", "2"]
                    }
                ],
                "total": 50,
                "offset": 0,
                "limit": 10
            }
        } 