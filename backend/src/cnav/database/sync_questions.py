"""
Sync script to import questions from organization response CSV files into the database.
This script processes the CSV files and creates Question records with clause mappings.
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# Import database models
from cnav.database.models import Base
from cnav.database.models.question import Question, AudienceType
from cnav.database.models.clause import Clause
from cnav.database.models.requirement_category import RequirementCategory

# Database configuration
DATABASE_URL = "sqlite:///./cnav.db"  # Adjust as needed


class QuestionSyncService:
    """Service to sync questions from CSV files to database."""
    
    def __init__(self, database_url: str = DATABASE_URL):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create database tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)
        
    def parse_csv_questions(self, csv_file_path: str) -> List[Dict]:
        """Parse the CSV file and extract unique questions with clause mappings."""
        questions = []
        seen_questions = set()
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                question_text = row.get('Question', '').strip()
                audience_text = row.get('Audience', '').strip()
                clause_text = row.get('Sub-category / Clause', '').strip()
                
                # Skip empty rows or rows without questions
                if not question_text or not audience_text:
                    continue
                
                # Create a unique key for the question to avoid duplicates
                question_key = (question_text, audience_text)
                
                if question_key not in seen_questions:
                    seen_questions.add(question_key)
                    
                    # Map audience text to enum
                    try:
                        audience_enum = self._map_audience_to_enum(audience_text)
                        if audience_enum:
                            question_data = {
                                'name': question_text,
                                'description': question_text,  # Using same text for both
                                'audience': audience_enum,
                                'clause_identifier': clause_text if clause_text else None
                            }
                            questions.append(question_data)
                    except ValueError as e:
                        print(f"Warning: Unknown audience type '{audience_text}' for question: {question_text[:50]}...")
                        continue
                        
        return questions
    
    def _map_audience_to_enum(self, audience_text: str) -> Optional[AudienceType]:
        """Map audience text to AudienceType enum."""
        audience_mapping = {
            'HR': AudienceType.HR,
            'IT': AudienceType.IT,
            'OWNER': AudienceType.OWNER,
            'Owner': AudienceType.OWNER,
            'owner': AudienceType.OWNER,
        }
        
        return audience_mapping.get(audience_text.strip())
    
    def _parse_clause_identifier(self, clause_text: str) -> Optional[Tuple[int, str]]:
        """
        Parse clause identifier from CSV format to (category_id, clause_identifier).
        Examples:
        - "A.1.4a" -> (1, "4a")
        - "A.2.4.b" -> (2, "4b")
        - "A.3.4" -> (3, "4")
        """
        if not clause_text:
            return None
            
        # Handle patterns like "A.1.4a", "A.2.4.b", "A.3.4"
        match = re.match(r'^A\.(\d+)\.(\d+)\.?([a-z])?$', clause_text)
        if match:
            category_id = int(match.group(1))
            clause_number = match.group(2)
            clause_letter = match.group(3) if match.group(3) else ""
            
            clause_identifier = f"{clause_number}{clause_letter}"
            return (category_id, clause_identifier)
        
        # Handle patterns like "A.1.4" (category level)
        match = re.match(r'^A\.(\d+)\.(\d+)$', clause_text)
        if match:
            category_id = int(match.group(1))
            clause_number = match.group(2)
            return (category_id, clause_number)
            
        return None
    
    def _find_clause_by_identifier(self, session: Session, clause_identifier_text: str) -> Optional[Clause]:
        """Find a clause by its identifier text from the CSV."""
        parsed = self._parse_clause_identifier(clause_identifier_text)
        if not parsed:
            return None
            
        category_id, clause_identifier = parsed
        
        # First try to find exact match
        clause = session.query(Clause).join(RequirementCategory).filter(
            RequirementCategory.id == category_id,
            Clause.clause_identifier == clause_identifier
        ).first()
        
        if clause:
            return clause
            
        # If no exact match, try to find by just the number part (for cases like "A.1.4")
        if clause_identifier.isdigit():
            clause = session.query(Clause).join(RequirementCategory).filter(
                RequirementCategory.id == category_id,
                Clause.clause_identifier.like(f"{clause_identifier}%")
            ).first()
            
        return clause
    
    def sync_questions(self, session: Session, questions_data: List[Dict]) -> int:
        """Sync questions to the database and create clause associations."""
        questions_created = 0
        questions_updated = 0
        associations_created = 0
        
        for question_info in questions_data:
            # Check if question already exists (by name and audience)
            existing_question = session.query(Question).filter_by(
                name=question_info['name'],
                audience=question_info['audience']
            ).first()
            
            if existing_question:
                # Update existing question
                existing_question.description = question_info['description']
                questions_updated += 1
                current_question = existing_question
                print(f"Updated question: {question_info['audience'].value} - {question_info['name'][:50]}...")
            else:
                # Create new question
                current_question = Question(
                    name=question_info['name'],
                    description=question_info['description'],
                    audience=question_info['audience']
                )
                session.add(current_question)
                questions_created += 1
                print(f"Created question: {question_info['audience'].value} - {question_info['name'][:50]}...")
            
            # Handle clause association
            clause_identifier = question_info.get('clause_identifier')
            if clause_identifier:
                clause = self._find_clause_by_identifier(session, clause_identifier)
                if clause:
                    # Check if association already exists
                    if clause not in current_question.clauses:
                        current_question.clauses.append(clause)
                        associations_created += 1
                        print(f"  -> Associated with clause: {clause.clause_identifier}")
                else:
                    print(f"  -> Warning: Could not find clause for identifier: {clause_identifier}")
        
        print(f"Summary: {questions_created} questions created, {questions_updated} questions updated, {associations_created} clause associations created")
        return questions_created + questions_updated
    
    def sync_data(self, csv_file_path: str) -> bool:
        """Main sync method to process CSV and update database."""
        try:
            # Create tables if they don't exist
            self.create_tables()
            
            # Parse CSV data
            print("Parsing CSV questions...")
            questions_data = self.parse_csv_questions(csv_file_path)
            print(f"Found {len(questions_data)} unique questions")
            
            # Group questions by audience for reporting
            audience_counts = {}
            clause_mappings = 0
            for q in questions_data:
                audience = q['audience'].value
                audience_counts[audience] = audience_counts.get(audience, 0) + 1
                if q.get('clause_identifier'):
                    clause_mappings += 1
            
            print("Questions by audience:")
            for audience, count in audience_counts.items():
                print(f"  {audience}: {count} questions")
            print(f"Questions with clause mappings: {clause_mappings}")
            
            # Sync to database
            with self.SessionLocal() as session:
                try:
                    # Sync questions
                    print("Syncing questions...")
                    total_processed = self.sync_questions(session, questions_data)
                    
                    # Commit changes
                    session.commit()
                    
                    print("Question sync completed successfully!")
                    return True
                    
                except Exception as e:
                    print(f"Error during sync: {str(e)}")
                    session.rollback()
                    raise
                    
        except Exception as e:
            print(f"Failed to sync questions: {str(e)}")
            return False


def main():
    """Main function to run the sync process."""
    # Path to one of the CSV files (they all contain the same questions)
    csv_file_path = Path(__file__).parent.parent / "data" / "example_organization_questions_and_responses" / "zublin.csv"
    
    if not csv_file_path.exists():
        print(f"CSV file not found: {csv_file_path}")
        return
    
    # Create sync service and run
    sync_service = QuestionSyncService()
    success = sync_service.sync_data(str(csv_file_path))
    
    if success:
        print("Question synchronization completed successfully!")
    else:
        print("Question synchronization failed!")


if __name__ == "__main__":
    main()
