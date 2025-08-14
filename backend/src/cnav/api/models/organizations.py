"""
Organization API response models
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal

class OrganizationBase(BaseModel):
    """Base model for organization data"""
    organisation_name: str = Field(..., description="Organization name")
    acra_number_uen: Optional[str] = Field(None, description="ACRA Number/Unique Entity Number (UEN)")
    annual_turnover: Optional[Decimal] = Field(None, description="Annual turnover amount")
    number_of_employees: Optional[int] = Field(None, description="Number of employees")
    date_of_self_assessment: Optional[date] = Field(None, description="Date of self-assessment")
    scope_of_certification: Optional[str] = Field(None, description="Scope of certification for Cyber Essentials mark")

class OrganizationCreate(OrganizationBase):
    """Model for creating a new organization"""
    pass

class OrganizationUpdate(BaseModel):
    """Model for updating an existing organization"""
    organisation_name: Optional[str] = Field(None, description="Organization name")
    acra_number_uen: Optional[str] = Field(None, description="ACRA Number/Unique Entity Number (UEN)")
    annual_turnover: Optional[Decimal] = Field(None, description="Annual turnover amount")
    number_of_employees: Optional[int] = Field(None, description="Number of employees")
    date_of_self_assessment: Optional[date] = Field(None, description="Date of self-assessment")
    scope_of_certification: Optional[str] = Field(None, description="Scope of certification for Cyber Essentials mark")

class OrganizationResponse(OrganizationBase):
    """Model for organization response data"""
    id: str = Field(..., description="Unique identifier for the organization")
    created_at: str = Field(..., description="Organization creation timestamp")
    updated_at: str = Field(..., description="Organization last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "organisation_name": "Tech Solutions Pte Ltd",
                "acra_number_uen": "201234567H",
                "annual_turnover": "5000000.00",
                "number_of_employees": 150,
                "date_of_self_assessment": "2024-01-15",
                "scope_of_certification": "IT services and software development",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }

class OrganizationList(BaseModel):
    """Model for paginated organization list responses"""
    organizations: List[OrganizationResponse] = Field(..., description="List of organizations")
    total: int = Field(..., description="Total number of organizations")
    offset: int = Field(0, description="Offset used for pagination")
    limit: Optional[int] = Field(None, description="Limit used for pagination")
    
    class Config:
        json_schema_extra = {
            "example": {
                "organizations": [
                    {
                        "id": "1",
                        "organisation_name": "Tech Solutions Pte Ltd",
                        "acra_number_uen": "201234567H",
                        "annual_turnover": "5000000.00",
                        "number_of_employees": 150,
                        "date_of_self_assessment": "2024-01-15",
                        "scope_of_certification": "IT services and software development",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total": 25,
                "offset": 0,
                "limit": 10
            }
        }