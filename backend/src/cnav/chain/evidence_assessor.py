"""
Evidence Assessment Chain
Evaluates quality and sufficiency of evidence files for CSA Cyber Essentials compliance
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain.llms.base import LLM
from langchain.schema import BaseOutputParser
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from prompts.evidence_assessment import (
    EVIDENCE_ASSESSMENT_SYSTEM_PROMPT,
    EVIDENCE_ASSESSMENT_USER_PROMPT,
    BATCH_EVIDENCE_ASSESSMENT_PROMPT
)

@dataclass
class IndividualEvidenceReview:
    filename: str
    evidence_type: str
    quality_rating: str
    relevance: str
    currency: str
    completeness: str
    specific_findings: str
    red_flags: List[str]
    strengths: List[str]

@dataclass
class EvidenceAssessmentResult:
    overall_quality: str
    overall_score: int
    supports_compliance_claim: bool
    assessment_confidence: str
    individual_evidence_reviews: List[IndividualEvidenceReview]
    evidence_gaps: List[str]
    recommendations: List[str]
    additional_evidence_needed: List[str]
    authenticity_concerns: List[str]
    summary: str

class EvidenceAssessmentOutputParser(BaseOutputParser[EvidenceAssessmentResult]):
    """Parses LLM output for evidence assessment"""
    
    def parse(self, text: str) -> EvidenceAssessmentResult:
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            json_str = text[start_idx:end_idx]
            data = json.loads(json_str)
            
            assessment_data = data['evidence_assessment']
            
            # Parse individual evidence reviews
            individual_reviews = []
            for review_data in assessment_data.get('individual_evidence_reviews', []):
                review = IndividualEvidenceReview(
                    filename=review_data['filename'],
                    evidence_type=review_data['evidence_type'],
                    quality_rating=review_data['quality_rating'],
                    relevance=review_data['relevance'],
                    currency=review_data['currency'],
                    completeness=review_data['completeness'],
                    specific_findings=review_data['specific_findings'],
                    red_flags=review_data.get('red_flags', []),
                    strengths=review_data.get('strengths', [])
                )
                individual_reviews.append(review)
            
            return EvidenceAssessmentResult(
                overall_quality=assessment_data['overall_quality'],
                overall_score=assessment_data['overall_score'],
                supports_compliance_claim=assessment_data['supports_compliance_claim'],
                assessment_confidence=assessment_data['assessment_confidence'],
                individual_evidence_reviews=individual_reviews,
                evidence_gaps=assessment_data.get('evidence_gaps', []),
                recommendations=assessment_data.get('recommendations', []),
                additional_evidence_needed=assessment_data.get('additional_evidence_needed', []),
                authenticity_concerns=assessment_data.get('authenticity_concerns', []),
                summary=assessment_data.get('summary', '')
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            return EvidenceAssessmentResult(
                overall_quality="inadequate",
                overall_score=0,
                supports_compliance_claim=False,
                assessment_confidence="low",
                individual_evidence_reviews=[],
                evidence_gaps=["Assessment parsing failed"],
                recommendations=["Retry evidence assessment"],
                additional_evidence_needed=["All evidence needs review"],
                authenticity_concerns=[f"Assessment error: {e}"],
                summary="Evidence assessment failed due to parsing error"
            )

class EvidenceAssessor:
    """
    LangChain-based assessor for evaluating evidence quality and sufficiency
    """
    
    def __init__(self, llm: LLM):
        self.llm = llm
        self.output_parser = EvidenceAssessmentOutputParser()
        
        self.assessment_prompt = PromptTemplate(
            input_variables=[
                "provision_id", "provision_text", "question", "answer", 
                "company_name", "evidence_files", "evidence_description", 
                "answered_by", "scope"
            ],
            template=EVIDENCE_ASSESSMENT_SYSTEM_PROMPT + "\n\n" + EVIDENCE_ASSESSMENT_USER_PROMPT
        )
        
        self.assessment_chain = LLMChain(
            llm=self.llm,
            prompt=self.assessment_prompt,
            output_parser=self.output_parser
        )
    
    def assess_evidence(
        self,
        provision_id: str,
        provision_text: str,
        question: str,
        answer: str,
        company_context: Dict[str, str],
        evidence_files: List[Dict[str, Any]],
        evidence_description: str = "",
        answered_by: str = ""
    ) -> EvidenceAssessmentResult:
        """
        Assess evidence for a specific compliance claim
        """
        evidence_text = self._format_evidence_for_prompt(evidence_files)
        
        try:
            result = self.assessment_chain.run(
                provision_id=provision_id,
                provision_text=provision_text,
                question=question,
                answer=answer,
                company_name=company_context.get('name', 'Unknown'),
                evidence_files=evidence_text,
                evidence_description=evidence_description,
                answered_by=answered_by,
                scope=company_context.get('scope', 'Not specified')
            )
            return result
            
        except Exception as e:
            return EvidenceAssessmentResult(
                overall_quality="inadequate",
                overall_score=0,
                supports_compliance_claim=False,
                assessment_confidence="low",
                individual_evidence_reviews=[],
                evidence_gaps=["Assessment failed"],
                recommendations=["Retry assessment"],
                additional_evidence_needed=["All evidence needs review"],
                authenticity_concerns=[f"System error: {e}"],
                summary="Evidence assessment failed due to system error"
            )
    
    def _format_evidence_for_prompt(self, evidence_files: List[Dict[str, Any]]) -> str:
        """Format evidence files for inclusion in prompts"""
        if not evidence_files:
            return "No evidence files provided"
        
        evidence_text = ""
        for i, evidence in enumerate(evidence_files, 1):
            filename = evidence.get('filename', f'File_{i}')
            file_type = evidence.get('file_type', 'Unknown')
            description = evidence.get('description', 'No description')
            uploaded_at = evidence.get('uploaded_at', 'Unknown date')
            
            evidence_text += f"{i}. {filename} ({file_type})\n"
            evidence_text += f"   Description: {description}\n"
            evidence_text += f"   Uploaded: {uploaded_at}\n\n"
        
        return evidence_text 