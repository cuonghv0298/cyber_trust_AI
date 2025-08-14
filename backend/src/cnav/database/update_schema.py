#!/usr/bin/env python3
"""
Script to update the database schema with new tables.
Run this after adding new models to create the corresponding database tables.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from cnav.database.models import Base

# Database configuration - matches your existing setup
DATABASE_URL = "sqlite:///./cnav.db"

def update_database_schema():
    """Update database schema by creating all tables defined in models."""
    
    print("Updating database schema...")
    print(f"Database: {DATABASE_URL}")
    
    # Create engine
    engine = create_engine(DATABASE_URL, echo=False)
    
    # Create all tables (this is safe - won't recreate existing tables)
    print("Creating new tables (if they don't exist)...")
    Base.metadata.create_all(bind=engine)
    
    # Verify the new tables were created
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        # Check if new tables exist
        result = session.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('system_prompt_runs', 'evaluation_runs')
            ORDER BY name;
        """))
        
        new_tables = [row[0] for row in result.fetchall()]
        
        if new_tables:
            print(f"✅ Successfully created tables: {', '.join(new_tables)}")
        else:
            print("ℹ️  Tables may already exist or there was an issue.")
        
        # Show all tables for verification
        print("\nAll tables in database:")
        result = session.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
        """))
        
        all_tables = [row[0] for row in result.fetchall()]
        for table in all_tables:
            print(f"  - {table}")
    
    print("\n✅ Schema update completed!")

def show_table_info():
    """Show information about the new tables."""
    
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        print("\n📊 Table Information:")
        
        # System Prompt Runs table
        try:
            result = session.execute(text("PRAGMA table_info(system_prompt_runs);"))
            columns = result.fetchall()
            print("\nsystem_prompt_runs columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        except Exception as e:
            print(f"Could not get info for system_prompt_runs: {e}")
        
        # Evaluation Runs table  
        try:
            result = session.execute(text("PRAGMA table_info(evaluation_runs);"))
            columns = result.fetchall()
            print("\nevaluation_runs columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        except Exception as e:
            print(f"Could not get info for evaluation_runs: {e}")

def verify_relationships():
    """Verify that foreign key relationships are properly set up."""
    
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        print("\n🔗 Foreign Key Relationships:")
        
        # Check evaluation_runs -> system_prompt_runs
        try:
            result = session.execute(text("PRAGMA foreign_key_list(evaluation_runs);"))
            fks = result.fetchall()
            print("\nevaluation_runs foreign keys:")
            for fk in fks:
                print(f"  - {fk[3]} -> {fk[2]}.{fk[4]}")
        except Exception as e:
            print(f"Could not get foreign keys for evaluation_runs: {e}")
        
        # Check clause_system_prompts -> system_prompt_runs  
        try:
            result = session.execute(text("PRAGMA foreign_key_list(clause_system_prompts);"))
            fks = result.fetchall()
            print("\nclause_system_prompts foreign keys:")
            for fk in fks:
                print(f"  - {fk[3]} -> {fk[2]}.{fk[4]}")
        except Exception as e:
            print(f"Could not get foreign keys for clause_system_prompts: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("Database Schema Update Script")
    print("=" * 50)
    
    update_database_schema()
    show_table_info()
    verify_relationships()
    
    print("\n" + "=" * 50)
    print("Schema update complete!")
    print("You can now use SystemPromptRun and EvaluationRun models.")
    print("=" * 50) 