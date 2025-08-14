"""
Prompts for Report Generation Chain
Generates comprehensive CSA Cyber Essentials compliance reports
"""

REPORT_GENERATION_SYSTEM_PROMPT = """
You are a cybersecurity consultant specializing in creating professional CSA Cyber Essentials compliance reports. Your role is to synthesize assessment data into comprehensive, audit-ready reports suitable for certification bodies, executives, and technical teams.

## Report Standards & Requirements:
1. **Professional Quality**: Clear, well-structured, executive-appropriate presentation
2. **Audit Readiness**: Sufficient detail for certification body review
3. **Actionable Insights**: Specific recommendations with implementation guidance
4. **Evidence-Based**: All findings supported by verifiable evidence
5. **Risk-Focused**: Clear linkage between gaps and business/security risks
6. **Compliance Mapping**: Explicit mapping to CSA provisions and requirements

## Report Structure Framework:
- **Executive Summary**: High-level findings, recommendations, certification readiness
- **Assessment Overview**: Scope, methodology, participants, timeline
- **Compliance Analysis**: Detailed provision-by-provision assessment
- **Gap Analysis**: Identified gaps with remediation plans
- **Risk Assessment**: Security and business risks from non-compliance
- **Recommendations**: Prioritized action plan for certification
- **Appendices**: Evidence inventory, detailed findings, reference materials

## Audience Considerations:
- **Executives**: Focus on business impact, risk, timelines, budget
- **IT Teams**: Technical details, implementation steps, tools needed
- **Auditors**: Evidence references, provision mapping, compliance status
- **Compliance Teams**: Gap tracking, remediation progress, deadlines

## Professional Standards:
- Use formal business language and tone
- Include specific dates, references, and version numbers
- Provide clear pass/fail determinations where applicable
- Ensure traceability from findings to evidence
- Include confidence levels and assessment limitations
"""

EXECUTIVE_REPORT_PROMPT = """
Generate an executive-level CSA Cyber Essentials compliance report based on the assessment data:

**Organization Information**:
Company: {company_name}
Industry: {industry}
Assessment Scope: {scope}
Assessment Date: {assessment_date}
Assessor: {assessor_name}

**Assessment Results**:
{assessment_results}

**Gap Analysis**:
{gap_analysis}

**Evidence Assessment**:
{evidence_assessment}

Generate a professional executive report in the following structure:
```markdown
# CSA Cyber Essentials Compliance Assessment Report

## Executive Summary

### Assessment Overview
- **Organization**: {company_name}
- **Assessment Date**: {assessment_date}
- **Certification Scope**: {scope}
- **Assessment Status**: [READY FOR CERTIFICATION / REQUIRES REMEDIATION / SIGNIFICANT GAPS]

### Key Findings
- **Overall Compliance Score**: X% (X/Y provisions compliant)
- **Critical Gaps**: X items requiring immediate attention
- **Certification Readiness**: [Timeline and key milestones]
- **Risk Level**: [HIGH/MEDIUM/LOW with justification]

### Certification Recommendation
[PASS/CONDITIONAL PASS/FAIL with detailed justification]

## Compliance Summary by Category

| Category | Provisions | Compliant | Partial | Non-Compliant | Score |
|----------|------------|-----------|---------|---------------|-------|
| A.1 People | X | X | X | X | X% |
| A.2 Hardware/Software | X | X | X | X | X% |
| A.3 Data | X | X | X | X | X% |
| A.4 Malware Protection | X | X | X | X | X% |
| A.5 Access Control | X | X | X | X | X% |
| A.6 Secure Configuration | X | X | X | X | X% |
| A.7 Software Updates | X | X | X | X | X% |
| A.8 Backup | X | X | X | X | X% |
| A.9 Incident Response | X | X | X | X | X% |

## Critical Issues Requiring Immediate Attention

[List of critical gaps that block certification]

## Business Risk Assessment

### High-Risk Areas
[Security and business risks from identified gaps]

### Risk Mitigation Priorities
[Prioritized actions to reduce risk]

## Remediation Roadmap

### Phase 1: Critical Issues (X weeks)
[Immediate actions required for certification eligibility]

### Phase 2: High Priority (X weeks)  
[Important improvements for strong security posture]

### Phase 3: Enhancements (X weeks)
[Best practice implementations and continuous improvement]

## Resource Requirements

### Personnel
[Roles and time commitments needed]

### Budget Estimate
[Overall cost estimate for gap remediation]

### Timeline
[Realistic timeline to certification readiness]

## Recommendations

### Strategic Recommendations
[High-level strategic guidance]

### Next Steps
[Immediate actions for the organization]

---

**Report Prepared By**: {assessor_name}
**Report Date**: {report_date}
**Report Version**: 1.0
```

Ensure the report is professional, actionable, and provides clear guidance for achieving certification.
"""

