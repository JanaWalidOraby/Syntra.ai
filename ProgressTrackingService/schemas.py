from pydantic import BaseModel, Field
from typing import List, Dict

class WeightRequest(BaseModel):
    track_name: str = Field(..., example="Artificial Intelligence")
    roadmap_courses: List[str] = Field(
        ..., 
        example=["Linear Algebra", "Machine Learning Basics", "Deep Learning", "Computer Vision"]
    )


class WeightResponse(BaseModel):
    track_name: str
    all_courses_weights: Dict[str, float] = Field(..., description="Full roadmap courses with their calculated weights")