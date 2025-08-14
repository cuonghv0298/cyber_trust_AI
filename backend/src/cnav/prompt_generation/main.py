from dotenv import load_dotenv

load_dotenv()

import json
import os
from typing import List, Dict, Any
import logging
import re
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
# from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from langchain.schema import BaseMessage

from cnav.prompt_generation.prompts import SYSTEM_PROMPT_TEMPLATE, USER_PROMPT_TEMPLATE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    # handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

SAVE_DIR = "./output"
os.makedirs(SAVE_DIR, exist_ok=True)

LLM_MODEL_NAME = "openai:gpt-4.1"

def load_cyber_essentials_data(file_path: str) -> List[Dict[str, Any]]:
    """Load the structured cyber essentials data from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # This is for debugging purposes
        assert isinstance(data, list), "Data must be a list"
        data = data[:1]

        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find the data file: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file: {file_path}")


def provision_id_to_snake_case(provision_id: str) -> str:
    """Convert provision ID to snake_case filename."""
    # Remove spaces and special characters, convert to lowercase
    # Example: "A.1.4 (a)" -> "a_1_4_a"
    cleaned = re.sub(r'[^\w\s]', '_', provision_id.lower())
    cleaned = re.sub(r'\s+', '_', cleaned)
    cleaned = re.sub(r'_+', '_', cleaned)
    cleaned = cleaned.strip('_')
    return cleaned


def create_timestamped_directory(base_dir: str) -> str:
    """Create a timestamped directory for this run."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    timestamped_dir = os.path.join(base_dir, timestamp)
    os.makedirs(timestamped_dir, exist_ok=True)
    return timestamped_dir


def save_prompt_to_file(prompt_content: str, provision_id: str, clause_id: str, output_dir: str) -> str:
    """Save a single prompt to a markdown file."""
    filename = provision_id_to_snake_case(provision_id) + ".md"
    filepath = os.path.join(output_dir, filename)
    
    # Create markdown content with metadata
    markdown_content = f"""# Evaluation Prompt for {provision_id}

## Clause Information
**Clause ID**: {clause_id}

## Provision ID
{provision_id}

## Evaluation Prompt

{prompt_content}
"""
    
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(markdown_content)
        return filepath
    except Exception as e:
        raise Exception(f"Failed to save prompt to {filepath}: {str(e)}")

def create_prompt_generation_chain():
    """Create the LangChain chain for prompt generation."""
    # Initialize the chat model
    # llm = ChatOpenAI(
    #     model=LLM_MODEL_NAME,
    #     temperature=0.1,  # Low temperature for consistent, focused outputs
    #     # max_completion_tokens=2000   # Sufficient for detailed evaluation prompts
    # )
    llm = init_chat_model(
        model=LLM_MODEL_NAME,
        temperature=0.1,
    )
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT_TEMPLATE),
        HumanMessagePromptTemplate.from_template(USER_PROMPT_TEMPLATE)
    ])
    
    # Create the output parser
    output_parser = StrOutputParser()
    
    # Create the chain
    chain = prompt | llm | output_parser
    
    return chain


def generate_evaluation_prompts(clauses_data: List[Dict[str, Any]], chain, output_dir: str) -> List[Dict[str, Any]]:
    """Generate evaluation prompts for all clause-provision pairs and save each one immediately."""
    results = []
    
    logger.info("Starting prompt generation for all clause-provision pairs...")
    
    for clause_idx, clause in enumerate(clauses_data):
        logger.info(f"\nProcessing clause {clause_idx + 1}/{len(clauses_data)}: {clause['clause_id'][:50]}...")
        
        for provision_idx, provision in enumerate(clause['provisions']):
            logger.info(f"  Processing provision {provision_idx + 1}/{len(clause['provisions'])}: {provision['provision_id']}")
            
            try:
                # Prepare the input for the chain
                input_data = {
                    "clause_id": clause['clause_id'],
                    "clause_description": clause['clause_description'] or "N/A",
                    "provision_id": provision['provision_id'],
                    "provision_description": provision['provision_description'],
                    "suggested_artefacts": provision['suggested_artefacts'] or "N/A"
                }
                
                # Generate the evaluation prompt
                evaluation_prompt = chain.invoke(input_data)
                
                # Save the prompt to individual file immediately
                try:
                    saved_filepath = save_prompt_to_file(
                        evaluation_prompt,
                        provision['provision_id'],
                        clause['clause_id'],
                        output_dir
                    )
                    logger.info(f"    ✓ Saved prompt to: {saved_filepath}")
                except Exception as save_error:
                    logger.error(f"    ✗ Error saving prompt file: {str(save_error)}")
                
                # Store the result for summary
                result = {
                    "clause_id": clause['clause_id'],
                    "clause_description": clause['clause_description'],
                    "provision_id": provision['provision_id'],
                    "provision_description": provision['provision_description'],
                    "suggested_artefacts": provision['suggested_artefacts'],
                    "evaluation_prompt": evaluation_prompt,
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "saved_to": saved_filepath if 'saved_filepath' in locals() else None
                }
                
                results.append(result)
                logger.info(f"    ✓ Generated evaluation prompt for {provision['provision_id']}")
                
            except Exception as e:
                logger.error(f"    ✗ Error processing {provision['provision_id']}: {str(e)}")
                # Still add the provision but mark the error
                error_result = {
                    "clause_id": clause['clause_id'],
                    "clause_description": clause['clause_description'],
                    "provision_id": provision['provision_id'],
                    "provision_description": provision['provision_description'],
                    "suggested_artefacts": provision['suggested_artefacts'],
                    "evaluation_prompt": f"ERROR: Failed to generate prompt - {str(e)}",
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "saved_to": None
                }
                results.append(error_result)
    
    return results


