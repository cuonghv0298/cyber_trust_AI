#!/usr/bin/env python3
"""
Script to import Rotary questionnaire data into the database
Reads from rotary_data.csv and creates categories, clauses, and questions with proper relationships
"""

import pandas as pd
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, RequirementCategory, Clause, Question, AudienceType
from typing import Dict, List, Tuple, Optional

def parse_clause_identifier(sub_category_clause: str) -> List[str]:
    """
    Parse the Sub-category / Clause column to extract clause identifiers
    Examples:
    - "A.1.4" -> ["A.1.4"]
    - "A.1.4a" -> ["A.1.4a"]
    - "A.2.4l, A.2.4.m" -> ["A.2.4l", "A.2.4.m"]
    """
    if pd.isna(sub_category_clause):
        return []
    
    # Split by comma and clean up
    clauses = [clause.strip() for clause in str(sub_category_clause).split(',')]
    return [clause for clause in clauses if clause]

def extract_category_and_clause(clause_identifier: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract category and clause parts from identifiers like "A.1.4a"
    Returns (category_part, clause_part)
    Examples:
    - "A.1.4" -> ("A.1", "4")
    - "A.1.4a" -> ("A.1", "4a")
    - "A.2.4.b" -> ("A.2", "4.b")
    """
    # Pattern to match formats like A.1.4, A.1.4a, A.2.4.b, etc.
    pattern = r'^([A-Z]\.\d+)\.(.+)$'
    match = re.match(pattern, clause_identifier)
    
    if match:
        return match.group(1), match.group(2)
    else:
        print(f"Warning: Could not parse clause identifier: {clause_identifier}")
        return None, None

def get_or_create_category(session, category_name: str, category_key: str) -> RequirementCategory:
    """Get existing category or create new one"""
    # Try to find existing category by name or create new
    category = session.query(RequirementCategory).filter(
        RequirementCategory.name == category_name
    ).first()
    
    if not category:
        category = RequirementCategory(
            name=category_name,
            description=f"Category for {category_key} requirements"
        )
        session.add(category)
        session.flush()  # Get the ID
        print(f"Created category: {category_name} (ID: {category.id})")
    
    return category

def get_or_create_clause(session, category: RequirementCategory, clause_identifier: str, clause_full_id: str) -> Clause:
    """Get existing clause or create new one"""
    # Try to find existing clause
    clause = session.query(Clause).filter(
        Clause.category_id == category.id,
        Clause.clause_identifier == clause_identifier
    ).first()
    
    if not clause:
        clause = Clause(
            category_id=category.id,
            clause_identifier=clause_identifier,
            name=f"Clause {clause_full_id}",
            description=f"Requirements for {clause_full_id}"
        )
        session.add(clause)
        session.flush()
        print(f"Created clause: {clause.full_identifier} - {clause.name}")
    
    return clause

def import_rotary_data(csv_file_path: str, db_url: str = 'sqlite:///rotary_data.db'):
    """Import data from CSV file into database"""
    
    # Create database engine
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Read CSV file
        print(f"Reading CSV file: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        
        print(f"Total rows in CSV: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        print()
        
        # Track statistics
        questions_created = 0
        mappings_created = 0
        errors = 0
        
        # Process each row
        for index, row in df.iterrows():
            try:
                question_text = row['Question']
                category_name = row['Category']
                sub_category_clause = row['Sub-category / Clause']
                audience_str = row['Audience'].strip()
                
                # Convert audience string to enum
                if audience_str == 'HR':
                    audience = AudienceType.HR
                elif audience_str == 'IT':
                    audience = AudienceType.IT
                elif audience_str == 'Owner':
                    audience = AudienceType.OWNER
                else:
                    print(f"Warning: Unknown audience type '{audience_str}' in row {index+1}")
                    continue
                
                # Create question
                question = Question(
                    name=question_text,
                    description=f"Question from {category_name} category",
                    audience=audience
                )
                session.add(question)
                session.flush()
                stats['questions_created'] += 1
                
                # Parse clause identifiers
                clause_identifiers = parse_clause_identifier(sub_category_clause)
                
                if not clause_identifiers:
                    print(f"Warning: No clause identifiers found in row {index+1}")
                    continue
                
                # Process each clause identifier
                for clause_full_id in clause_identifiers:
                    category_key, clause_id = extract_category_and_clause(clause_full_id)
                    
                    if not category_key or not clause_id:
                        print(f"Warning: Could not parse '{clause_full_id}' in row {index+1}")
                        continue
                    
                                    # Get or create category
                category = get_or_create_category(session, category_name, category_key)
                if category_name not in categories_seen:
                    categories_seen.add(category_name)
                    stats['categories_created'] += 1
                
                # Get or create clause
                clause = get_or_create_clause(session, category, clause_id, clause_full_id)
                if clause_full_id not in clauses_seen:
                    clauses_seen.add(clause_full_id)
                    stats['clauses_created'] += 1
                
                # Create question-clause mapping
                question.add_clause(clause)
                stats['mappings_created'] += 1
                
                # Commit every 10 rows to avoid large transactions
                if (index + 1) % 10 == 0:
                    session.commit()
                    print(f"Processed {index + 1} rows...")
                    
            except Exception as e:
                print(f"Error processing row {index+1}: {str(e)}")
                stats['errors'] += 1
                session.rollback()
        
        # Final commit
        session.commit()
        
        # Print statistics
        print("\n=== Import Summary ===")
        print(f"Questions created: {stats['questions_created']}")
        print(f"Categories found/created: {len(session.query(RequirementCategory).all())}")
        print(f"Clauses found/created: {len(session.query(Clause).all())}")
        print(f"Question-clause mappings created: {stats['mappings_created']}")
        print(f"Errors: {stats['errors']}")
        
        # Show some sample data
        print("\n=== Sample Data ===")
        print("Categories:")
        for category in session.query(RequirementCategory).limit(5):
            print(f"  - {category.name} (ID: {category.id})")
        
        print("\nClauses:")
        for clause in session.query(Clause).limit(5):
            print(f"  - {clause.full_identifier}: {clause.name}")
        
        print("\nQuestions by audience:")
        for audience_type in AudienceType:
            count = session.query(Question).filter(Question.audience == audience_type).count()
            print(f"  - {audience_type.value}: {count} questions")
        
        # Show some mappings
        print("\nSample question-clause mappings:")
        for question in session.query(Question).limit(3):
            print(f"Question [{question.audience.value}]: {question.name[:50]}...")
            for clause in question.clauses:
                print(f"  → {clause.full_identifier}")
        
        print(f"\nData successfully imported to: {db_url}")
        return True
        
    except Exception as e:
        print(f"Error during import: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

def main():
    """Main function to run the import"""
    csv_file = "rotary_data.csv"
    db_file = "rotary_questionnaire.db"
    
    print("Starting Rotary Data Import...")
    print("=" * 50)
    
    success = import_rotary_data(csv_file, f'sqlite:///{db_file}')
    
    if success:
        print("\n✅ Import completed successfully!")
        print(f"Database file: {db_file}")
    else:
        print("\n❌ Import failed!")

if __name__ == "__main__":
    main() 