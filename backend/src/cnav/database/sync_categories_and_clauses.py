"""
Sync script to import data from category_clause_definition.csv into the database.
This script processes the CSV file and creates/updates RequirementCategory and Clause records.
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# Import database models
from cnav.database.models import Base
from cnav.database.models.requirement_category import RequirementCategory
from cnav.database.models.clause import Clause

# Database configuration
DATABASE_URL = "sqlite:///./cnav.db"  # Adjust as needed


class CsvSyncService:
    """Service to sync CSV data with database tables."""
    
    def __init__(self, database_url: str = DATABASE_URL):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create database tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)
        
    def parse_csv_data(self, csv_file_path: str) -> Dict[str, List[Dict]]:
        """Parse the CSV file and extract categories and clauses."""
        categories = {}
        current_category = None
        current_category_id = None
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            # Skip header rows until we find the actual data
            for row in reader:
                if len(row) >= 4 and row[0] == "Clause":
                    break
                    
            # Process data rows
            for row in reader:
                if len(row) < 2:
                    continue
                    
                clause_text = row[0].strip()
                description = row[1].strip()
                
                # Skip empty rows
                if not clause_text and not description:
                    continue
                    
                # Check if this is a new category section
                if self._is_category_row(clause_text, description):
                    category_info = self._parse_category(clause_text, description)
                    if category_info:
                        current_category = category_info['name']
                        current_category_id = category_info['id']
                        
                        if current_category not in categories:
                            categories[current_category] = {
                                'id': current_category_id,
                                'name': current_category,
                                'description': category_info['description'],
                                'clauses': []
                            }
                
                # Check if this is a clause row
                elif self._is_clause_row(clause_text) and current_category and current_category_id is not None:
                    clause_info = self._parse_clause(clause_text, description, current_category_id)
                    if clause_info:
                        categories[current_category]['clauses'].append(clause_info)
        
        return categories
    
    def _is_category_row(self, clause_text: str, description: str) -> bool:
        """Check if this row represents a category."""
        # Categories typically start with A.1, A.2, etc. and have empty or minimal description
        category_pattern = r'^A\.\d+\s+'
        return bool(re.match(category_pattern, clause_text)) and len(description.strip()) == 0
    
    def _is_clause_row(self, clause_text: str) -> bool:
        """Check if this row represents a clause."""
        # Clauses typically match pattern like A.1.4 (a), A.2.4 (b), etc.
        clause_pattern = r'^A\.\d+\.\d+\s*\([a-z]\)$'
        return bool(re.match(clause_pattern, clause_text))
    
    def _parse_category(self, clause_text: str, description: str) -> Optional[Dict]:
        """Parse category information from the row."""
        # Extract category ID and name (e.g., "A.1 Assets: People – ..." -> id=1, name="Assets: People – ...")
        match = re.match(r'^A\.(\d+)\s+(.+)', clause_text)
        if not match:
            return None
            
        category_id = int(match.group(1))
        category_name = match.group(2)
        
        # Use the category name as description since description column is empty for categories
        category_description = category_name
            
        return {
            'id': category_id,
            'name': category_name,
            'description': category_description
        }
    
    def _parse_clause(self, clause_text: str, description: str, category_id: int) -> Optional[Dict]:
        """Parse clause information from the row."""
        # Extract clause identifier (e.g., "4a" from "A.1.4 (a)")
        match = re.match(r'^A\.\d+\.(\d+)\s*\(([a-z])\)$', clause_text)
        if not match:
            return None
            
        clause_number = match.group(1)
        clause_letter = match.group(2)
        clause_identifier = f"{clause_number}{clause_letter}"
        
        # Generate a name from the first part of the description
        name = description[:100] + "..." if len(description) > 100 else description
        if not name:
            name = f"Clause {clause_identifier}"
        
        return {
            'category_id': category_id,
            'clause_identifier': clause_identifier,
            'name': name,
            'description': description
        }
    
    def sync_categories(self, session: Session, categories_data: Dict) -> Dict[str, RequirementCategory]:
        """Sync categories to the database."""
        categories_map = {}
        
        for category_name, category_info in categories_data.items():
            # Check if category already exists
            existing_category = session.query(RequirementCategory).filter_by(
                name=category_info['name']
            ).first()
            
            if existing_category:
                # Update existing category
                existing_category.description = category_info['description']
                category = existing_category
                print(f"Updated category: {category_info['name']}")
            else:
                # Create new category
                category = RequirementCategory(
                    name=category_info['name'],
                    description=category_info['description']
                )
                session.add(category)
                print(f"Created category: {category_info['name']}")
            
            categories_map[category_name] = category
            
        return categories_map
    
    def sync_clauses(self, session: Session, categories_data: Dict, categories_map: Dict[str, RequirementCategory]):
        """Sync clauses to the database."""
        clauses_created = 0
        clauses_updated = 0
        
        for category_name, category_info in categories_data.items():
            category = categories_map[category_name]
            
            for clause_info in category_info['clauses']:
                # Check if clause already exists
                existing_clause = session.query(Clause).filter_by(
                    category_id=category.id,
                    clause_identifier=clause_info['clause_identifier']
                ).first()
                
                if existing_clause:
                    # Update existing clause
                    existing_clause.name = clause_info['name']
                    existing_clause.description = clause_info['description']
                    clauses_updated += 1
                    print(f"Updated clause: {category.name} - {clause_info['clause_identifier']}")
                else:
                    # Create new clause
                    clause = Clause(
                        category_id=category.id,
                        clause_identifier=clause_info['clause_identifier'],
                        name=clause_info['name'],
                        description=clause_info['description']
                    )
                    session.add(clause)
                    clauses_created += 1
                    print(f"Created clause: {category.name} - {clause_info['clause_identifier']}")
        
        print(f"Summary: {clauses_created} clauses created, {clauses_updated} clauses updated")
    
    def sync_data(self, csv_file_path: str) -> bool:
        """Main sync method to process CSV and update database."""
        try:
            # Create tables if they don't exist
            self.create_tables()
            
            # Parse CSV data
            print("Parsing CSV data...")
            categories_data = self.parse_csv_data(csv_file_path)
            print(f"Found {len(categories_data)} categories")
            
            # Sync to database
            with self.SessionLocal() as session:
                try:
                    # Sync categories first
                    print("Syncing categories...")
                    categories_map = self.sync_categories(session, categories_data)
                    
                    # Commit categories before syncing clauses
                    session.commit()
                    
                    # Sync clauses
                    print("Syncing clauses...")
                    self.sync_clauses(session, categories_data, categories_map)
                    
                    # Commit clauses
                    session.commit()
                    
                    print("Data sync completed successfully!")
                    return True
                    
                except Exception as e:
                    print(f"Error during sync: {str(e)}")
                    session.rollback()
                    raise
                    
        except Exception as e:
            print(f"Failed to sync data: {str(e)}")
            return False


def main():
    """Main function to run the sync process."""
    # Path to the CSV file
    csv_file_path = Path(__file__).parent.parent / "data" / "category_clause_definition.csv"
    
    if not csv_file_path.exists():
        print(f"CSV file not found: {csv_file_path}")
        return
    
    # Create sync service and run
    sync_service = CsvSyncService()
    success = sync_service.sync_data(str(csv_file_path))
    
    if success:
        print("Data synchronization completed successfully!")
    else:
        print("Data synchronization failed!")


if __name__ == "__main__":
    main()