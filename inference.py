import os
import json
import httpx
import yaml
from openai import OpenAI
import time

# --- Configuration & Setup (Follows Sample strictly) ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3-70B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") # No default allowed here

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

def step(action: str, params: dict, task_id: str):
    response = httpx.post(f"{API_BASE_URL}/step", json={"action": action, "params": params, "task_id": task_id})
    return response.json()

def reset():
    print("[START]") # Pure start tag
    response = httpx.post(f"{API_BASE_URL}/reset")
    return response.json()

def get_state():
    response = httpx.get(f"{API_BASE_URL}/state")
    return response.json()

SYSTEM_PROMPT = "You are a Cloud Ops agent. Output ONLY a JSON object with 'action' and 'params'."

def solve_task(task):
    task_id = task["id"]
    description = task["description"]
    
    max_steps = 5
    for i in range(max_steps):
        state = get_state()
        prompt = f"Goal: {description}\nState: {json.dumps(state)}\nAction:"
        
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            content = completion.choices[0].message.content.strip()
            if "`json" in content: content = content.split("`json")[1].split("`")[0].strip()
            
            decision = json.loads(content)
            print(f"[STEP]") # Pure step tag
            result = step(decision["action"], decision["params"], task_id)
            
            if result.get("done"):
                return 1.0
            time.sleep(1)
        except:
            break
    return 0.0

if __name__ == "__main__":
    reset()
    with open("openenv.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    for task in config["tasks"]:
        solve_task(task)
    
    print("[END]") # Pure end tag