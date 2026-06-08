from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import WeightRequest, WeightResponse
from .core_logic import calculate_roadmap_weights

app = FastAPI(
    title="Syntra.AI - Progress & Weight Tracking Service",
    description="Microservice responsible for calculating relative roadmap course weights using LLM & Custom ML Models.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/calculate-weights", response_model=WeightResponse, tags=["Weight Prediction"])
async def predict_roadmap_weights(payload: WeightRequest):
    """
    Endpoint used by the backend when a roadmap is created or assigned to a student.
    It returns the calculated weights for all courses in the roadmap.
    """
    if not payload.roadmap_courses:
        raise HTTPException(status_code=400, detail="Roadmap courses list cannot be empty.")
        

    calculated_weights = calculate_roadmap_weights(
        track_name=payload.track_name, 
        roadmap_courses=payload.roadmap_courses
    )
    

    return WeightResponse(
        track_name=payload.track_name,
        all_courses_weights=calculated_weights
    )

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Syntra.AI Weight Prediction Service is Live!"}