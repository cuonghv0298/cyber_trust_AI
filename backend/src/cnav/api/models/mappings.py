"""
Mapping API response models for question-provision relationships
"""

from typing import Optional, List
from pydantic import BaseModel, Field

class MappingCreate(BaseModel):
    """Model for creating a mapping between question and provision"""
    question_id: str = Field(..., description="ID of the question to map")
    provision_id: str = Field(..., description="ID of the provision to map")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "1",
                "provision_id": "1"
            }
        }

class MappingResponse(BaseModel):
    """Model for mapping response data"""
    question_id: str = Field(..., description="ID of the mapped question")
    provision_id: str = Field(..., description="ID of the mapped provision")
    created_at: Optional[str] = Field(None, description="ISO timestamp when mapping was created")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "question_id": "1",
                "provision_id": "1",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }

class MappingStatsResponse(BaseModel):
    """Model for mapping statistics"""
    total_mappings: int = Field(..., description="Total number of mappings")
    questions: dict = Field(..., description="Question mapping statistics")
    provisions: dict = Field(..., description="Provision mapping statistics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_mappings": 150,
                "questions": {
                    "total": 75,
                    "mapped": 60,
                    "unmapped": 15
                },
                "provisions": {
                    "total": 50,
                    "mapped": 45,
                    "unmapped": 5
                }
            }
        }

class QuestionProvisionMappingResponse(BaseModel):
    """Model for question with its mapped provisions"""
    question_id: str = Field(..., description="ID of the question")
    question_text: Optional[str] = Field(None, description="Text of the question")
    provision_ids: List[str] = Field(..., description="List of mapped provision IDs")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "question_id": "1",
                "question_text": "Does your organization have a documented information security policy?",
                "provision_ids": ["1", "2", "3"]
            }
        }

class ProvisionQuestionMappingResponse(BaseModel):
    """Model for provision with its mapped questions"""
    provision_id: str = Field(..., description="ID of the provision")
    provision_text: Optional[str] = Field(None, description="Text of the provision")
    question_ids: List[str] = Field(..., description="List of mapped question IDs")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "provision_id": "1",
                "provision_text": "Information security policy document shall be defined and approved by management.",
                "question_ids": ["1", "2", "5"]
            }
        } 