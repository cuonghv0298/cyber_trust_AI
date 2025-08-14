"""
Assessment Orchestrator
Coordinates all LangChain chains for comprehensive CSA Cyber Essentials automation
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from langchain.llms.base import LLM

from .question_provision_mapper import QuestionProvisionMapper
from .compliance_evaluator import ComplianceEvaluator
from .evidence_assessor import EvidenceAssessor
from .gap_analyzer import GapAnalyzer
from .report_generator import ReportGenerator, ReportContext

@dataclass
class OrganizationContext:
    name: str
    industry: str
    size: str
    scope: str
    technical_maturity: str = "medium"
    assessor_name: str = "Automated Assessment System"

@dataclass
class AssessmentConfiguration:
    include_question_mapping: bool = True
    include_compliance_evaluation: bool = True
    include_evidence_assessment: bool = True
    include_gap_analysis: bool = True
    include_report_generation: bool = True
    report_types: Optional[List[str]] = None  # ["executive", "technical", "audit"]

@dataclass
class AssessmentResult:
    organization: OrganizationContext
    assessment_date: datetime
    overall_score: int
    certification_recommendation: str
    question_mappings: List[Any]
    compliance_evaluations: List[Any]
    gap_analysis: Any
    reports: Dict[str, str]
    processing_notes: List[str]

class AssessmentOrchestrator:
    """
    Master orchestrator for the entire CSA Cyber Essentials assessment process
    """
    
    def __init__(self, llm: LLM):
        self.llm = llm
        self.question_mapper = None
        self.compliance_evaluator = ComplianceEvaluator(llm)
        self.evidence_assessor = EvidenceAssessor(llm)
        self.gap_analyzer = GapAnalyzer(llm)
        self.report_generator = ReportGenerator(llm)
        self.processing_notes = []
    
    def initialize_question_mapper(self, provisions_data: List[Dict[str, Any]]):
        """Initialize the question mapper with provisions data"""
        self.question_mapper = QuestionProvisionMapper(provisions_data)
    
    def run_complete_assessment(
        self,
        organization_context: OrganizationContext,
        questions_data: List[Dict[str, Any]],
        answers_data: List[Dict[str, Any]],
        provisions_data: List[Dict[str, Any]]
    ) -> AssessmentResult:
        """Run the complete assessment workflow"""
        
        assessment_date = datetime.now()
        self.processing_notes = []
        
        # Initialize question mapper
        if self.question_mapper is None:
            self.initialize_question_mapper(provisions_data)
        
        # Step 1: Map questions to provisions
        self.processing_notes.append("Mapping questions to provisions...")
        question_mappings = []
        if self.question_mapper:
            question_mappings = self.question_mapper.map_multiple_questions(questions_data)
        
        # Step 2: Evaluate compliance
        self.processing_notes.append("Evaluating compliance...")
        compliance_evaluations = self._evaluate_compliance(
            answers_data, provisions_data, organization_context
        )
        
        # Step 3: Perform gap analysis
        self.processing_notes.append("Performing gap analysis...")
        gap_analysis = self._perform_gap_analysis(
            organization_context, provisions_data, answers_data
        )
        
        # Step 4: Generate reports
        self.processing_notes.append("Generating reports...")
        reports = self._generate_reports(
            organization_context, assessment_date, compliance_evaluations, gap_analysis
        )
        
        # Calculate overall results
        overall_score, certification_recommendation = self._calculate_overall_results(
            compliance_evaluations
        )
        
        return AssessmentResult(
            organization=organization_context,
            assessment_date=assessment_date,
            overall_score=overall_score,
            certification_recommendation=certification_recommendation,
            question_mappings=question_mappings,
            compliance_evaluations=compliance_evaluations,
            gap_analysis=gap_analysis,
            reports=reports,
            processing_notes=self.processing_notes
        )
    
    def run_quick_assessment(
        self,
        organization_context: OrganizationContext,
        answers_data: List[Dict[str, Any]],
        provisions_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run a quick assessment for immediate feedback"""
        
        answered_count = len([a for a in answers_data if a.get('answer')])
        total_count = len(answers_data)
        
        assessment_data = {
            'answered_count': answered_count,
            'total_questions': total_count,
            'completion_rate': answered_count / total_count if total_count > 0 else 0
        }
        
        return self.gap_analyzer.get_quick_assessment(
            organization_context.name, assessment_data, provisions_data
        )
    
    def _evaluate_compliance(
        self,
        answers_data: List[Dict[str, Any]],
        provisions_data: List[Dict[str, Any]],
        organization_context: OrganizationContext
    ) -> List[Any]:
        """Evaluate compliance for answered questions"""
        
        responses_for_evaluation = []
        
        for answer in answers_data:
            if answer.get('answer'):
                # Get related provisions
                provision_ids = answer.get('provisions', [])
                for provision_id in provision_ids:
                    provision_data = next(
                        (p for p in provisions_data if p.get('_id') == provision_id), 
                        None
                    )
                    
                    if provision_data:
                        responses_for_evaluation.append({
                            'question': answer.get('question', ''),
                            'answer': answer.get('answer', ''),
                            'provision_id': provision_id,
                            'provision_text': provision_data.get('provision', ''),
                            'requirement_type': provision_data.get('requirement_type', 'should'),
                            'evidence_files': answer.get('evidence_files', []),
                            'question_id': answer.get('_id', '')
                        })
        
        company_context = {
            'name': organization_context.name,
            'industry': organization_context.industry,
            'scope': organization_context.scope
        }
        
        return self.compliance_evaluator.evaluate_multiple_responses(
            responses_for_evaluation, company_context
        )
    
    def _perform_gap_analysis(
        self,
        organization_context: OrganizationContext,
        provisions_data: List[Dict[str, Any]],
        answers_data: List[Dict[str, Any]]
    ) -> Any:
        """Perform gap analysis"""
        
        company_context = {
            'name': organization_context.name,
            'industry': organization_context.industry,
            'size': organization_context.size,
            'technical_maturity': organization_context.technical_maturity,
            'scope': organization_context.scope
        }
        
        answered_questions = [a for a in answers_data if a.get('answer')]
        unanswered_questions = [a for a in answers_data if not a.get('answer')]
        
        assessment_status = {
            'total_questions': len(answers_data),
            'answered_questions': len(answered_questions),
            'completion_rate': len(answered_questions) / len(answers_data) if answers_data else 0
        }
        
        return self.gap_analyzer.analyze_gaps(
            company_context, provisions_data, answered_questions, 
            unanswered_questions, assessment_status
        )
    
    def _generate_reports(
        self,
        organization_context: OrganizationContext,
        assessment_date: datetime,
        compliance_evaluations: List[Any],
        gap_analysis: Any
    ) -> Dict[str, str]:
        """Generate comprehensive reports"""
        
        report_context = ReportContext(
            company_name=organization_context.name,
            industry=organization_context.industry,
            scope=organization_context.scope,
            assessment_date=assessment_date.strftime("%Y-%m-%d"),
            assessor_name=organization_context.assessor_name,
            report_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Format results for reports
        assessment_results = self._format_assessment_results(compliance_evaluations)
        gap_results = gap_analysis.__dict__ if gap_analysis else {}
        evidence_results = {'overall_evidence_quality': 'good'}
        
        # Generate reports
        reports = {}
        
        try:
            reports['executive'] = self.report_generator.generate_executive_report(
                report_context, assessment_results, gap_results, evidence_results
            )
        except Exception as e:
            reports['executive'] = f"Executive report generation failed: {e}"
        
        try:
            reports['technical'] = self.report_generator.generate_technical_report(
                report_context, assessment_results, {}, {}
            )
        except Exception as e:
            reports['technical'] = f"Technical report generation failed: {e}"
        
        return reports
    
    def _calculate_overall_results(self, compliance_evaluations: List[Any]) -> tuple:
        """Calculate overall score and certification recommendation"""
        
        if not compliance_evaluations:
            return 0, "INSUFFICIENT_DATA"
        
        # Calculate average score
        total_score = sum(eval_result.evaluation.score for eval_result in compliance_evaluations)
        overall_score = total_score // len(compliance_evaluations)
        
        # Determine recommendation
        compliant_count = len([e for e in compliance_evaluations 
                              if e.evaluation.compliance_status == "COMPLIANT"])
        compliance_rate = compliant_count / len(compliance_evaluations)
        
        if overall_score >= 80 and compliance_rate >= 0.9:
            recommendation = "PASS"
        elif overall_score >= 60 and compliance_rate >= 0.7:
            recommendation = "CONDITIONAL"
        else:
            recommendation = "FAIL"
        
        return overall_score, recommendation
    
    def _format_assessment_results(self, evaluations: List[Any]) -> Dict[str, Any]:
        """Format compliance evaluation results for reports"""
        
        if not evaluations:
            return {'total_provisions': 0}
        
        compliant = len([e for e in evaluations if e.evaluation.compliance_status == "COMPLIANT"])
        partial = len([e for e in evaluations if e.evaluation.compliance_status == "PARTIAL"])
        non_compliant = len([e for e in evaluations if e.evaluation.compliance_status == "NON_COMPLIANT"])
        
        return {
            'total_provisions': len(evaluations),
            'compliant_count': compliant,
            'partial_count': partial,
            'non_compliant_count': non_compliant,
            'overall_score': sum(e.evaluation.score for e in evaluations) // len(evaluations),
            'certification_recommendation': self._calculate_overall_results(evaluations)[1]
        } 