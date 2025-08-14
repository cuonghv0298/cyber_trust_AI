#!/usr/bin/env python3
"""
Parse cyber-essentials-self-assessment.csv into structured JSON format.
Structure: list[clause -> list[provision]]
"""

import csv
import json
import re
from typing import List, Dict, Any


def parse_csv_to_json(csv_file_path: str, output_file_path: str) -> List[Dict[str, Any]]:
    """
    Parse the cyber essentials CSV file into structured JSON format.
    
    Args:
        csv_file_path: Path to the CSV file
        output_file_path: Path to save the JSON output
    
    Returns:
        List of clauses, each containing provisions
    """
    clauses = []
    current_clause = None
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        # Skip header lines
        next(reader)  # Skip "2. Cyber Essentials mark questionnaire"
        next(reader)  # Skip empty line
        next(reader)  # Skip column headers
        
        for row in reader:
            if len(row) < 1 or not row[0].strip():
                continue
                
            clause_id = row[0].strip()
            description = row[1].strip() if len(row) > 1 else ""
            suggested_artefacts = row[2].strip() if len(row) > 2 else ""
            implementation_status = row[3].strip() if len(row) > 3 else ""
            remarks = row[4].strip() if len(row) > 4 else ""
            
            # Debug print
            print(f"Processing: {clause_id[:50]}...")
            
            # Check if this is a main clause (starts with A.X and has full description)
            # Handle both quoted and unquoted clauses
            if re.match(r'^"?A\.\d+\s+', clause_id):
                # This is a main clause header
                current_clause = {
                    "clause_id": clause_id.strip('"'),
                    "clause_description": description,
                    "provisions": []
                }
                clauses.append(current_clause)
                print(f"Found clause: {clause_id}")
            
            # Check if this is a provision (starts with A.X.Y (z))
            elif re.match(r'^A\.\d+\.\d+\s*\([a-z]+\)', clause_id) and description:
                # This is a provision under the current clause
                if current_clause is not None:
                    provision = {
                        "provision_id": clause_id,
                        "provision_description": description,
                        "suggested_artefacts": suggested_artefacts,
                        "implementation_status": implementation_status,
                        "remarks": remarks
                    }
                    current_clause["provisions"].append(provision)
                    print(f"Found provision: {clause_id}")
    
    # Save to JSON file
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(clauses, json_file, indent=2, ensure_ascii=False)
    
    return clauses


def main():
    """Main function to run the parsing"""
    csv_file_path = "data/cyber-essentials-self-assessment.csv"
    output_file_path = "data/cyber-essentials-structured.json"
    
    print("Parsing cyber-essentials-self-assessment.csv...")
    clauses = parse_csv_to_json(csv_file_path, output_file_path)
    
    print(f"Successfully parsed {len(clauses)} clauses")
    for clause in clauses:
        print(f"  - {clause['clause_id']}: {len(clause['provisions'])} provisions")
    
    print(f"JSON output saved to: {output_file_path}")


if __name__ == "__main__":
    main() 