TECHNICAL_REPORT_PROMPT = """
Generate a detailed technical CSA Cyber Essentials compliance report for IT teams:

**Assessment Data**: {assessment_data}
**Technical Findings**: {technical_findings}
**Evidence Details**: {evidence_details}

Generate a comprehensive technical report:
```markdown
# CSA Cyber Essentials Technical Assessment Report

## Assessment Methodology

### Scope and Approach
[Detailed description of assessment methodology]

### Evidence Evaluation Process
[How evidence was assessed and validated]

## Detailed Findings by Provision

{provision_findings}

## Technical Gap Analysis

### Missing Controls
[Detailed list of missing technical controls]

### Configuration Issues
[Specific configuration problems identified]

### Policy and Procedure Gaps
[Documentation and process deficiencies]

## Evidence Assessment Summary

### Evidence Quality by Category
[Assessment of evidence quality across different areas]

### Missing Evidence
[Comprehensive list of missing evidence items]

### Evidence Recommendations
[Specific guidance for improving evidence quality]

## Implementation Guidance

### Technical Recommendations
[Detailed technical implementation steps]

### Tool and Solution Recommendations
[Specific tools and products recommended]

### Configuration Templates
[Where applicable, provide configuration examples]

## Verification and Testing

### Verification Steps for Each Gap
[How to verify that gaps have been closed]

### Testing Recommendations
[Recommended testing approaches]

---

**Assessment Conducted By**: {assessor_name}
**Assessment Date**: {assessment_date}
**Technical Review Date**: {review_date}
```

Focus on providing detailed technical guidance that IT teams can immediately act upon.
"""

AUDIT_REPORT_PROMPT = """
Generate an audit-ready CSA Cyber Essentials compliance report suitable for certification body review:

**Complete Assessment Data**: {complete_assessment}
**Evidence Inventory**: {evidence_inventory}
**Compliance Determinations**: {compliance_determinations}

Generate a formal audit report:
```markdown
# CSA Cyber Essentials Certification Assessment Report

## Report Information
- **Report ID**: {report_id}
- **Assessment Date**: {assessment_date}
- **Report Date**: {report_date}
- **Assessor**: {assessor_name}
- **Assessor Credentials**: {assessor_credentials}

## Organization Information
- **Organization Name**: {company_name}
- **Industry Sector**: {industry}
- **Organization Size**: {organization_size}
- **Certification Scope**: {certification_scope}

## Assessment Summary
- **Total Provisions Assessed**: X
- **Compliant Provisions**: X
- **Partially Compliant Provisions**: X  
- **Non-Compliant Provisions**: X
- **Overall Compliance Score**: X%

## Provision-by-Provision Assessment

{detailed_provision_assessment}

## Evidence Registry

{evidence_registry}

## Non-Conformities and Observations

### Critical Non-Conformities
[Issues that prevent certification]

### Major Non-Conformities  
[Significant issues requiring remediation]

### Minor Non-Conformities
[Areas for improvement]

### Observations
[Best practice recommendations]

## Certification Recommendation

### Assessor Determination
[RECOMMEND CERTIFICATION / RECOMMEND CONDITIONAL CERTIFICATION / DO NOT RECOMMEND CERTIFICATION]

### Justification
[Detailed rationale for recommendation]

### Conditions (if applicable)
[Specific conditions that must be met for certification]

## Appendices

### Appendix A: Assessment Checklist
[Complete assessment checklist with findings]

### Appendix B: Evidence Inventory
[Detailed inventory of all evidence reviewed]

### Appendix C: Interview Records
[Summary of interviews conducted]

---

**Assessor Signature**: ________________
**Date**: ________________
**Certification Body**: {certification_body}
```

Ensure the report meets all formal audit requirements and provides complete traceability.
""" 