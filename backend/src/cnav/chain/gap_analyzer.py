"""
Gap Analysis Chain
Identifies compliance gaps and provides remediation recommendations for CSA Cyber Essentials
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain.llms.base import LLM
from langchain.schema import BaseOutputParser
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from prompts.gap_analysis import (
    GAP_ANALYSIS_SYSTEM_PROMPT,
    GAP_ANALYSIS_USER_PROMPT,
    QUICK_GAP_ASSESSMENT_PROMPT
)

@dataclass
class RemediationPlan:
    immediate_actions: List[str]
    short_term_actions: List[str]
    long_term_actions: List[str]
    verification_steps: List[str]
    estimated_effort: str
    required_resources: List[str]
    success_criteria: str

@dataclass
class IdentifiedGap:
    provision_id: str
    provision_text: str
    gap_severity: str
    gap_description: str
    risk_impact: str
    current_status: str
    remediation_plan: RemediationPlan
    dependencies: List[str]
    quick_wins: List[str]

@dataclass
class CategoryCoverage:
    covered: int
    total: int
    gaps: List[str]

@dataclass
class RemediationPhase:
    timeline: str
    actions: List[str]
    success_criteria: List[str]

@dataclass
class ResourceRequirements:
    personnel: List[str]
    tools_software: List[str]
    training: List[str]
    external_support: List[str]
    estimated_budget: str

@dataclass
class GapAnalysisResult:
    executive_summary: Dict[str, Any]
    identified_gaps: List[IdentifiedGap]
    coverage_by_category: Dict[str, CategoryCoverage]
    remediation_roadmap: Dict[str, RemediationPhase]
    resource_requirements: ResourceRequirements
    recommendations: List[str]

class GapAnalysisOutputParser(BaseOutputParser[GapAnalysisResult]):
    """Parses LLM output for gap analysis"""
    
    def parse(self, text: str) -> GapAnalysisResult:
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            json_str = text[start_idx:end_idx]
            data = json.loads(json_str)
            
            gap_data = data['gap_analysis']
            
            # Parse identified gaps
            gaps = []
            for gap_data_item in gap_data.get('identified_gaps', []):
                remediation_data = gap_data_item['remediation_plan']
                remediation_plan = RemediationPlan(
                    immediate_actions=remediation_data.get('immediate_actions', []),
                    short_term_actions=remediation_data.get('short_term_actions', []),
                    long_term_actions=remediation_data.get('long_term_actions', []),
                    verification_steps=remediation_data.get('verification_steps', []),
                    estimated_effort=remediation_data.get('estimated_effort', ''),
                    required_resources=remediation_data.get('required_resources', []),
                    success_criteria=remediation_data.get('success_criteria', '')
                )
                
                gap = IdentifiedGap(
                    provision_id=gap_data_item['provision_id'],
                    provision_text=gap_data_item['provision_text'],
                    gap_severity=gap_data_item['gap_severity'],
                    gap_description=gap_data_item['gap_description'],
                    risk_impact=gap_data_item['risk_impact'],
                    current_status=gap_data_item['current_status'],
                    remediation_plan=remediation_plan,
                    dependencies=gap_data_item.get('dependencies', []),
                    quick_wins=gap_data_item.get('quick_wins', [])
                )
                gaps.append(gap)
            
            # Parse coverage by category
            coverage_data = gap_data.get('coverage_by_category', {})
            coverage_by_category = {}
            for category, cov_data in coverage_data.items():
                coverage_by_category[category] = CategoryCoverage(
                    covered=cov_data.get('covered', 0),
                    total=cov_data.get('total', 0),
                    gaps=cov_data.get('gaps', [])
                )
            
            # Parse remediation roadmap
            roadmap_data = gap_data.get('remediation_roadmap', {})
            remediation_roadmap = {}
            for phase, phase_data in roadmap_data.items():
                remediation_roadmap[phase] = RemediationPhase(
                    timeline=phase_data.get('timeline', ''),
                    actions=phase_data.get('actions', []),
                    success_criteria=phase_data.get('success_criteria', [])
                )
            
            # Parse resource requirements
            resource_data = gap_data.get('resource_requirements', {})
            resource_requirements = ResourceRequirements(
                personnel=resource_data.get('personnel', []),
                tools_software=resource_data.get('tools_software', []),
                training=resource_data.get('training', []),
                external_support=resource_data.get('external_support', []),
                estimated_budget=resource_data.get('estimated_budget', '')
            )
            
            return GapAnalysisResult(
                executive_summary=gap_data.get('executive_summary', {}),
                identified_gaps=gaps,
                coverage_by_category=coverage_by_category,
                remediation_roadmap=remediation_roadmap,
                resource_requirements=resource_requirements,
                recommendations=gap_data.get('recommendations', [])
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            # Return a minimal failed result
            return GapAnalysisResult(
                executive_summary={"error": f"Gap analysis parsing failed: {e}"},
                identified_gaps=[],
                coverage_by_category={},
                remediation_roadmap={},
                resource_requirements=ResourceRequirements(
                    personnel=[], tools_software=[], training=[], 
                    external_support=[], estimated_budget=""
                ),
                recommendations=["Retry gap analysis"]
            )

class GapAnalyzer:
    """
    LangChain-based analyzer for identifying compliance gaps and remediation planning
    """
    
    def __init__(self, llm: LLM):
        self.llm = llm
        self.output_parser = GapAnalysisOutputParser()
        
        self.gap_analysis_prompt = PromptTemplate(
            input_variables=[
                "company_name", "industry", "company_size", "technical_maturity",
                "scope", "assessment_status", "all_provisions", "answered_questions",
                "unanswered_questions"
            ],
            template=GAP_ANALYSIS_SYSTEM_PROMPT + "\n\n" + GAP_ANALYSIS_USER_PROMPT
        )
        
        self.gap_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.gap_analysis_prompt,
            output_parser=self.output_parser
        )
    
    def analyze_gaps(
        self,
        company_context: Dict[str, str],
        all_provisions: List[Dict[str, Any]],
        answered_questions: List[Dict[str, Any]],
        unanswered_questions: List[Dict[str, Any]],
        assessment_status: Dict[str, Any]
    ) -> GapAnalysisResult:
        """
        Perform comprehensive gap analysis for an organization
        """
        # Format data for the prompt
        provisions_text = self._format_provisions_for_prompt(all_provisions)
        answered_text = self._format_answered_questions_for_prompt(answered_questions)
        unanswered_text = self._format_unanswered_questions_for_prompt(unanswered_questions)
        status_text = json.dumps(assessment_status, indent=2)
        
        try:
            result = self.gap_analysis_chain.run(
                company_name=company_context.get('name', 'Unknown'),
                industry=company_context.get('industry', 'Unknown'),
                company_size=company_context.get('size', 'Unknown'),
                technical_maturity=company_context.get('technical_maturity', 'Medium'),
                scope=company_context.get('scope', 'Not specified'),
                assessment_status=status_text,
                all_provisions=provisions_text,
                answered_questions=answered_text,
                unanswered_questions=unanswered_text
            )
            return result
            
        except Exception as e:
            return GapAnalysisResult(
                executive_summary={"error": f"Gap analysis failed: {e}"},
                identified_gaps=[],
                coverage_by_category={},
                remediation_roadmap={},
                resource_requirements=ResourceRequirements(
                    personnel=[], tools_software=[], training=[], 
                    external_support=[], estimated_budget=""
                ),
                recommendations=["Retry gap analysis with corrected data"]
            )
    
    def get_quick_assessment(
        self,
        company_name: str,
        assessment_data: Dict[str, Any],
        provisions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Provide a rapid gap assessment for immediate planning
        """
        quick_prompt = PromptTemplate(
            input_variables=["company_name", "assessment_data", "provisions"],
            template=QUICK_GAP_ASSESSMENT_PROMPT
        )
        
        quick_chain = LLMChain(llm=self.llm, prompt=quick_prompt)
        
        try:
            result = quick_chain.run(
                company_name=company_name,
                assessment_data=json.dumps(assessment_data, indent=2),
                provisions=self._format_provisions_for_prompt(provisions)
            )
            
            # Parse the JSON response
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            json_str = result[start_idx:end_idx]
            return json.loads(json_str)
            
        except Exception as e:
            return {
                "quick_gap_assessment": {
                    "certification_blockers": [f"Assessment failed: {e}"],
                    "top_5_priorities": ["Fix assessment system"],
                    "quick_wins": ["Retry assessment"],
                    "estimated_readiness_timeline": "Unknown",
                    "next_steps": ["Contact technical support"],
                    "risk_summary": "Cannot assess risk due to system error"
                }
            }
    
    def _format_provisions_for_prompt(self, provisions: List[Dict[str, Any]]) -> str:
        """Format provisions data for inclusion in prompts"""
        if not provisions:
            return "No provisions data available"
        
        provisions_text = ""
        for provision in provisions:
            provision_id = provision.get('_id', 'Unknown ID')
            provision_text = provision.get('provision', 'No text available')
            provisions_text += f"- {provision_id}: {provision_text}\n"
        
        return provisions_text
    
    def _format_answered_questions_for_prompt(self, questions: List[Dict[str, Any]]) -> str:
        """Format answered questions for inclusion in prompts"""
        if not questions:
            return "No answered questions available"
        
        questions_text = ""
        for question in questions:
            q_id = question.get('_id', 'Unknown ID')
            q_text = question.get('question', 'No question text')
            answer = question.get('answer', 'No answer')
            compliance_status = question.get('compliance_status', 'Unknown')
            
            questions_text += f"Question {q_id}: {q_text}\n"
            questions_text += f"Answer: {answer}\n"
            questions_text += f"Compliance Status: {compliance_status}\n\n"
        
        return questions_text
    
    def _format_unanswered_questions_for_prompt(self, questions: List[Dict[str, Any]]) -> str:
        """Format unanswered questions for inclusion in prompts"""
        if not questions:
            return "All questions have been answered"
        
        questions_text = "Unanswered Questions:\n"
        for question in questions:
            q_id = question.get('_id', 'Unknown ID')
            q_text = question.get('question', 'No question text')
            provisions = question.get('provisions', [])
            
            questions_text += f"- Question {q_id}: {q_text}\n"
            if provisions:
                questions_text += f"  Related Provisions: {', '.join(provisions)}\n"
        
        return questions_text 