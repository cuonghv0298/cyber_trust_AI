"""
Provision API response models
"""

from typing import Optional, List
from pydantic import BaseModel, Field

class ProvisionBase(BaseModel):
    """Base model for provision data"""
    section: str = Field(..., description="Main section identifier")
    subsection: str = Field(..., description="Subsection identifier")
    clause: str = Field(..., description="Clause identifier")
    subclause: str = Field(..., description="Subclause identifier")
    provision: str = Field(..., description="The provision text/content")
    keywords: Optional[List[str]] = Field(None, description="Keywords associated with this provision")

class ProvisionCreate(ProvisionBase):
    """Model for creating a new provision"""
    id: str = Field(..., description="Unique identifier for the provision")

class ProvisionUpdate(BaseModel):
    """Model for updating an existing provision"""
    section: Optional[str] = Field(None, description="Main section identifier")
    subsection: Optional[str] = Field(None, description="Subsection identifier")
    clause: Optional[str] = Field(None, description="Clause identifier")
    subclause: Optional[str] = Field(None, description="Subclause identifier")
    provision: Optional[str] = Field(None, description="The provision text/content")
    keywords: Optional[List[str]] = Field(None, description="Keywords associated with this provision")
    questions: Optional[List[str]] = Field(None, description="List of question IDs")

class ProvisionResponse(ProvisionBase):
    """Model for provision response data"""
    id: str = Field(..., description="Unique identifier for the provision")
    questions: Optional[List[str]] = Field(None, description="List of question IDs")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "section": "A",
                "subsection": "A.5",
                "clause": "A.5.1",
                "subclause": "A.5.1.1",
                "provision": "Information security policy document shall be defined and approved by management.",
                "keywords": ["policy", "management", "approval", "documentation"],
                "questions": ["1", "2"]
            }
        }

class ProvisionList(BaseModel):
    """Model for paginated provision list responses"""
    provisions: List[ProvisionResponse] = Field(..., description="List of provisions")
    total: int = Field(..., description="Total number of provisions")
    offset: int = Field(0, description="Offset used for pagination")
    limit: Optional[int] = Field(None, description="Limit used for pagination")
    
    class Config:
        json_schema_extra = {
            "example": {
                "provisions": [
                    {
                        "id": "1",
                        "section": "A",
                        "subsection": "A.5",
                        "clause": "A.5.1",
                        "subclause": "A.5.1.1",
                        "provision": "Information security policy document shall be defined and approved by management.",
                        "keywords": ["policy", "management", "approval", "documentation"],
                        "questions": ["1", "2"]
                    }
                ],
                "total": 25,
                "offset": 0,
                "limit": 10
            }
        } 