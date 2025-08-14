#!/usr/bin/env python3
"""
Script to parse Excel file and extract data from "Rotary" sheet.
Extracts columns: Question, Category, Sub-category / Clause, Audience (excluding Response)
"""

import pandas as pd
import os

def parse_rotary_data():
    # File paths
    input_file = "data/Cyber Essentials Questionnaire.xlsx"
    output_file = "data/rotary_data.csv"
    
    try:
        # Read the Excel file
        print(f"Reading Excel file: {input_file}")
        
        # First, let's check what sheets are available
        excel_file = pd.ExcelFile(input_file)
        print(f"Available sheets: {excel_file.sheet_names}")
        
        # Read the "Rotary" sheet
        if "Rotary" not in excel_file.sheet_names:
            print("Error: 'Rotary' sheet not found!")
            return False
            
        df = pd.read_excel(input_file, sheet_name="Rotary")
        
        print(f"Original data shape: {df.shape}")
        print(f"Original columns: {list(df.columns)}")
        
        # Define the columns we want to extract
        desired_columns = ["Question", "Category", "Sub-category / Clause", "Audience"]
        
        # Check which columns exist
        available_columns = []
        for col in desired_columns:
            if col in df.columns:
                available_columns.append(col)
            else:
                print(f"Warning: Column '{col}' not found in the sheet")
        
        if not available_columns:
            print("Error: None of the desired columns were found!")
            return False
            
        # Extract the desired columns
        extracted_df = df[available_columns].copy()
        
        # Remove any completely empty rows
        extracted_df = extracted_df.dropna(how='all')
        
        print(f"Extracted data shape: {extracted_df.shape}")
        print(f"Extracted columns: {list(extracted_df.columns)}")
        
        # Save to CSV
        extracted_df.to_csv(output_file, index=False)
        print(f"Data saved to: {output_file}")
        
        # Show first few rows
        print("\nFirst 5 rows of extracted data:")
        print(extracted_df.head())
        
        return True
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = parse_rotary_data()
    if success:
        print("\nData extraction completed successfully!")
    else:
        print("\nData extraction failed!") 