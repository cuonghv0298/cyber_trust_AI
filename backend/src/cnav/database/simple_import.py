#!/usr/bin/env python3
"""
Simple script to import Rotary questionnaire data into the database
"""

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, RequirementCategory, Clause, Question, AudienceType

def simple_import():
    """Simple import function"""
    # Create database
    engine = create_engine('sqlite:///rotary_questionnaire.db', echo=False)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Read CSV
    df = pd.read_csv('rotary_data.csv')
    print(f"Processing {len(df)} rows from CSV...")
    
    # Create a simple category mapping
    category_map = {}
    
    for _, row in df.iterrows():
        question_text = row['Question']
        category_name = row['Category']
        audience_str = row['Audience'].strip()
        
        # Map audience
        if audience_str == 'HR':
            audience = AudienceType.HR
        elif audience_str == 'IT':
            audience = AudienceType.IT
        elif audience_str == 'Owner':
            audience = AudienceType.OWNER
        else:
            continue
        
        # Get or create category
        if category_name not in category_map:
            category = RequirementCategory(
                name=category_name,
                description=f"Category for {category_name}"
            )
            session.add(category)
            session.flush()
            category_map[category_name] = category
        else:
            category = category_map[category_name]
        
        # Create question
        question = Question(
            name=question_text,
            description=f"Question from {category_name}",
            audience=audience
        )
        session.add(question)
    
    session.commit()
    print("Import completed!")
    
    # Show statistics
    print(f"Categories: {session.query(RequirementCategory).count()}")
    print(f"Questions: {session.query(Question).count()}")
    
    for audience_type in AudienceType:
        count = session.query(Question).filter(Question.audience == audience_type).count()
        print(f"{audience_type.value}: {count} questions")
    
    session.close()

if __name__ == "__main__":
    simple_import() 