from typing import List
from pydantic import BaseModel, Field

class QuestionResponseEvaluation(BaseModel):
    question_id: str = Field(..., description="The ID of the question being evaluated")
    question_compliance_rationale: str = Field(..., description="The rationale for the evaluation result")
    question_compliance_result: bool = Field(..., description="Whether the question response is compliant with the provision, True of passed, False of failed")
    question_compliance_confidence_score: float = Field(..., description="How confident you are in the question compliance evaluation result, between 0 and 1")

class ProvisionEvaluation(BaseModel):
    question_response_evaluations: List[QuestionResponseEvaluation] = Field(..., description="A list of question response evaluations")
    provision_compliance_rationale: str = Field(..., description="The rationale for the provision compliance result")
    provision_compliance_result: bool = Field(..., description="Whether the provision is compliant with the clause, True of passed, False of failed")
    provision_compliance_confidence_score: float = Field(..., description="How confident you are in the provision compliance evaluation result, between 0 and 1")