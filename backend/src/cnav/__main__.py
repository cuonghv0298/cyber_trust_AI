from dotenv import load_dotenv

load_dotenv()

import json
import os
import re
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
from textwrap import dedent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import init_chat_model


from cnav.output_schemas import ProvisionEvaluation, QuestionResponseEvaluation
from cnav.prompts.main_user_prompt import user_prompt_template
from cnav.database.models import Base
from cnav.database.models.requirement_category import RequirementCategory
from cnav.database.models.clause import Clause
from cnav.database.models.question import Question, AudienceType
from cnav.database.models.organization import Organization
from cnav.database.models.self_assessment_answer import SelfAssessmentAnswer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

# Configuration
SYSTEM_PROMPT_DIR = "/Users/hungquocto/Research/cnav/backend/src/cnav/prompt_generation/output/20250715140048"
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'cnav.db')}"
LLM_MODEL_NAME = "openai:gpt-4.1"
OUTPUT_DIR = "./evaluation_results"
ORGANIZATION_NAME = "Rotary"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ProvisionComplianceEvaluator:
    """Main class for evaluating provision compliance using generated prompts and database data."""
    
    def __init__(self, system_prompt_dir: str, database_url: str):
        self.system_prompt_dir = system_prompt_dir
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Initialize LLM with structured output
        base_llm = init_chat_model(
            model=LLM_MODEL_NAME,
            temperature=0.1,
        )
        self.llm = base_llm.with_structured_output(ProvisionEvaluation)
    
    def load_system_prompt(self, provision_id: str) -> Optional[str]:
        """Load the system prompt for a specific provision from the generated prompt files."""
        try:
            # Convert provision ID to snake_case filename (e.g., "A.1.4a" -> "a_1_4_a.md")
            filename = self._provision_id_to_snake_case(provision_id) + ".md"
            prompt_file_path = os.path.join(self.system_prompt_dir, filename)
            
            if not os.path.exists(prompt_file_path):
                logger.warning(f"System prompt file not found: {prompt_file_path}")
                return None
            
            with open(prompt_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Extract the evaluation prompt section from the markdown file
            # The prompt starts after "## Evaluation Prompt" and continues to the end
            if "## Evaluation Prompt" in content:
                prompt_start = content.find("## Evaluation Prompt") + len("## Evaluation Prompt")
                system_prompt = content[prompt_start:].strip()
                return system_prompt
            else:
                logger.warning(f"No evaluation prompt section found in {prompt_file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading system prompt for {provision_id}: {str(e)}")
            return None
    
    def _provision_id_to_snake_case(self, provision_id: str) -> str:
        """Convert provision ID to snake_case filename."""
        cleaned = re.sub(r'[^\w\s]', '_', provision_id.lower())
        cleaned = re.sub(r'\s+', '_', cleaned)
        cleaned = re.sub(r'_+', '_', cleaned)
        cleaned = cleaned.strip('_')
        return cleaned
    
    def load_provision_data(self, session: Session, clause: Clause) -> Optional[Dict[str, Any]]:
        """Load all dependency data for a specific provision/clause."""
        try:
            # Get the requirement category for this clause
            category = clause.category
            
            # Get all questions associated with this clause
            questions = clause.questions
            
            # For each question, get the organization responses (only for Rotary organization)
            question_responses = []
            for question in questions:
                # Get self-assessment answers for this question from Rotary organization only
                answers = session.query(SelfAssessmentAnswer).join(Organization).filter(
                    SelfAssessmentAnswer.question_id == question.id,
                    Organization.name == ORGANIZATION_NAME
                ).all()
                
                for answer in answers:
                    question_responses.append({
                        'question_id': question.id,
                        'question_text': question.name,
                        'question_audience': question.audience.value,
                        'organization_name': answer.organization.name,
                        'organization_id': answer.organization.id,
                        'response_text': answer.answer,
                        'response_date': answer.created_at.isoformat() if answer.created_at is not None else None
                    })
            
            provision_data = {
                'clause_id': f"A.{clause.full_identifier}",
                'clause_description': category.description,
                'provision_id': f"A.{clause.full_identifier}",
                'provision_description': clause.description,
                'suggested_artefacts': "N/A",  # Not available in current schema
                'question_responses': question_responses,
                'category_name': category.name,
                'clause_name': clause.name
            }
            
            return provision_data
            
        except Exception as e:
            logger.error(f"Error loading provision data for clause {clause.full_identifier}: {str(e)}")
            return None
    
    def format_question_response_pairs(self, question_responses: List[Dict[str, Any]]) -> str:
        """Format question-response pairs for the user prompt template."""
        if not question_responses:
            return "No question responses found for this provision."
        
        formatted_pairs = []
        
        # Group responses by organization
        org_responses = {}
        for response in question_responses:
            org_name = response['organization_name']
            if org_name not in org_responses:
                org_responses[org_name] = []
            org_responses[org_name].append(response)
        
        for org_name, responses in org_responses.items():
            formatted_pairs.append(f"\n### Organization: {org_name}")
            
            for response in responses:
                formatted_pairs.append(dedent(f"""
                    **Question ID**: {response['question_id']}
                    **Audience**: {response['question_audience']}
                    **Question**: {response['question_text']}
                    **Response**: {response['response_text']}
                    **Response Date**: {response['response_date']}
                    ---""")
                    )
        
        return "\n".join(formatted_pairs)
    
    def create_evaluation_chain(self, system_prompt: str):
        """Create the evaluation chain with system prompt, user prompt, and structured output."""
        try:
            # Create the prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template(user_prompt_template)
            ])
            
            # Create the chain with structured output (LLM already has structured output)
            chain = prompt_template | self.llm
            chain.name = "provision_evaluation_chain"
            
            return chain
            
        except Exception as e:
            logger.error(f"Error creating evaluation chain: {str(e)}")
            return None
    
    def evaluate_provision(self, session: Session, clause: Clause) -> Optional[Dict[str, Any]]:
        """Evaluate a single provision/clause for compliance."""
        try:
            provision_id = f"A.{clause.full_identifier}"
            logger.info(f"Evaluating provision: {provision_id}")
            
            # Load system prompt
            system_prompt = self.load_system_prompt(provision_id)
            if not system_prompt:
                logger.error(f"Failed to load system prompt for {provision_id}")
                return None
            
            # Load provision data
            provision_data = self.load_provision_data(session, clause)
            if not provision_data:
                logger.error(f"Failed to load provision data for {provision_id}")
                return None
            
            # Check if there are any question responses
            if not provision_data['question_responses']:
                logger.warning(f"No question responses found for {provision_id}")
                return {
                    'provision_id': provision_id,
                    'clause_id': provision_data['clause_id'],
                    'status': 'NO_RESPONSES',
                    'evaluation': None,
                    'error': 'No question responses found for this provision'
                }
            
            # Format question-response pairs
            question_response_pairs = self.format_question_response_pairs(provision_data['question_responses'])
            
            # Create evaluation chain
            evaluation_chain = self.create_evaluation_chain(system_prompt)
            if not evaluation_chain:
                logger.error(f"Failed to create evaluation chain for {provision_id}")
                return None
            
            # Prepare input for the chain
            chain_input = {
                'clause_id': provision_data['clause_id'],
                'clause_description': provision_data['clause_description'],
                'provision_id': provision_data['provision_id'],
                'provision_description': provision_data['provision_description'],
                'suggested_artefacts': provision_data['suggested_artefacts'],
                'question_response_pairs': question_response_pairs
            }
            
            # Execute evaluation
            logger.info(f"Executing evaluation for {provision_id}...")
            evaluation_result = evaluation_chain.invoke(chain_input)
            
            # Return the result
            result = {
                'provision_id': provision_id,
                'clause_id': provision_data['clause_id'],
                'status': 'SUCCESS',
                'evaluation': evaluation_result,
                'provision_data': provision_data
            }
            
            logger.info(f"✓ Successfully evaluated {provision_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating provision {provision_id}: {str(e)}")
            return {
                'provision_id': provision_id,
                'clause_id': f"A.{clause.full_identifier}",
                'status': 'ERROR',
                'evaluation': None,
                'error': str(e)
            }
    
    def save_evaluation_results(self, results: List[Dict[str, Any]], output_file: str):
        """Save evaluation results to a JSON file."""
        try:
            # Convert ProvisionEvaluation objects to dictionaries for JSON serialization
            serializable_results = []
            for result in results:
                serializable_result = result.copy()
                if result.get('evaluation') and hasattr(result['evaluation'], 'model_dump'):
                    serializable_result['evaluation'] = result['evaluation'].model_dump()
                elif result.get('evaluation') and hasattr(result['evaluation'], 'dict'):
                    serializable_result['evaluation'] = result['evaluation'].dict()
                serializable_results.append(serializable_result)
            
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(serializable_results, file, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Evaluation results saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving evaluation results: {str(e)}")
    
    def run_evaluation(self) -> List[Dict[str, Any]]:
        """Main method to run evaluation for all provisions."""
        logger.info("=== Cyber Essentials Provision Compliance Evaluation ===")
        logger.info(f"Starting evaluation of all provisions for {ORGANIZATION_NAME} organization using database data and generated prompts...\n")
        
        results = []
        
        try:
            with self.SessionLocal() as session:
                # Get all clauses from the database
                clauses = session.query(Clause).join(RequirementCategory).all()
                
                logger.info(f"Found {len(clauses)} clauses to evaluate")
                
                for idx, clause in enumerate(clauses, 1):
                    logger.info(f"\n--- Evaluating clause {idx}/{len(clauses)}: {clause.full_identifier} ---")
                    
                    # Evaluate this provision
                    result = self.evaluate_provision(session, clause)
                    if result:
                        results.append(result)
                    else:
                        logger.error(f"Failed to evaluate clause {clause.full_identifier}")
                
                # Save results
                output_file = os.path.join(OUTPUT_DIR, f"evaluation_results_{len(results)}_provisions.json")
                self.save_evaluation_results(results, output_file)
                
                # Summary
                successful_evaluations = len([r for r in results if r['status'] == 'SUCCESS'])
                failed_evaluations = len([r for r in results if r['status'] == 'ERROR'])
                no_responses = len([r for r in results if r['status'] == 'NO_RESPONSES'])
                
                logger.info(f"\n=== Evaluation Summary ===")
                logger.info(f"Total provisions processed: {len(results)}")
                logger.info(f"Successful evaluations: {successful_evaluations}")
                logger.info(f"Failed evaluations: {failed_evaluations}")
                logger.info(f"No responses found: {no_responses}")
                logger.info(f"Results saved to: {output_file}")
                
                return results
                
        except Exception as e:
            logger.error(f"Fatal error during evaluation: {str(e)}")
            return []


def main():
    """Main function to run the provision compliance evaluation."""
    evaluator = ProvisionComplianceEvaluator(
        system_prompt_dir=SYSTEM_PROMPT_DIR,
        database_url=DATABASE_URL
    )
    
    results = evaluator.run_evaluation()
    
    if results:
        logger.info("✅ Evaluation completed successfully!")
        return 0
    else:
        logger.error("❌ Evaluation failed!")
        return 1


if __name__ == "__main__":
    exit(main())