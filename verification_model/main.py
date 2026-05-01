from fastapi import FastAPI, BackgroundTasks
from schemas import ProjectEvaluationRequest, ProjectEvaluationResponse
from core_logic import start_evaluation_process
import os

app = FastAPI()

results_db = {}

@app.post("/evaluate")
async def evaluate_project(request: ProjectEvaluationRequest, background_tasks: BackgroundTasks):
    student_id = request.studentId
    results_db[student_id] = {"status": "Processing"}
    background_tasks.add_task(start_evaluation_process, request, results_db)
    return {"message": "Evaluation started", "studentId": student_id}

@app.get("/results/{student_id}")
async def get_results(student_id: str):
    result = results_db.get(student_id)
    if not result:
        return {"error": "No evaluation found for this student ID"}
    return result