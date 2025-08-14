from typing import List, Optional, Union

from sqlalchemy.exc import IntegrityError

from cnav.database.models.organization import Organization
from cnav.api.services import DatabaseService


class OrganizationService(DatabaseService):
    """Service for managing organizations using database backend"""
    
    def get_all_organizations(self) -> List[Organization]:
        """Get all organizations from database"""
        with self.get_db_session() as session:
            return session.query(Organization).all()
    
    def get_organization_by_id(self, organization_id: Union[int, str]) -> Optional[Organization]:
        """Get a specific organization by ID"""
        with self.get_db_session() as session:
            if isinstance(organization_id, str):
                try:
                    organization_id = int(organization_id)
                except ValueError:
                    return None
            return session.query(Organization).filter(Organization.id == organization_id).first()
    
    def create_organization(self, organization_data) -> Organization:
        """Create a new organization"""
        with self.get_db_session() as session:
            try:
                # Convert Pydantic model to dict if needed
                if hasattr(organization_data, 'model_dump'):
                    data = organization_data.model_dump()
                else:
                    data = organization_data if isinstance(organization_data, dict) else organization_data.__dict__
                
                # Create organization from the data
                db_organization = Organization(
                    organisation_name=data.get('organisation_name', ''),
                    acra_number_uen=data.get('acra_number_uen'),
                    annual_turnover=data.get('annual_turnover'),
                    number_of_employees=data.get('number_of_employees'),
                    date_of_self_assessment=data.get('date_of_self_assessment'),
                    scope_of_certification=data.get('scope_of_certification')
                )
                
                session.add(db_organization)
                session.commit()
                session.refresh(db_organization)
                return db_organization
                
            except IntegrityError as e:
                session.rollback()
                raise ValueError(f"Organization creation failed: {str(e)}")
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to create organization: {str(e)}")

    def update_organization(self, organization_id: Union[int, str], organization_data) -> Optional[Organization]:
        """Update an existing organization"""
        with self.get_db_session() as session:
            try:
                if isinstance(organization_id, str):
                    try:
                        organization_id = int(organization_id)
                    except ValueError:
                        return None
                
                organization = session.query(Organization).filter(Organization.id == organization_id).first()
                if not organization:
                    return None
                
                # Convert Pydantic model to dict if needed
                if hasattr(organization_data, 'model_dump'):
                    data = organization_data.model_dump(exclude_unset=True)
                else:
                    data = organization_data if isinstance(organization_data, dict) else organization_data.__dict__
                
                # Update organization fields
                for field, value in data.items():
                    if hasattr(organization, field) and value is not None:
                        setattr(organization, field, value)
                
                session.commit()
                session.refresh(organization)
                return organization
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to update organization: {str(e)}")
    
    def delete_organization(self, organization_id: Union[int, str]) -> bool:
        """Delete an organization"""
        with self.get_db_session() as session:
            try:
                if isinstance(organization_id, str):
                    try:
                        organization_id = int(organization_id)
                    except ValueError:
                        return False
                
                organization = session.query(Organization).filter(Organization.id == organization_id).first()
                if not organization:
                    return False
                
                session.delete(organization)
                session.commit()
                return True
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Failed to delete organization: {str(e)}")
    
    def get_organizations_by_name(self, name_pattern: str) -> List[Organization]:
        """Get organizations filtered by name pattern"""
        with self.get_db_session() as session:
            return session.query(Organization).filter(
                Organization.organisation_name.ilike(f"%{name_pattern}%")
            ).all()
    
    def get_organizations_by_employee_count_range(self, min_employees: int, max_employees: int) -> List[Organization]:
        """Get organizations filtered by employee count range"""
        with self.get_db_session() as session:
            query = session.query(Organization)
            
            if min_employees is not None:
                query = query.filter(Organization.number_of_employees >= min_employees)
            if max_employees is not None:
                query = query.filter(Organization.number_of_employees <= max_employees)
                
            return query.all()