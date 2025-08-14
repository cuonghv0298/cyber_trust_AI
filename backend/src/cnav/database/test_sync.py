"""
Test script to verify CSV parsing and database sync functionality.
Run this after running the sync_data.py script.
"""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.requirement_category import RequirementCategory
from models.clause import Clause

def test_database_query():
    """Test database queries after sync."""
    engine = create_engine("sqlite:///./cnav.db")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        # Test category count
        category_count = session.query(RequirementCategory).count()
        print(f"Total categories in database: {category_count}")
        
        # Test clause count
        clause_count = session.query(Clause).count()
        print(f"Total clauses in database: {clause_count}")
        
        # Show some examples
        print("\nSample categories:")
        categories = session.query(RequirementCategory).limit(3).all()
        for category in categories:
            print(f"  - {category.name} ({len(category.clauses)} clauses)")
        
        print("\nSample clauses:")
        clauses = session.query(Clause).limit(5).all()
        for clause in clauses:
            print(f"  - {clause.full_identifier}: {clause.name[:50]}...")
        
        # Test specific queries
        print("\nTest queries:")
        
        # Find a specific category
        category = session.query(RequirementCategory).filter(
            RequirementCategory.name.like("%Assets: People%")
        ).first()
        
        if category:
            print(f"Found category: {category.name}")
            print(f"Number of clauses: {len(category.clauses)}")
            
            # Show first few clauses in this category
            for clause in category.clauses[:3]:
                print(f"  - {clause.clause_identifier}: {clause.name[:50]}...")
        
        # Test clause lookup by full identifier
        clause = session.query(Clause).filter(Clause.clause_identifier == "4a").first()
        if clause:
            print(f"\nFound clause 4a: {clause.name[:50]}...")
            print(f"Category: {clause.category.name}")

if __name__ == "__main__":
    print("=== Database Query Test ===")
    test_database_query() 