from fastapi import APIRouter, HTTPException, status
from typing import List, Optional

from ..models import OrganizationResponse, OrganizationCreate, OrganizationUpdate, OrganizationList
from ..dependencies import OrganizationServiceDep
from ..adapters import db_organizations_to_api, db_organization_to_api

router = APIRouter()

@router.get("/", response_model=List[OrganizationResponse])
async def get_organizations(
    organization_service: OrganizationServiceDep,
    limit: Optional[int] = None, 
    offset: Optional[int] = None
):
    """Get all organizations"""
    db_organizations = organization_service.get_all_organizations()
    organizations = db_organizations_to_api(db_organizations)
    
    if limit and offset and offset >= len(organizations):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Offset is greater than the number of organizations"
        )
    if limit:
        organizations = organizations[:limit]
    if offset:
        if offset >= len(organizations):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Offset is greater than the number of organizations"
            )
        organizations = organizations[offset:]
    return organizations

@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: str,
    organization_service: OrganizationServiceDep
):
    """Get a specific organization by ID"""
    db_organization = organization_service.get_organization_by_id(organization_id)
    if db_organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Organization with ID {organization_id} not found"
        )
    return db_organization_to_api(db_organization)

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    organization: OrganizationCreate,
    organization_service: OrganizationServiceDep
):
    """Create a new organization"""
    try:
        db_organization = organization_service.create_organization(organization)
        return db_organization_to_api(db_organization)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create organization: {str(e)}"
        )

@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: str, 
    organization: OrganizationUpdate,
    organization_service: OrganizationServiceDep
):
    """Update an existing organization"""
    try:
        db_organization = organization_service.update_organization(organization_id, organization)
        if db_organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization with ID {organization_id} not found"
            )
        return db_organization_to_api(db_organization)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update organization: {str(e)}"
        )

@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: str,
    organization_service: OrganizationServiceDep
):
    """Delete an organization"""
    try:
        success = organization_service.delete_organization(organization_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization with ID {organization_id} not found"
            )
        return {"message": f"Organization with ID {organization_id} has been deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete organization: {str(e)}"
        )

# Additional endpoints for specific searches
@router.get("/search/by-name/{name_pattern}", response_model=List[OrganizationResponse])
async def search_organizations_by_name(
    name_pattern: str,
    organization_service: OrganizationServiceDep
):
    """Search organizations by name pattern"""
    try:
        db_organizations = organization_service.get_organizations_by_name(name_pattern)
        return db_organizations_to_api(db_organizations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search organizations: {str(e)}"
        )

@router.get("/search/by-employee-count/{min_employees}/{max_employees}", response_model=List[OrganizationResponse])
async def search_organizations_by_employee_count(
    min_employees: int,
    max_employees: int,
    organization_service: OrganizationServiceDep
):
    """Search organizations by employee count range"""
    try:
        if min_employees > max_employees:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum employees cannot be greater than maximum employees"
            )
        
        db_organizations = organization_service.get_organizations_by_employee_count_range(
            min_employees, max_employees
        )
        return db_organizations_to_api(db_organizations)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search organizations: {str(e)}"
        )
