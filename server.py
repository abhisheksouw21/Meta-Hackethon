from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import subprocess
from environment import ComplianceEnv
from models import Action, ExecuteSQL, ReadFile, WriteFile, SubmitTask

app = FastAPI(title="Compliance Scrubber OpenEnv")
env = ComplianceEnv()

# API Models for requests
class StepRequest(BaseModel):
    action_type: str
    action_data: Dict[str, Any]

class ResetRequest(BaseModel):
    task_level: str = "easy"

@app.get("/")
def health_check():
    """Required by Hugging Face to verify the Space is running."""
    return {"status": "ok"}

@app.post("/reset")
def reset_environment(req: ResetRequest):
    """Resets the environment for a specific task level."""
    obs = env.reset(req.task_level)
    return {"observation": obs.model_dump()}

@app.post("/step")
def step_environment(req: StepRequest):
    """Executes an action in the environment."""
    try:
        # Reconstruct the Pydantic Action object based on the type
        if req.action_type == "ExecuteSQL":
            action = ExecuteSQL(**req.action_data)
        elif req.action_type == "ReadFile":
            action = ReadFile(**req.action_data)
        elif req.action_type == "WriteFile":
            action = WriteFile(**req.action_data)
        elif req.action_type == "SubmitTask":
            action = SubmitTask(**req.action_data)
        else:
            raise ValueError("Unknown action_type")
            
        obs, float_reward, done, info = env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": float_reward,
            "done": done,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
def get_state():
    """Returns the internal state of the environment."""
    return env.state()

@app.get("/tasks")
def get_tasks():
    """Returns the list of tasks and action schema."""
    return {
        "tasks": ["easy", "medium", "hard"],
        "action_schema": "ExecuteSQL(query), ReadFile(filepath), WriteFile(filepath, content), SubmitTask(reasoning)"
    }

@app.post("/grader")
def get_grader_score():
    """Returns the current grader score."""
    # We call our internal grader logic without submitting
    score = env._grade_task()
    return {"score": score}

@app.get("/baseline")
def run_baseline_endpoint():
    """Triggers the baseline script and returns the scores."""
    try:
        # Run the baseline.py script as a separate process
        result = subprocess.run(["python", "baseline.py"], capture_output=True, text=True, check=True)
        return {"status": "success", "logs": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Baseline failed: {e.stderr}")