import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from env.environment import CloudOpsEngine
import logging

logging.basicConfig(level=logging.INFO, format='[STEP] %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = CloudOpsEngine()

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
async def reset(request: Request):
    print("[START]")
    try:
        body = await request.body()
    except Exception:
        pass
    
    engine.reset()
    obs = engine.get_state()
    return JSONResponse(content=obs)

@app.post("/step")
async def step(request: Request):
    try:
        body = await request.json()
        action = body.get("action")
        params = body.get("params", {})
        task_id = body.get("task_id", "")
    except Exception:
        return JSONResponse(status_code=400, content={"detail": "Invalid JSON"})
    
    result = engine.step(action, params)
    
    reward_val = engine.calculate_reward(task_id) if task_id else 0.0
    done = (reward_val == 1.0)
    
    return JSONResponse(content={
        "observation": engine.get_state(),
        "reward": {"value": reward_val},
        "done": done,
        "info": {"message": result.get("message", "")}
    })

@app.get("/state")
def state():
    return JSONResponse(content=engine.get_state())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)