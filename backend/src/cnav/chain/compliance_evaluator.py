"""
Compliance Evaluation Chain
Evaluates organization answers against CSA Cyber Essentials provisions for compliance assessment
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain.llms.base import LLM
from langchain.schema import BaseOutputParser
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from prompts.compliance_evaluation import (
    COMPLIANCE_EVALUATION_SYSTEM_PROMPT,
    COMPLIANCE_EVALUATION_USER_PROMPT,
    BATCH_COMPLIANCE_EVALUATION_PROMPT
)

@dataclass
class EvidenceAssessment:
    evidence_provided: bool
    evidence_quality: str  # "excellent", "good", "fair", "poor", "none"
    evidence_gaps: List[str]
    evidence_notes: str

@dataclass
class ImplementationAssessment:
    fully_implemented: bool
    implementation_notes: str
    scope_coverage: str  # "complete", "partial", "unclear"
    effectiveness: str  # "high", "medium", "low", "unknown"

@dataclass
class ComplianceEvaluation:
    compliance_status: str  # "COMPLIANT", "PARTIAL", "NON_COMPLIANT", "INSUFFICIENT_INFO"
    confidence_level: str  # "high", "medium", "low"
    score: int  # 0-100
    rationale: str
    evidence_assessment: EvidenceAssessment
    implementation_assessment: ImplementationAssessment
    recommendations: List[str]
    critical_issues: List[str]
    next_steps: List[str]

@dataclass
class ProvisionEvaluationResult:
    question_id: str
    provision_id: str
    evaluation: ComplianceEvaluation

@dataclass
class OverallAssessment:
    total_provisions_evaluated: int
    compliant_count: int
    partial_count: int
    non_compliant_count: int
    shall_provisions_compliant: int
    shall_provisions_total: int
    certification_recommendation: str  # "PASS", "FAIL", "CONDITIONAL"
    overall_score: int
    critical_gaps: List[str]
    priority_recommendations: List[str]
    strengths: List[str]

class ComplianceEvaluationOutputParser(BaseOutputParser[ProvisionEvaluationResult]):
    """Parses LLM output for compliance evaluation"""
    
    def parse(self, text: str) -> ProvisionEvaluationResult:
        try:
            # Extract JSON from the LLM response
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            json_str = text[start_idx:end_idx]
            data = json.loads(json_str)
            
            eval_data = data['evaluation']
            
            # Parse evidence assessment
            evidence_data = eval_data['evidence_assessment']
            evidence_assessment = EvidenceAssessment(
                evidence_provided=evidence_data['evidence_provided'],
                evidence_quality=evidence_data['evidence_quality'],
                evidence_gaps=evidence_data.get('evidence_gaps', []),
                evidence_notes=evidence_data.get('evidence_notes', '')
            )
            
            # Parse implementation assessment
            impl_data = eval_data['implementation_assessment']
            implementation_assessment = ImplementationAssessment(
                fully_implemented=impl_data['fully_implemented'],
                implementation_notes=impl_data.get('implementation_notes', ''),
                scope_coverage=impl_data.get('scope_coverage', 'unclear'),
                effectiveness=impl_data.get('effectiveness', 'unknown')
            )
            
            # Create compliance evaluation
            evaluation = ComplianceEvaluation(
                compliance_status=eval_data['compliance_status'],
                confidence_level=eval_data['confidence_level'],
                score=eval_data['score'],
                rationale=eval_data['rationale'],
                evidence_assessment=evidence_assessment,
                implementation_assessment=implementation_assessment,
                recommendations=eval_data.get('recommendations', []),
                critical_issues=eval_data.get('critical_issues', []),
                next_steps=eval_data.get('next_steps', [])
            )
            
            return ProvisionEvaluationResult(
                question_id=data.get('question_id', ''),
                provision_id=data.get('provision_id', ''),
                evaluation=evaluation
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            # Return a default failed evaluation
            return ProvisionEvaluationResult(
                question_id='',
                provision_id='',
                evaluation=ComplianceEvaluation(
                    compliance_status="INSUFFICIENT_INFO",
                    confidence_level="low",
                    score=0,
                    rationale=f"Evaluation parsing failed: {e}",
                    evidence_assessment=EvidenceAssessment(
                        evidence_provided=False,
                        evidence_quality="none",
                        evidence_gaps=["Evaluation failed"],
                        evidence_notes="Could not parse evaluation response"
                    ),
                    implementation_assessment=ImplementationAssessment(
                        fully_implemented=False,
                        implementation_notes="Evaluation failed",
                        scope_coverage="unclear",
                        effectiveness="unknown"
                    ),
                    recommendations=["Re-evaluate with clear evidence"],
                    critical_issues=["Evaluation system error"],
                    next_steps=["Retry evaluation"]
                )
            )

class ComplianceEvaluator:
    """
    LangChain-based evaluator for assessing compliance against CSA provisions
    """
    
    def __init__(self, llm: LLM):
        self.llm = llm
        self.output_parser = ComplianceEvaluationOutputParser()
        
        # Create the evaluation prompt template
        self.evaluation_prompt = PromptTemplate(
            input_variables=[
                "question", "answer", "evidence_files", "answered_by", 
                "confidence_level", "provision_id", "provision_text", 
                "requirement_type", "company_name", "industry", "scope_description"
            ],
            template=COMPLIANCE_EVALUATION_SYSTEM_PROMPT + "\n\n" + COMPLIANCE_EVALUATION_USER_PROMPT
        )
        
        # Create the LangChain chain
        self.evaluation_chain = LLMChain(
            llm=self.llm,
            prompt=self.evaluation_prompt,
            output_parser=self.output_parser
        )
    
    def evaluate_single_response(
        self,
        question: str,
        answer: str,
        provision_id: str,
        provision_text: str,
        requirement_type: str,  # "shall" or "should"
        company_context: Dict[str, str],
        evidence_files: Optional[List[Dict[str, Any]]] = None,
        answered_by: str = "",
        confidence_level: str = "medium"
    ) -> ProvisionEvaluationResult:
        """
        Evaluate a single organization response against a specific provision
        """
        # Format evidence files for the prompt
        evidence_text = self._format_evidence_for_prompt(evidence_files or [])
        
        try:
            result = self.evaluation_chain.run(
                question=question,
                answer=answer,
                evidence_files=evidence_text,
                answered_by=answered_by,
                confidence_level=confidence_level,
                provision_id=provision_id,
                provision_text=provision_text,
                requirement_type=requirement_type,
                company_name=company_context.get('name', 'Unknown'),
                industry=company_context.get('industry', 'Unknown'),
                scope_description=company_context.get('scope', 'Not specified')
            )
            
            # Ensure we have the question_id and provision_id in the result
            result.question_id = company_context.get('question_id', '')
            result.provision_id = provision_id
            
            return result
            
        except Exception as e:
            # Return a default failed evaluation
            return ProvisionEvaluationResult(
                question_id=company_context.get('question_id', ''),
                provision_id=provision_id,
                evaluation=ComplianceEvaluation(
                    compliance_status="INSUFFICIENT_INFO",
                    confidence_level="low",
                    score=0,
                    rationale=f"Evaluation failed: {str(e)}",
                    evidence_assessment=EvidenceAssessment(
                        evidence_provided=False,
                        evidence_quality="none",
                        evidence_gaps=["Evaluation error"],
                        evidence_notes="System error during evaluation"
                    ),
                    implementation_assessment=ImplementationAssessment(
                        fully_implemented=False,
                        implementation_notes="Could not evaluate",
                        scope_coverage="unclear",
                        effectiveness="unknown"
                    ),
                    recommendations=["Retry evaluation"],
                    critical_issues=["System evaluation error"],
                    next_steps=["Contact technical support"]
                )
            )
    
    def evaluate_multiple_responses(
        self,
        responses_data: List[Dict[str, Any]],
        company_context: Dict[str, str]
    ) -> List[ProvisionEvaluationResult]:
        """
        Evaluate multiple responses for a comprehensive assessment
        """
        results = []
        
        for response_data in responses_data:
            question = response_data.get('question', '')
            answer = response_data.get('answer', '')
            provision_id = response_data.get('provision_id', '')
            provision_text = response_data.get('provision_text', '')
            requirement_type = response_data.get('requirement_type', 'should')
            evidence_files = response_data.get('evidence_files', [])
            answered_by = response_data.get('answered_by', '')
            confidence_level = response_data.get('confidence_level', 'medium')
            question_id = response_data.get('question_id', '')
            
            # Add question_id to company context
            context_with_question = {**company_context, 'question_id': question_id}
            
            if question and answer and provision_id:
                result = self.evaluate_single_response(
                    question=question,
                    answer=answer,
                    provision_id=provision_id,
                    provision_text=provision_text,
                    requirement_type=requirement_type,
                    company_context=context_with_question,
                    evidence_files=evidence_files,
                    answered_by=answered_by,
                    confidence_level=confidence_level
                )
                results.append(result)
        
        return results
    
    def generate_overall_assessment(
        self, 
        evaluation_results: List[ProvisionEvaluationResult]
    ) -> OverallAssessment:
        """
        Generate an overall assessment based on individual evaluations
        """
        total_provisions = len(evaluation_results)
        compliant_count = len([r for r in evaluation_results if r.evaluation.compliance_status == "COMPLIANT"])
        partial_count = len([r for r in evaluation_results if r.evaluation.compliance_status == "PARTIAL"])
        non_compliant_count = len([r for r in evaluation_results if r.evaluation.compliance_status == "NON_COMPLIANT"])
        
        # Count shall provisions (these are critical for certification)
        shall_provisions_total = len([r for r in evaluation_results if "shall" in r.provision_id.lower()])
        shall_provisions_compliant = len([
            r for r in evaluation_results 
            if "shall" in r.provision_id.lower() and r.evaluation.compliance_status == "COMPLIANT"
        ])
        
        # Calculate overall score
        total_score = sum(r.evaluation.score for r in evaluation_results)
        overall_score = total_score // total_provisions if total_provisions > 0 else 0
        
        # Determine certification recommendation
        if shall_provisions_compliant == shall_provisions_total and overall_score >= 80:
            certification_recommendation = "PASS"
        elif shall_provisions_compliant == shall_provisions_total and overall_score >= 60:
            certification_recommendation = "CONDITIONAL"
        else:
            certification_recommendation = "FAIL"
        
        # Collect critical gaps and recommendations
        critical_gaps = []
        priority_recommendations = []
        strengths = []
        
        for result in evaluation_results:
            critical_gaps.extend(result.evaluation.critical_issues)
            priority_recommendations.extend(result.evaluation.recommendations)
            
            if result.evaluation.compliance_status == "COMPLIANT" and result.evaluation.score >= 90:
                strengths.append(f"{result.provision_id}: Excellent compliance")
        
        return OverallAssessment(
            total_provisions_evaluated=total_provisions,
            compliant_count=compliant_count,
            partial_count=partial_count,
            non_compliant_count=non_compliant_count,
            shall_provisions_compliant=shall_provisions_compliant,
            shall_provisions_total=shall_provisions_total,
            certification_recommendation=certification_recommendation,
            overall_score=overall_score,
            critical_gaps=list(set(critical_gaps)),
            priority_recommendations=list(set(priority_recommendations)),
            strengths=strengths
        )
    
    def _format_evidence_for_prompt(self, evidence_files: List[Dict[str, Any]]) -> str:
        """Format evidence files for inclusion in prompts"""
        if not evidence_files:
            return "No evidence files provided"
        
        evidence_text = "Evidence Files:\n"
        for evidence in evidence_files:
            filename = evidence.get('filename', 'Unknown file')
            file_type = evidence.get('file_type', 'Unknown type')
            description = evidence.get('description', 'No description')
            evidence_text += f"- {filename} ({file_type}): {description}\n"
        
        return evidence_text 