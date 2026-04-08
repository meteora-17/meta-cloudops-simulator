import os
import json
import httpx
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
    print("[START]")
    response = httpx.post(f"{API_BASE_URL}/reset")
    return response.json()

def get_state():
    response = httpx.get(f"{API_BASE_URL}/state")
    return response.json()

SYSTEM_PROMPT = "You are a Cloud Ops agent. Output ONLY a JSON object with 'action' and 'params'."

TASKS = [
    {
        "id": "task_1",
        "name": "Basic Provisioning",
        "description": "Create a 't3.micro' instance named 'web-server' in the 'us-east-1' region."
    },
    {
        "id": "task_2",
        "name": "Storage Setup",
        "description": "Create a secure storage bucket named 'company-reports' and upload a file 'policy.txt' with the content 'confidential-data'."
    },
    {
        "id": "task_3",
        "name": "Full Stack Infrastructure",
        "description": "Deploy a production-ready environment: create an 'm5.large' instance named 'db-prod' and a bucket 'db-backups'."
    }
]

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
            print(f"[STEP]")
            result = step(decision["action"], decision["params"], task_id)
            
            if result.get("done"):
                return 1.0
            time.sleep(1)
        except:
            break
    return 0.0

if __name__ == "__main__":
    reset()
    for task in TASKS:
        solve_task(task)
    print("[END]")