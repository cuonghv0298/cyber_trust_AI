user_prompt_template = """
## Clause Information
**Clause ID**: {clause_id}
**Clause Description**: {clause_description}

## Provision Details
**Provision ID**: {provision_id}
**Provision Requirement**: {provision_description}
**Suggested Artifacts**: {suggested_artefacts}

## Dependent Questions & Responses from Organization
**Questions and Responses**: 
{question_response_pairs}
"""