"""
Sync script to import organization information and their responses from CSV files into the database.
This script processes the CSV files and creates Organization and SelfAssessmentAnswer records.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# Import database models
from cnav.database.models import Base
from cnav.database.models.organization import Organization
from cnav.database.models.self_assessment_answer import SelfAssessmentAnswer
from cnav.database.models.question import Question, AudienceType

# Database configuration
DATABASE_URL = "sqlite:///./cnav.db"  # Adjust as needed


class OrganizationAnswerSyncService:
    """Service to sync organization answers from CSV files to database."""
    
    def __init__(self, database_url: str = DATABASE_URL):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create database tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)
    
    def _extract_organization_name(self, csv_filename: str) -> str:
        """Extract organization name from CSV filename."""
        # Remove .csv extension and replace underscores with spaces
        name = Path(csv_filename).stem
        name = name.replace('_', ' ')
        
        # Capitalize each word
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name
    
    def _parse_audience_text(self, audience_text: str) -> Optional[AudienceType]:
        """Parse audience text to AudienceType enum."""
        audience_mapping = {
            'HR': AudienceType.HR,
            'IT': AudienceType.IT,
            'OWNER': AudienceType.OWNER,
            'Owner': AudienceType.OWNER,
            'owner': AudienceType.OWNER,
        }
        
        return audience_mapping.get(audience_text.strip())
    
    def sync_organization(self, session: Session, organization_name: str) -> Organization:
        """Sync organization to database."""
        # Check if organization already exists
        existing_org = session.query(Organization).filter_by(name=organization_name).first()
        
        if existing_org:
            print(f"Found existing organization: {organization_name}")
            return existing_org
        else:
            # Create new organization
            new_org = Organization(
                name=organization_name,
                description=f"Organization: {organization_name}"
            )
            session.add(new_org)
            session.flush()  # Flush to get the ID
            print(f"Created new organization: {organization_name}")
            return new_org
    
    def sync_responses(self, session: Session, csv_file_path: str, organization: Organization) -> Tuple[int, int]:
        """Sync responses from CSV file to database."""
        responses_created = 0
        responses_updated = 0
        responses_skipped = 0
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, start=2):  # Start from row 2 (after header)
                question_text = row.get('Question', '').strip()
                audience_text = row.get('Audience', '').strip()
                response_text = row.get('Response', '').strip()
                
                # Skip empty rows or rows without required data
                if not question_text or not audience_text or not response_text:
                    continue
                
                # Parse audience
                audience_enum = self._parse_audience_text(audience_text)
                if not audience_enum:
                    print(f"Row {row_num}: Warning - Unknown audience type '{audience_text}', skipping")
                    responses_skipped += 1
                    continue
                
                # Find the question in the database
                question = session.query(Question).filter_by(
                    name=question_text,
                    audience=audience_enum
                ).first()
                
                if not question:
                    print(f"Row {row_num}: Warning - Question not found: {question_text[:50]}... (Audience: {audience_text})")
                    responses_skipped += 1
                    continue
                
                # Check if response already exists
                existing_response = session.query(SelfAssessmentAnswer).filter_by(
                    organization_id=organization.id,
                    question_id=question.id
                ).first()
                
                if existing_response:
                    # Update existing response
                    setattr(existing_response, 'answer', response_text)
                    responses_updated += 1
                    print(f"Row {row_num}: Updated response for question: {question_text[:50]}...")
                else:
                    # Create new response
                    new_response = SelfAssessmentAnswer(
                        organization_id=organization.id,
                        question_id=question.id,
                        answer=response_text
                    )
                    session.add(new_response)
                    responses_created += 1
                    print(f"Row {row_num}: Created response for question: {question_text[:50]}...")
        
        print(f"Responses - Created: {responses_created}, Updated: {responses_updated}, Skipped: {responses_skipped}")
        return responses_created, responses_updated
    
    def sync_organization_data(self, csv_file_path: str) -> bool:
        """Sync data from a single organization CSV file."""
        try:
            csv_filename = Path(csv_file_path).name
            organization_name = self._extract_organization_name(csv_filename)
            
            print(f"\nProcessing organization: {organization_name}")
            print(f"CSV file: {csv_filename}")
            
            with self.SessionLocal() as session:
                try:
                    # Sync organization
                    organization = self.sync_organization(session, organization_name)
                    
                    # Sync responses
                    responses_created, responses_updated = self.sync_responses(
                        session, csv_file_path, organization
                    )
                    
                    # Commit changes
                    session.commit()
                    
                    print(f"Successfully synced {organization_name}: {responses_created} responses created, {responses_updated} updated")
                    return True
                    
                except Exception as e:
                    print(f"Error syncing {organization_name}: {str(e)}")
                    session.rollback()
                    raise
                    
        except Exception as e:
            print(f"Failed to sync organization data from {csv_file_path}: {str(e)}")
            return False
    
    def sync_all_organizations(self, data_directory: str) -> bool:
        """Sync all organization CSV files from the data directory."""
        try:
            # Create tables if they don't exist
            self.create_tables()
            
            data_path = Path(data_directory)
            if not data_path.exists():
                print(f"Data directory not found: {data_directory}")
                return False
            
            # Find all CSV files
            csv_files = list(data_path.glob("*.csv"))
            if not csv_files:
                print(f"No CSV files found in: {data_directory}")
                return False
            
            print(f"Found {len(csv_files)} CSV files to process:")
            for csv_file in csv_files:
                print(f"  - {csv_file.name}")
            
            # Process each CSV file
            total_success = 0
            total_failed = 0
            
            for csv_file in csv_files:
                if self.sync_organization_data(str(csv_file)):
                    total_success += 1
                else:
                    total_failed += 1
            
            print(f"\nSync Summary:")
            print(f"  Organizations processed successfully: {total_success}")
            print(f"  Organizations failed: {total_failed}")
            
            return total_failed == 0
            
        except Exception as e:
            print(f"Failed to sync all organizations: {str(e)}")
            return False


def main():
    """Main function to run the sync process."""
    # Path to the organization data directory
    data_directory = Path(__file__).parent.parent / "data" / "example_organization_questions_and_responses"
    
    if not data_directory.exists():
        print(f"Data directory not found: {data_directory}")
        return
    
    # Create sync service and run
    sync_service = OrganizationAnswerSyncService()
    success = sync_service.sync_all_organizations(str(data_directory))
    
    if success:
        print("\nOrganization answer synchronization completed successfully!")
    else:
        print("\nOrganization answer synchronization failed!")


if __name__ == "__main__":
    main()
