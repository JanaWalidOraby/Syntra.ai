from pydantic import BaseModel
from typing import List, Dict

class ProjectEvaluationRequest(BaseModel):
    projectLink: str
    trackId: str
    studentId: str

class FeedbackContent(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    suggestions: str

class RequirementStatus(BaseModel):
    feature: str
    status: bool

class ProjectEvaluationResponse(BaseModel):
    score: int
    status: str
    feedback: FeedbackContent
    requirements_met: List[RequirementStatus]