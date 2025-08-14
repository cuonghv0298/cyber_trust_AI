import json
import re
import pandas as pd
from typing import Optional
from dataclasses import asdict

from data_models import Question

def extract_audience_entities(text: str) -> Optional[list[str]]:
    """
    Extract entities from a string where entities are separated by commas, 'or', or both.
    """
    if not isinstance(text, str) or pd.isna(text) or text.strip() == "":
        return None
    
    # Pattern explanation:
    # \s*,\s*(?:or\s*)? - matches comma with optional whitespace, optionally followed by "or"
    # |\s+or\s+ - OR matches "or" with required whitespace on both sides
    pattern = r'\s*,\s*(?:or\s*)?|\s+or\s+'
    
    # Split the text using the regex pattern
    entities = re.split(pattern, text)
    
    # Clean up the results: strip whitespace and convert to lowercase
    cleaned_entities = [entity.strip().lower() for entity in entities if entity.strip()]
    
    return cleaned_entities if cleaned_entities else None

def load_fake_questions(file_path: str) -> list[Question]:
    """Load questions from fake_questions.json"""
    questions = []
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    for item in data:
        question = Question(
            _id=str(item.get('_id', '')),
            question=item.get('question', ''),
            audience=item.get('audience', None),  # Already in list format
            cyberessentials_requirement=item.get('cyberessentials_requirement', None),
            group_tag=item.get('group_tag', None)
        )
        questions.append(question)
    
    return questions

def load_sample_company_qa(file_path: str) -> list[Question]:
    """Load questions from sample_company_qa.csv"""
    questions = []
    
    df = pd.read_csv(file_path)
    
    for index, row in df.iterrows():
        # Extract audience entities and convert to list format
        audience_raw = extract_audience_entities(row["Audience"])
        
        question = Question(
            _id=str(row["Item"]),
            question=row["Questions"],
            audience=audience_raw,
            cyberessentials_requirement=None,  # Not available in this dataset
            group_tag=None  # Not available in this dataset
        )
        questions.append(question)
    
    return questions

def load_cyberessentials_template(file_path: str) -> list[Question]:
    """Load questions from cyberessentials_template_questions.csv"""
    questions = []
    
    df = pd.read_csv(file_path)
    
    for index, row in df.iterrows():
        # Handle NaN values
        cyberessentials_req = row["Cyberessentials Requirement"] if pd.notna(row["Cyberessentials Requirement"]) else None
        group_tag = row["Group Tag"] if pd.notna(row["Group Tag"]) else None
        
        question = Question(
            _id=str(row["Item"]),
            question=row["Questions"],
            audience=None,  # Not available in this dataset
            cyberessentials_requirement=cyberessentials_req,
            group_tag=group_tag
        )
        questions.append(question)
    
    return questions

def main():
    # Data source paths
    data_source_path_1 = "data/fake_questions.json"
    data_source_path_2 = "data/sample_company_qa.csv"
    data_source_path_3 = "data/cyberessentials_template_questions.csv"
    
    # Load questions from all sources
    print("Loading questions from fake_questions.json...")
    fake_questions = load_fake_questions(data_source_path_1)
    print(f"Loaded {len(fake_questions)} questions from fake_questions.json")
    
    print("Loading questions from sample_company_qa.csv...")
    company_questions = load_sample_company_qa(data_source_path_2)
    print(f"Loaded {len(company_questions)} questions from sample_company_qa.csv")
    
    print("Loading questions from cyberessentials_template_questions.csv...")
    template_questions = load_cyberessentials_template(data_source_path_3)
    print(f"Loaded {len(template_questions)} questions from cyberessentials_template_questions.csv")
    
    # Combine all questions
    all_questions = []
    
    # Add fake questions (keep original IDs)
    all_questions.extend(fake_questions)
    
    # Add company questions with offset IDs
    offset_id = len(all_questions)
    for i, question in enumerate(company_questions):
        question._id = str(offset_id + i + 1)
        all_questions.append(question)
    
    # Add template questions with offset IDs
    offset_id = len(all_questions)
    for i, question in enumerate(template_questions):
        question._id = str(offset_id + i + 1)
        all_questions.append(question)
    
    print(f"Total questions combined: {len(all_questions)}")
    
    # Convert to dictionaries for JSON serialization
    questions_dict = [asdict(question) for question in all_questions]
    
    # Save to JSON file
    output_path = "data/questions.json"
    with open(output_path, 'w') as f:
        json.dump(questions_dict, f, indent=4)
    
    print(f"Successfully saved {len(questions_dict)} questions to {output_path}")
    
    # Print sample of questions for verification
    print("\nSample questions:")
    for i, question in enumerate(all_questions[:3]):
        print(f"{i+1}. ID: {question._id}")
        print(f"   Question: {question.question[:100]}...")
        print(f"   Audience: {question.audience}")
        print(f"   Requirement: {question.cyberessentials_requirement}")
        print(f"   Group Tag: {question.group_tag}")
        print()

if __name__ == "__main__":
    main()