from dotenv import load_dotenv

load_dotenv()

import json
import os
from typing import List, Dict, Any, Optional
import logging
import re
from datetime import datetime
from textwrap import dedent

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from cnav.prompt_generation.prompts import SYSTEM_PROMPT_TEMPLATE, USER_PROMPT_TEMPLATE
from cnav.database.models import Base
from cnav.database.models.requirement_category import RequirementCategory
from cnav.database.models.clause import Clause
from cnav.database.models.question import Question, AudienceType

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

SAVE_DIR = "./output"
os.makedirs(SAVE_DIR, exist_ok=True)

LLM_MODEL_NAME = "openai:gpt-4.1"
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'database', 'cnav.db')}"


class DatabaseMetaPromptingPipeline:
    """Pipeline for generating evaluation prompts using database data."""
    
    def __init__(self, database_url: str = DATABASE_URL):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def load_clauses_from_database(self, session: Session) -> List[Dict[str, Any]]:
        """Load clauses and their associated data from the database."""
        logger.info("Loading clauses from database...")
        
        # Query all requirement categories with their clauses
        categories = session.query(RequirementCategory).all()
        
        clauses_data = []
        
        for category in categories:
            logger.info(f"Processing category: {category.name}")
            
            for clause in category.clauses:
                logger.info(f"  Processing clause: {clause.full_identifier}")
                
                # Get questions associated with this clause
                questions = clause.questions
                
                # Format questions for the dependent_questions field
                dependent_questions = []
                for question in questions:
                    dependent_questions.append({
                        'id': question.id,
                        'name': question.name,
                        'audience': question.audience.value,
                        'description': question.description
                    })
                
                # Create a clause data structure that matches the expected format
                # Note: In the database, clauses are equivalent to provisions from the JSON structure
                clause_data = {
                    'clause_id': f"A.{clause.full_identifier}",  # Format as A.1.4a, A.2.1b, etc.
                    'clause_description': category.description,
                    'provisions': [{
                        'provision_id': f"A.{clause.full_identifier}",
                        'provision_description': clause.description,
                        'suggested_artefacts': "N/A",  # Not available in current database schema
                        'dependent_questions': dependent_questions
                    }]
                }
                
                clauses_data.append(clause_data)
        
        logger.info(f"Loaded {len(clauses_data)} clauses from database")
        return clauses_data
    
    def provision_id_to_snake_case(self, provision_id: str) -> str:
        """Convert provision ID to snake_case filename."""
        # Remove spaces and special characters, convert to lowercase
        # Example: "A.1.4a" -> "a_1_4_a"
        cleaned = re.sub(r'[^\w\s]', '_', provision_id.lower())
        cleaned = re.sub(r'\s+', '_', cleaned)
        cleaned = re.sub(r'_+', '_', cleaned)
        cleaned = cleaned.strip('_')
        return cleaned
    
    def create_timestamped_directory(self, base_dir: str) -> str:
        """Create a timestamped directory for this run."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        timestamped_dir = os.path.join(base_dir, timestamp)
        os.makedirs(timestamped_dir, exist_ok=True)
        return timestamped_dir
    
    def save_prompt_to_file(self, prompt_content: str, provision_id: str, clause_id: str, output_dir: str) -> str:
        """Save a single prompt to a markdown file."""
        filename = self.provision_id_to_snake_case(provision_id) + ".md"
        filepath = os.path.join(output_dir, filename)
        
        # Create markdown content with metadata
        markdown_content = dedent(f"""# Evaluation Prompt for {provision_id}
            ## Clause Information
            **Clause ID**: {clause_id}

            ## Provision ID
            {provision_id}

            ## Evaluation Prompt

            {prompt_content}
            """)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(markdown_content)
            return filepath
        except Exception as e:
            raise Exception(f"Failed to save prompt to {filepath}: {str(e)}")
    
    def create_prompt_generation_chain(self):
        """Create the LangChain chain for prompt generation."""
        # Initialize the chat model
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
        chain.name = "metaprompting_chain"

        return chain
    
    def format_dependent_questions(self, dependent_questions: List[Dict[str, Any]]) -> str:
        """Format dependent questions for the prompt template."""
        if not dependent_questions:
            return "No dependent questions found."
        
        formatted_questions = []
        for question in dependent_questions:
            formatted_questions.append(
                f"- **{question['audience']}**: {question['name']}"
            )
        
        return "\n".join(formatted_questions)
    
    def generate_evaluation_prompts(self, clauses_data: List[Dict[str, Any]], chain, output_dir: str) -> List[Dict[str, Any]]:
        """Generate evaluation prompts for all clause-provision pairs and save each one immediately."""
        results = []
        
        logger.info("Starting prompt generation for all clause-provision pairs...")
        
        for clause_idx, clause in enumerate(clauses_data):
            logger.info(f"\nProcessing clause {clause_idx + 1}/{len(clauses_data)}: {clause['clause_id']}")
            
            for provision_idx, provision in enumerate(clause['provisions']):
                logger.info(f"  Processing provision {provision_idx + 1}/{len(clause['provisions'])}: {provision['provision_id']}")
                
                try:
                    # Format dependent questions
                    dependent_questions_formatted = self.format_dependent_questions(
                        provision.get('dependent_questions', [])
                    )
                    
                    # Prepare the input for the chain
                    input_data = {
                        "clause_id": clause['clause_id'],
                        "clause_description": clause['clause_description'] or "N/A",
                        "provision_id": provision['provision_id'],
                        "provision_description": provision['provision_description'],
                        "suggested_artefacts": provision['suggested_artefacts'] or "N/A",
                        "dependent_questions": dependent_questions_formatted
                    }
                    
                    # Generate the evaluation prompt
                    evaluation_prompt = chain.invoke(input_data)
                    
                    # Save the prompt to individual file immediately
                    try:
                        saved_filepath = self.save_prompt_to_file(
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
                        "dependent_questions": provision.get('dependent_questions', []),
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
                        "dependent_questions": provision.get('dependent_questions', []),
                        "evaluation_prompt": f"ERROR: Failed to generate prompt - {str(e)}",
                        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "saved_to": None
                    }
                    results.append(error_result)
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str):
        """Save the generated evaluation prompts to JSON file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(results, file, indent=2, ensure_ascii=False)
            logger.info(f"\n✓ Results saved to: {output_file}")
        except Exception as e:
            logger.error(f"\n✗ Error saving results: {str(e)}")
    
    def create_index_file(self, results: List[Dict[str, Any]], output_dir: str):
        """Create an index.md file listing all generated prompts."""
        index_file = os.path.join(output_dir, "index.md")
        
        try:
            with open(index_file, 'w', encoding='utf-8') as file:
                file.write("# Cyber Essentials Evaluation Prompts Index (Database Version)\n\n")
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
                        filename = self.provision_id_to_snake_case(result['provision_id']) + ".md"
                        file.write(f"- ✅ **{result['provision_id']}** - [{filename}]({filename})\n")
                        
                        # Add dependent questions info
                        if result.get('dependent_questions'):
                            question_count = len(result['dependent_questions'])
                            file.write(f"  - *{question_count} dependent questions*\n")
                
                if failed_results:
                    file.write(f"\n## Failed Generations\n\n")
                    for result in failed_results:
                        file.write(f"- **{result['provision_id']}**: {result['evaluation_prompt']}\n")
            
            logger.info(f"✓ Index file created: {index_file}")
            
        except Exception as e:
            logger.error(f"✗ Error creating index file: {str(e)}")
    
    def run_pipeline(self) -> int:
        """Main pipeline execution method."""
        logger.info("=== Database-Powered Cyber Essentials Evaluation Prompt Generator ===")
        logger.info("This tool generates evaluation prompts for auditors to assess")
        logger.info("organization compliance with Cyber Essentials provisions using database data.\n")
        
        try:
            # Create timestamped output directory
            logger.info("Creating timestamped output directory...")
            output_dir = self.create_timestamped_directory(SAVE_DIR)
            logger.info(f"✓ Output directory created: {output_dir}")
            
            # Load clauses from database
            logger.info("Loading clauses from database...")
            with self.SessionLocal() as session:
                clauses_data = self.load_clauses_from_database(session)
            
            total_provisions = sum(len(clause['provisions']) for clause in clauses_data)
            logger.info(f"Loaded {len(clauses_data)} clauses with {total_provisions} total provisions")
            
            # Create the chain
            logger.info("\nInitializing LangChain components...")
            chain = self.create_prompt_generation_chain()
            logger.info("✓ Chain created successfully")
            
            # Generate evaluation prompts (saves each one immediately)
            logger.info("\nGenerating evaluation prompts...")
            results = self.generate_evaluation_prompts(clauses_data, chain, output_dir)
            
            # Save summary results to JSON file
            logger.info(f"\nSaving summary results...")
            summary_file = os.path.join(output_dir, "generation_summary.json")
            self.save_results(results, summary_file)
            
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
            self.create_index_file(results, output_dir)
            
        except Exception as e:
            logger.error(f"✗ Fatal error: {str(e)}")
            return 1
        
        return 0


def main():
    """Main function to execute the database-powered prompt generation process."""
    pipeline = DatabaseMetaPromptingPipeline()
    return pipeline.run_pipeline()


if __name__ == "__main__":
    exit(main())