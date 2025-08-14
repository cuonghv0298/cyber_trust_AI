"""
Report Generation Chain
Generates comprehensive CSA Cyber Essentials compliance reports for different audiences
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from prompts.report_generation import (
    REPORT_GENERATION_SYSTEM_PROMPT,
    EXECUTIVE_REPORT_PROMPT,
    TECHNICAL_REPORT_PROMPT,
    AUDIT_REPORT_PROMPT
)

@dataclass
class ReportContext:
    company_name: str
    industry: str
    scope: str
    assessment_date: str
    assessor_name: str
    report_date: str
    report_version: str = "1.0"

class ReportGenerator:
    """
    LangChain-based generator for creating professional compliance reports
    """
    
    def __init__(self, llm: LLM):
        self.llm = llm
        
        # Executive Report Chain
        self.executive_prompt = PromptTemplate(
            input_variables=[
                "company_name", "industry", "scope", "assessment_date",
                "assessor_name", "assessment_results", "gap_analysis",
                "evidence_assessment", "report_date"
            ],
            template=REPORT_GENERATION_SYSTEM_PROMPT + "\n\n" + EXECUTIVE_REPORT_PROMPT
        )
        self.executive_chain = LLMChain(llm=self.llm, prompt=self.executive_prompt)
        
        # Technical Report Chain
        self.technical_prompt = PromptTemplate(
            input_variables=[
                "assessment_data", "technical_findings", "evidence_details",
                "assessor_name", "assessment_date", "review_date"
            ],
            template=REPORT_GENERATION_SYSTEM_PROMPT + "\n\n" + TECHNICAL_REPORT_PROMPT
        )
        self.technical_chain = LLMChain(llm=self.llm, prompt=self.technical_prompt)
        
        # Audit Report Chain
        self.audit_prompt = PromptTemplate(
            input_variables=[
                "complete_assessment", "evidence_inventory", "compliance_determinations",
                "report_id", "assessment_date", "report_date", "assessor_name",
                "assessor_credentials", "company_name", "industry", "organization_size",
                "certification_scope", "detailed_provision_assessment", "evidence_registry",
                "certification_body"
            ],
            template=REPORT_GENERATION_SYSTEM_PROMPT + "\n\n" + AUDIT_REPORT_PROMPT
        )
        self.audit_chain = LLMChain(llm=self.llm, prompt=self.audit_prompt)
    
    def generate_executive_report(
        self,
        report_context: ReportContext,
        assessment_results: Dict[str, Any],
        gap_analysis: Dict[str, Any],
        evidence_assessment: Dict[str, Any]
    ) -> str:
        """
        Generate an executive-level compliance report
        """
        try:
            report = self.executive_chain.run(
                company_name=report_context.company_name,
                industry=report_context.industry,
                scope=report_context.scope,
                assessment_date=report_context.assessment_date,
                assessor_name=report_context.assessor_name,
                report_date=report_context.report_date,
                assessment_results=self._format_assessment_results(assessment_results),
                gap_analysis=self._format_gap_analysis(gap_analysis),
                evidence_assessment=self._format_evidence_assessment(evidence_assessment)
            )
            return report
            
        except Exception as e:
            return self._generate_error_report("executive", str(e), report_context)
    
    def generate_technical_report(
        self,
        report_context: ReportContext,
        assessment_data: Dict[str, Any],
        technical_findings: Dict[str, Any],
        evidence_details: Dict[str, Any]
    ) -> str:
        """
        Generate a detailed technical report for IT teams
        """
        try:
            report = self.technical_chain.run(
                assessment_data=self._format_assessment_data(assessment_data),
                technical_findings=self._format_technical_findings(technical_findings),
                evidence_details=self._format_evidence_details(evidence_details),
                assessor_name=report_context.assessor_name,
                assessment_date=report_context.assessment_date,
                review_date=report_context.report_date
            )
            return report
            
        except Exception as e:
            return self._generate_error_report("technical", str(e), report_context)
    
    def generate_audit_report(
        self,
        report_context: ReportContext,
        complete_assessment: Dict[str, Any],
        evidence_inventory: Dict[str, Any],
        compliance_determinations: Dict[str, Any],
        report_id: str,
        assessor_credentials: str,
        organization_size: str,
        certification_body: str
    ) -> str:
        """
        Generate a formal audit report for certification body review
        """
        try:
            report = self.audit_chain.run(
                complete_assessment=self._format_complete_assessment(complete_assessment),
                evidence_inventory=self._format_evidence_inventory(evidence_inventory),
                compliance_determinations=self._format_compliance_determinations(compliance_determinations),
                report_id=report_id,
                assessment_date=report_context.assessment_date,
                report_date=report_context.report_date,
                assessor_name=report_context.assessor_name,
                assessor_credentials=assessor_credentials,
                company_name=report_context.company_name,
                industry=report_context.industry,
                organization_size=organization_size,
                certification_scope=report_context.scope,
                detailed_provision_assessment=self._format_detailed_provision_assessment(complete_assessment),
                evidence_registry=self._format_evidence_registry(evidence_inventory),
                certification_body=certification_body
            )
            return report
            
        except Exception as e:
            return self._generate_error_report("audit", str(e), report_context)
    
    def generate_all_reports(
        self,
        report_context: ReportContext,
        comprehensive_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate all three types of reports from comprehensive assessment data
        """
        # Extract relevant data for each report type
        assessment_results = comprehensive_data.get('assessment_results', {})
        gap_analysis = comprehensive_data.get('gap_analysis', {})
        evidence_assessment = comprehensive_data.get('evidence_assessment', {})
        technical_findings = comprehensive_data.get('technical_findings', {})
        evidence_details = comprehensive_data.get('evidence_details', {})
        compliance_determinations = comprehensive_data.get('compliance_determinations', {})
        
        # Generate all reports
        reports = {
            'executive': self.generate_executive_report(
                report_context, assessment_results, gap_analysis, evidence_assessment
            ),
            'technical': self.generate_technical_report(
                report_context, comprehensive_data, technical_findings, evidence_details
            ),
            'audit': self.generate_audit_report(
                report_context, 
                comprehensive_data,
                evidence_assessment,
                compliance_determinations,
                f"AUDIT-{report_context.company_name}-{report_context.assessment_date}",
                "CSA Certified Auditor",
                comprehensive_data.get('organization_size', 'Medium'),
                "CSA Cyber Essentials Certification Body"
            )
        }
        
        return reports
    
    def _format_assessment_results(self, results: Dict[str, Any]) -> str:
        """Format assessment results for executive report"""
        if not results:
            return "No assessment results available"
        
        formatted = "Assessment Results Summary:\n"
        formatted += f"- Total Provisions: {results.get('total_provisions', 'Unknown')}\n"
        formatted += f"- Compliant: {results.get('compliant_count', 'Unknown')}\n"
        formatted += f"- Partial Compliance: {results.get('partial_count', 'Unknown')}\n"
        formatted += f"- Non-Compliant: {results.get('non_compliant_count', 'Unknown')}\n"
        formatted += f"- Overall Score: {results.get('overall_score', 'Unknown')}%\n"
        formatted += f"- Certification Recommendation: {results.get('certification_recommendation', 'Unknown')}\n"
        
        return formatted
    
    def _format_gap_analysis(self, gap_analysis: Dict[str, Any]) -> str:
        """Format gap analysis for executive report"""
        if not gap_analysis:
            return "No gap analysis available"
        
        formatted = "Gap Analysis Summary:\n"
        executive_summary = gap_analysis.get('executive_summary', {})
        formatted += f"- Critical Gaps: {executive_summary.get('critical', 0)}\n"
        formatted += f"- High Priority Gaps: {executive_summary.get('high', 0)}\n"
        formatted += f"- Medium Priority Gaps: {executive_summary.get('medium', 0)}\n"
        formatted += f"- Certification Readiness: {executive_summary.get('certification_readiness', 'Unknown')}\n"
        formatted += f"- Estimated Remediation Time: {executive_summary.get('estimated_remediation_time', 'Unknown')}\n"
        
        return formatted
    
    def _format_evidence_assessment(self, evidence: Dict[str, Any]) -> str:
        """Format evidence assessment for executive report"""
        if not evidence:
            return "No evidence assessment available"
        
        formatted = "Evidence Assessment Summary:\n"
        formatted += f"- Overall Evidence Quality: {evidence.get('overall_evidence_quality', 'Unknown')}\n"
        formatted += f"- Evidence Maturity: {evidence.get('organization_evidence_maturity', 'Unknown')}\n"
        formatted += f"- Audit Readiness: {evidence.get('audit_readiness', {}).get('ready_for_audit', 'Unknown')}\n"
        
        return formatted
    
    def _format_assessment_data(self, data: Dict[str, Any]) -> str:
        """Format comprehensive assessment data for technical report"""
        return f"Assessment conducted on {data.get('assessment_date', 'Unknown date')}\n" + \
               f"Scope: {data.get('scope', 'Not specified')}\n" + \
               f"Total Questions: {len(data.get('questions', []))}\n" + \
               f"Total Provisions: {len(data.get('provisions', []))}"
    
    def _format_technical_findings(self, findings: Dict[str, Any]) -> str:
        """Format technical findings for technical report"""
        if not findings:
            return "No technical findings available"
        
        return "Technical compliance findings and recommendations based on assessment results."
    
    def _format_evidence_details(self, details: Dict[str, Any]) -> str:
        """Format evidence details for technical report"""
        if not details:
            return "No evidence details available"
        
        return "Detailed analysis of evidence quality and recommendations for improvement."
    
    def _format_complete_assessment(self, assessment: Dict[str, Any]) -> str:
        """Format complete assessment for audit report"""
        return f"Complete assessment data including {len(assessment.get('questions', []))} questions " + \
               f"and {len(assessment.get('provisions', []))} provisions evaluated."
    
    def _format_evidence_inventory(self, inventory: Dict[str, Any]) -> str:
        """Format evidence inventory for audit report"""
        return f"Evidence inventory containing assessment of {inventory.get('total_evidence_files', 0)} files."
    
    def _format_compliance_determinations(self, determinations: Dict[str, Any]) -> str:
        """Format compliance determinations for audit report"""
        return f"Compliance determinations for {determinations.get('total_provisions_evaluated', 0)} provisions."
    
    def _format_detailed_provision_assessment(self, assessment: Dict[str, Any]) -> str:
        """Format detailed provision assessment for audit report"""
        return "Detailed provision-by-provision compliance assessment results."
    
    def _format_evidence_registry(self, registry: Dict[str, Any]) -> str:
        """Format evidence registry for audit report"""
        return "Comprehensive registry of all evidence reviewed during assessment."
    
    def _generate_error_report(self, report_type: str, error: str, context: ReportContext) -> str:
        """Generate a basic error report when report generation fails"""
        return f"""# CSA Cyber Essentials Assessment Report - {report_type.title()}

## Report Generation Error

**Company**: {context.company_name}
**Assessment Date**: {context.assessment_date}
**Report Date**: {context.report_date}

**Error**: Report generation failed due to: {error}

Please contact technical support for assistance with report generation.

---
*Report generated by CSA Cyber Essentials Automation System*
""" 