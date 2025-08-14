"""
Answer API response models
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from .common import AnswerStatusOptions, ConfidenceLevelOptions, RiskLevelOptions

class EvidenceFileResponse(BaseModel):
    """Model for evidence file data"""
    filename: str = Field(..., description="Name of the evidence file")
    file_type: str = Field(..., description="File type extension (pdf, docx, xlsx, png, etc.)")
    description: str = Field(..., description="Description of the evidence file")
    file_path: Optional[str] = Field(None, description="Path to the stored file")
    uploaded_at: Optional[str] = Field(None, description="ISO timestamp when file was uploaded")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "filename": "security_policy_v2.pdf",
                "file_type": "pdf",
                "description": "Current information security policy document",
                "file_path": "/uploads/evidence/security_policy_v2.pdf",
                "uploaded_at": "2024-01-15T10:30:00Z"
            }
        }

class AnswerBase(BaseModel):
    """Base model for answer data"""
    question_id: str = Field(..., description="ID of the question being answered")
    company_id: str = Field(..., description="ID of the company providing the answer")
    answer: str = Field(..., description="The answer text")
    answered_by: str = Field(..., description="Name or role of person who answered")
    answered_at: str = Field(..., description="ISO timestamp when answer was provided")
    status: AnswerStatusOptions = Field("draft", description="Current status of the answer")
    confidence_level: Optional[ConfidenceLevelOptions] = Field(None, description="Confidence level in the answer")
    evidence_description: Optional[str] = Field(None, description="Description of supporting evidence")
    compliance_notes: Optional[str] = Field(None, description="Notes about compliance aspects")
    extracted_keywords: Optional[List[str]] = Field(None, description="Keywords extracted from the answer")
    risk_level: Optional[RiskLevelOptions] = Field(None, description="Assessed risk level")
    reviewer_notes: Optional[str] = Field(None, description="Notes from the reviewer")

class AnswerCreate(AnswerBase):
    """Model for creating a new answer"""
    id: str = Field(..., description="Unique identifier for the answer")
    evidence_files: Optional[List[EvidenceFileResponse]] = Field(None, description="List of evidence files")

class AnswerUpdate(BaseModel):
    """Model for updating an existing answer"""
    answer: Optional[str] = Field(None, description="The answer text")
    answered_by: Optional[str] = Field(None, description="Name or role of person who answered")
    status: Optional[AnswerStatusOptions] = Field(None, description="Current status of the answer")
    confidence_level: Optional[ConfidenceLevelOptions] = Field(None, description="Confidence level in the answer")
    evidence_files: Optional[List[EvidenceFileResponse]] = Field(None, description="List of evidence files")
    evidence_description: Optional[str] = Field(None, description="Description of supporting evidence")
    compliance_notes: Optional[str] = Field(None, description="Notes about compliance aspects")
    extracted_keywords: Optional[List[str]] = Field(None, description="Keywords extracted from the answer")
    risk_level: Optional[RiskLevelOptions] = Field(None, description="Assessed risk level")
    reviewer_notes: Optional[str] = Field(None, description="Notes from the reviewer")
    last_updated_at: Optional[str] = Field(None, description="ISO timestamp of last update")

class AnswerResponse(AnswerBase):
    """Model for answer response data"""
    id: str = Field(..., description="Unique identifier for the answer")
    evidence_files: Optional[List[EvidenceFileResponse]] = Field(None, description="List of evidence files")
    last_updated_at: Optional[str] = Field(None, description="ISO timestamp of last update")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "question_id": "1", 
                "company_id": "1",
                "answer": "Yes, we have a comprehensive information security policy that is reviewed annually by management.",
                "answered_by": "IT Manager",
                "answered_at": "2024-01-15T14:30:00Z",
                "status": "submitted",
                "confidence_level": "high",
                "evidence_files": [
                    {
                        "filename": "security_policy_v2.pdf",
                        "file_type": "pdf",
                        "description": "Current information security policy document",
                        "file_path": "/uploads/evidence/security_policy_v2.pdf",
                        "uploaded_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "evidence_description": "Latest version of our information security policy document",
                "compliance_notes": "Policy meets all required standards",
                "extracted_keywords": ["policy", "security", "management", "annual"],
                "risk_level": "low",
                "last_updated_at": "2024-01-15T14:30:00Z",
                "reviewer_notes": None
            }
        } 