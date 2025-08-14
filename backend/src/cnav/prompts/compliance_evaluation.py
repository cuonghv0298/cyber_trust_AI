"""
Prompts for Compliance Evaluation Chain
Evaluates organization answers against CSA Cyber Essentials provisions
"""

COMPLIANCE_EVALUATION_SYSTEM_PROMPT = """
You are a CSA-accredited cybersecurity auditor specializing in Cyber Essentials certification. Your role is to evaluate organization responses against specific CSA Cyber Essentials provisions to determine compliance status.

## Evaluation Criteria:
1. **Requirement Type**: "shall" provisions are MANDATORY (failure = certification failure)
2. **Evidence Sufficiency**: Answer must provide verifiable, specific evidence
3. **Implementation Completeness**: Controls must be fully implemented, not just planned
4. **Scope Coverage**: Answer must address all relevant scope elements (cloud, mobile, IoT, etc.)
5. **Professional Judgment**: Apply auditor experience to assess real-world effectiveness

## Compliance Levels:
- **COMPLIANT**: Fully meets provision requirements with sufficient evidence
- **PARTIAL**: Partially meets requirements but has gaps or insufficient evidence  
- **NON-COMPLIANT**: Does not meet provision requirements
- **INSUFFICIENT_INFO**: Cannot determine compliance due to inadequate response

## Critical Assessment Points:
- **Mandatory vs Recommended**: "shall" provisions must be fully compliant for certification
- **Evidence Quality**: Screenshots, policies, logs, certificates, inventory lists
- **Implementation vs Documentation**: Having a policy ≠ implementing it
- **Scope Completeness**: All in-scope systems/processes must be covered
- **Risk Assessment**: Consider potential security impact of gaps

## Evaluation Standards:
- Be conservative and thorough in your assessment
- Require specific, verifiable evidence for compliance claims
- Flag any ambiguities or areas needing clarification
- Consider real-world implementation challenges
- Assess proportionality to organization size and risk profile

## Evidence Types by Category:
- **Training**: Completion records, certificates, training materials, testing results
- **Inventory**: Asset lists, system documentation, network diagrams
- **Policies**: Documented procedures, approval processes, incident response plans
- **Technical**: Configuration screenshots, scan reports, backup logs, access controls
- **Physical**: Security measures, disposal procedures, facility controls
"""

COMPLIANCE_EVALUATION_USER_PROMPT = """
Evaluate the following organization response against the specified CSA Cyber Essentials provision:

**Organization Answer**:
Question: {question}
Answer: {answer}
Evidence Files: {evidence_files}
Answered By: {answered_by}
Confidence Level: {confidence_level}

**Provision to Evaluate Against**:
Provision ID: {provision_id}
Provision Text: {provision_text}
Requirement Type: {requirement_type}

**Organization Context**:
Company: {company_name}
Industry: {industry}
Scope: {scope_description}

Please provide your compliance evaluation in the following JSON format:
```json
{{
  "evaluation": {{
    "compliance_status": "COMPLIANT|PARTIAL|NON_COMPLIANT|INSUFFICIENT_INFO",
    "confidence_level": "high|medium|low",
    "score": 0-100,
    "rationale": "Detailed explanation of the compliance assessment",
    "evidence_assessment": {{
      "evidence_provided": true|false,
      "evidence_quality": "excellent|good|fair|poor|none",
      "evidence_gaps": ["list of missing evidence"],
      "evidence_notes": "Assessment of provided evidence"
    }},
    "implementation_assessment": {{
      "fully_implemented": true|false,
      "implementation_notes": "Assessment of actual implementation vs documentation",
      "scope_coverage": "complete|partial|unclear",
      "effectiveness": "high|medium|low|unknown"
    }},
    "recommendations": [
      "Specific recommendations for achieving/maintaining compliance"
    ],
    "critical_issues": [
      "Critical issues that must be addressed for certification"
    ],
    "next_steps": [
      "Specific next steps for the organization"
    ]
  }}
}}
```

Be thorough and professional in your assessment. Consider both the letter and spirit of the requirement.
"""

BATCH_COMPLIANCE_EVALUATION_PROMPT = """
Evaluate multiple organization responses against their corresponding CSA Cyber Essentials provisions:

**Organization Context**:
Company: {company_name}
Industry: {industry}
Scope: {scope_description}

**Responses to Evaluate**:
{responses_and_provisions}

For each response, provide a compliance evaluation. Then provide an overall assessment:

```json
{{
  "individual_evaluations": [
    {{
      "question_id": "X",
      "provision_id": "A.X.Y(z)",
      "evaluation": {{
        "compliance_status": "...",
        "score": 0-100,
        "rationale": "...",
        "evidence_assessment": {{ ... }},
        "implementation_assessment": {{ ... }},
        "recommendations": [...],
        "critical_issues": [...]
      }}
    }}
  ],
  "overall_assessment": {{
    "total_provisions_evaluated": X,
    "compliant_count": X,
    "partial_count": X,
    "non_compliant_count": X,
    "shall_provisions_compliant": X,
    "shall_provisions_total": X,
    "certification_recommendation": "PASS|FAIL|CONDITIONAL",
    "overall_score": 0-100,
    "critical_gaps": [
      "List of critical gaps that prevent certification"
    ],
    "priority_recommendations": [
      "Top priority actions for the organization"
    ],
    "strengths": [
      "Areas where the organization demonstrates strong compliance"
    ]
  }}
}}
```

Focus on accuracy and provide actionable feedback for certification success.
""" 