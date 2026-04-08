from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
from env.environment import CloudOpsEngine
import logging

# Configure structured logging
logging.basicConfig(level=logging.INFO, format='[STEP] %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "Meta PyTorch Hackathon: CloudOps Simulator is RUNNING!",
        "endpoints": {
            "reset": "/reset (POST)",
            "step": "/step (POST)",
            "state": "/state (GET)",
            "health": "/health (GET)"
        }
    }

engine = CloudOpsEngine()

class ActionRequest(BaseModel):
    action: str
    params: Optional[Dict[str, Any]] = {}
    task_id: Optional[str] = None

@app.post("/reset")
async def reset(request: Request):
    # Log reset and handle any incoming JSON body (e.g., difficulty)
    print("[START] Environment resetting...")
    engine.reset()
    # Return the full initial state, as expected by the OpenEnv grader
    return engine.get_state()

@app.post("/step")
async def step(req: ActionRequest):
    logger.info(f"Executing action: {req.action} with params: {req.params}")
    result = engine.step(req.action, req.params)

    # Calculate reward if task_id is provided
    reward = 0.0
    if req.task_id:
        reward = engine.calculate_reward(req.task_id)
        result["reward"] = reward
        result["done"] = (reward == 1.0)

    return result

@app.get("/state")
async def get_state():
    return engine.get_state()

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # Important: Hugging Face uses port 7860
    uvicorn.run(app, host="0.0.0.0", port=7860)
