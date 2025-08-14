"""
Prompts for Gap Analysis Chain
Identifies missing provisions and provides remediation recommendations
"""

GAP_ANALYSIS_SYSTEM_PROMPT = """
You are a cybersecurity consultant specializing in CSA Cyber Essentials certification gap analysis. Your role is to identify compliance gaps, assess their impact, and provide actionable remediation plans for organizations seeking certification.

## Gap Analysis Framework:
1. **Provision Coverage Analysis**: Identify all CSA provisions not adequately addressed
2. **Risk Impact Assessment**: Evaluate security and compliance risks of each gap
3. **Remediation Planning**: Provide specific, actionable steps to close gaps
4. **Priority Classification**: Categorize gaps by urgency and certification impact
5. **Resource Estimation**: Estimate time, cost, and effort required for remediation

## CSA Cyber Essentials Requirements Structure:
- **A.1 Assets: People** - Training, awareness, human-first defense
- **A.2 Assets: Hardware/Software** - Inventory, lifecycle management
- **A.3 Assets: Data** - Classification, protection, disposal
- **A.4 Virus/Malware Protection** - Endpoint security, threat detection
- **A.5 Access Control** - Identity management, authentication, authorization
- **A.6 Secure Configuration** - Hardening, secure defaults
- **A.7 Software Updates** - Patch management, vulnerability management
- **A.8 Backup** - Data protection, business continuity
- **A.9 Incident Response** - Detection, response, recovery

## Gap Severity Levels:
- **CRITICAL**: "Shall" provision completely missing - blocks certification
- **HIGH**: "Shall" provision partially implemented - significant remediation needed
- **MEDIUM**: "Should" provision missing or "shall" provision with minor gaps
- **LOW**: Enhancement opportunities, best practices not implemented

## Remediation Planning Principles:
- Provide specific, implementable actions
- Consider organization size, resources, and technical maturity
- Prioritize quick wins alongside long-term strategic improvements
- Include verification steps to confirm gap closure
- Address interdependencies between provisions
"""

GAP_ANALYSIS_USER_PROMPT = """
Perform comprehensive gap analysis for the following organization's CSA Cyber Essentials assessment:

**Organization Profile**:
Company: {company_name}
Industry: {industry}
Size: {company_size}
Technical Maturity: {technical_maturity}
Certification Scope: {scope}

**Current Assessment Status**:
{assessment_status}

**All CSA Provisions (Reference)**:
{all_provisions}

**Answered Questions with Compliance Status**:
{answered_questions}

**Unanswered Questions**:
{unanswered_questions}

Please provide comprehensive gap analysis in the following JSON format:
```json
{{
  "gap_analysis": {{
    "executive_summary": {{
      "total_provisions": X,
      "addressed_provisions": X,
      "gap_count_by_severity": {{
        "critical": X,
        "high": X,
        "medium": X,
        "low": X
      }},
      "certification_readiness": "ready|needs_work|significant_gaps",
      "estimated_remediation_time": "X weeks/months"
    }},
    "identified_gaps": [
      {{
        "provision_id": "A.X.Y(z)",
        "provision_text": "Full provision text",
        "gap_severity": "critical|high|medium|low",
        "gap_description": "Specific description of what's missing or inadequate",
        "risk_impact": "High-level risk if gap remains unaddressed",
        "current_status": "not_addressed|partially_addressed|inadequately_addressed",
        "remediation_plan": {{
          "immediate_actions": ["Specific actions to take within 1-2 weeks"],
          "short_term_actions": ["Actions to complete within 1-3 months"],
          "long_term_actions": ["Strategic improvements for 3+ months"],
          "verification_steps": ["How to verify gap has been closed"],
          "estimated_effort": "X hours/days/weeks",
          "required_resources": ["Personnel, tools, budget needed"],
          "success_criteria": "Measurable criteria for gap closure"
        }},
        "dependencies": ["Other provisions or gaps that must be addressed first"],
        "quick_wins": ["Easy improvements that can be made immediately"]
      }}
    ],
    "coverage_by_category": {{
      "A1_People": {{"covered": X, "total": X, "gaps": ["provision_ids"]}},
      "A2_Hardware_Software": {{"covered": X, "total": X, "gaps": ["provision_ids"]}},
      "A3_Data": {{"covered": X, "total": X, "gaps": ["provision_ids"]}},
      "A4_Malware": {{"covered": X, "total": X, "gaps": ["provision_ids"]}},
      "A5_Access_Control": {{"covered": X, "total": X, "gaps": ["provision_ids"]}},
      "A6_Secure_Config": {{"covered": X, "total": X, "gaps": ["provision_ids"]}},
      "A7_Updates": {{"covered": X, "total": X, "gaps": ["provision_ids"]}},
      "A8_Backup": {{"covered": X, "total": X, "gaps": ["provision_ids"]}},
      "A9_Incident_Response": {{"covered": X, "total": X, "gaps": ["provision_ids"]}}
    }},
    "remediation_roadmap": {{
      "phase_1_critical": {{
        "timeline": "X weeks",
        "actions": ["Most critical gaps to address first"],
        "success_criteria": ["Phase 1 completion criteria"]
      }},
      "phase_2_high": {{
        "timeline": "X weeks",
        "actions": ["High priority gaps"],
        "success_criteria": ["Phase 2 completion criteria"]
      }},
      "phase_3_enhancement": {{
        "timeline": "X weeks",
        "actions": ["Medium/low priority improvements"],
        "success_criteria": ["Final certification readiness criteria"]
      }}
    }},
    "resource_requirements": {{
      "personnel": ["Roles and time commitments needed"],
      "tools_software": ["Required tools or software purchases"],
      "training": ["Training needs identified"],
      "external_support": ["Areas where external consulting may be beneficial"],
      "estimated_budget": "Overall budget estimate for gap remediation"
    }},
    "recommendations": [
      "Strategic recommendations for successful certification"
    ]
  }}
}}
```

Focus on providing actionable, realistic remediation plans appropriate for the organization's context.
"""

QUICK_GAP_ASSESSMENT_PROMPT = """
Provide a rapid gap assessment for immediate planning purposes:

**Organization**: {company_name}
**Assessment Data**: {assessment_data}
**CSA Provisions**: {provisions}

Provide a focused gap analysis:
```json
{{
  "quick_gap_assessment": {{
    "certification_blockers": [
      "Critical gaps that prevent certification"
    ],
    "top_5_priorities": [
      "Most important gaps to address immediately"
    ],
    "quick_wins": [
      "Easy improvements that can be made this week"
    ],
    "estimated_readiness_timeline": "X weeks/months until certification ready",
    "next_steps": [
      "Immediate next steps for the organization"
    ],
    "risk_summary": "Overall risk level and key concerns"
  }}
}}
```

Focus on immediate actionability and clear priorities.
""" 