def save_results(results: List[Dict[str, Any]], output_file: str):
    """Save the generated evaluation prompts to JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(results, file, indent=2, ensure_ascii=False)
        logger.info(f"\n✓ Results saved to: {output_file}")
    except Exception as e:
        logger.error(f"\n✗ Error saving results: {str(e)}")


def create_index_file(results: List[Dict[str, Any]], output_dir: str):
    """Create an index.md file listing all generated prompts."""
    index_file = os.path.join(output_dir, "index.md")
    
    try:
        with open(index_file, 'w', encoding='utf-8') as file:
            file.write("# Cyber Essentials Evaluation Prompts Index\n\n")
            file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            successful_results = [r for r in results if not r['evaluation_prompt'].startswith('ERROR:')]
            failed_results = [r for r in results if r['evaluation_prompt'].startswith('ERROR:')]
            
            file.write(f"## Summary\n\n")
            file.write(f"- Total provisions: {len(results)}\n")
            file.write(f"- Successfully generated: {len(successful_results)}\n")
            file.write(f"- Failed: {len(failed_results)}\n\n")
            
            # Group by clauses
            current_clause = None
            for result in results:
                if result['clause_id'] != current_clause:
                    current_clause = result['clause_id']
                    file.write(f"## {current_clause}\n\n")
                
                if result['evaluation_prompt'].startswith('ERROR:'):
                    file.write(f"- ❌ **{result['provision_id']}** - Generation failed\n")
                else:
                    filename = provision_id_to_snake_case(result['provision_id']) + ".md"
                    file.write(f"- ✅ **{result['provision_id']}** - [{filename}]({filename})\n")
            
            if failed_results:
                file.write(f"\n## Failed Generations\n\n")
                for result in failed_results:
                    file.write(f"- **{result['provision_id']}**: {result['evaluation_prompt']}\n")
        
        logger.info(f"✓ Index file created: {index_file}")
        
    except Exception as e:
        logger.error(f"✗ Error creating index file: {str(e)}")


def main():
    """Main function to execute the prompt generation process."""
    # File paths
    data_file = "../data/cyber-essentials-structured.json"
    
    logger.info("=== Cyber Essentials Evaluation Prompt Generator ===")
    logger.info("This tool generates evaluation prompts for auditors to assess")
    logger.info("organization compliance with Cyber Essentials provisions.\n")
    
    try:
        # Create timestamped output directory
        logger.info("Creating timestamped output directory...")
        output_dir = create_timestamped_directory(SAVE_DIR)
        logger.info(f"✓ Output directory created: {output_dir}")
        
        # Load the structured data
        logger.info("Loading cyber essentials data...")
        clauses_data = load_cyber_essentials_data(data_file)
        
        total_provisions = sum(len(clause['provisions']) for clause in clauses_data)
        logger.info(f"Loaded {len(clauses_data)} clauses with {total_provisions} total provisions")
        
        # Create the chain
        logger.info("\nInitializing LangChain components...")
        chain = create_prompt_generation_chain()
        logger.info("✓ Chain created successfully")
        
        # Generate evaluation prompts (saves each one immediately)
        logger.info("\nGenerating evaluation prompts...")
        results = generate_evaluation_prompts(clauses_data, chain, output_dir)
        
        # Save summary results to JSON file
        logger.info(f"\nSaving summary results...")
        summary_file = os.path.join(output_dir, "generation_summary.json")
        save_results(results, summary_file)
        
        # Summary
        successful_generations = len([r for r in results if not r['evaluation_prompt'].startswith('ERROR:')])
        failed_generations = len(results) - successful_generations
        
        logger.info(f"\n=== Generation Complete ===")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Total provisions processed: {len(results)}")
        logger.info(f"Successful generations: {successful_generations}")
        logger.info(f"Failed generations: {failed_generations}")
        
        if failed_generations > 0:
            logger.info(f"\nFailed provisions:")
            for result in results:
                if result['evaluation_prompt'].startswith('ERROR:'):
                    logger.info(f"  - {result['provision_id']}: {result['evaluation_prompt']}")
        
        # Save a simple index file listing all generated prompts
        logger.info("Creating index file...")
        create_index_file(results, output_dir)
        
    except Exception as e:
        logger.error(f"✗ Fatal error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

