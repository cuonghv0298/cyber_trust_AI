from fastapi import APIRouter, HTTPException, status
from typing import List, Optional

from ..models import ProvisionResponse, ProvisionCreate, ProvisionUpdate, ProvisionList
from ..dependencies import ProvisionServiceDep
from ..adapters import db_clauses_to_api, db_clause_to_api

router = APIRouter()

@router.get("/", response_model=List[ProvisionResponse])
async def get_provisions(
    provision_service: ProvisionServiceDep
):
    """Get all provisions"""
    db_clauses = provision_service.get_all_provisions()
    return db_clauses_to_api(db_clauses)

@router.get("/provisions/{provision_id}", response_model=ProvisionResponse)
async def get_provision(
    provision_id: str,
    provision_service: ProvisionServiceDep
):
    """Get a specific provision by ID"""
    provision = provision_service.get_provision_by_id(provision_id)
    if provision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Provision with ID {provision_id} not found"
        )
    return provision

@router.post("/provisions", response_model=ProvisionResponse, status_code=status.HTTP_201_CREATED)
async def create_provision(
    provision: ProvisionCreate,
    provision_service: ProvisionServiceDep
):
    """Create a new provision"""
    try:
        return provision_service.create_provision(provision)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create provision: {str(e)}"
        )

@router.put("/provisions/{provision_id}", response_model=ProvisionResponse)
async def update_provision(
    provision_id: str, 
    provision: ProvisionUpdate,
    provision_service: ProvisionServiceDep
):
    """Update an existing provision"""
    try:
        updated_provision = provision_service.update_provision(provision_id, provision)
        if updated_provision is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provision with ID {provision_id} not found"
            )
        return updated_provision
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update provision: {str(e)}"
        )

@router.delete("/provisions/{provision_id}")
async def delete_provision(
    provision_id: str,
    provision_service: ProvisionServiceDep
):
    """Delete a provision"""
    try:
        success = provision_service.delete_provision(provision_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provision with ID {provision_id} not found"
            )
        return {"message": f"Provision with ID {provision_id} has been deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete provision: {str(e)}"
        ) 