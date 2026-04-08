import os
import json
import httpx
import yaml
from openai import OpenAI
import time
from dotenv import load_dotenv

# --- Configuration & Setup ---
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
HF_TOKEN = os.getenv("HF_TOKEN", "") 
MODEL_NAME = "meta-llama/Meta-Llama-3-70B-Instruct"

print(f"--- Debug: Using Base URL: {API_BASE_URL} ---")
print(f"--- Debug: Token length: {len(HF_TOKEN)} chars ---")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

def step(action: str, params: dict, task_id: str):
    try:
        response = httpx.post(f"{API_BASE_URL}/step", json={"action": action, "params": params, "task_id": task_id}, timeout=10.0)
        return response.json()
    except Exception as e:
        print(f"[STEP] Error connecting to Server: {e}")
        return {}

def reset():
    print("[START] Initializing environment...")
    try:
        response = httpx.post(f"{API_BASE_URL}/reset", timeout=10.0)
        return response.json()
    except Exception as e:
        print(f"[ERROR] Could not connect to Server at {API_BASE_URL}. Is Terminal 1 running?")
        exit(1)

def get_state():
    response = httpx.get(f"{API_BASE_URL}/state")
    return response.json()

SYSTEM_PROMPT = """You are an expert Cloud Operations AI agent.
Your goal is to complete infrastructure tasks using the provided API.
Available Actions:
- create_instance(name, type, region)
- create_bucket(name)
- upload_file(bucket, name, content)
- list_instances()
- get_status()

IMPORTANT: YOU MUST ONLY OUTPUT A VALID JSON OBJECT.
Example: {"action": "create_instance", "params": {"name": "test", "type": "t3.micro", "region": "us-east-1"}}
"""

def solve_task(task):
    task_id = task["id"]
    description = task["description"]
    print(f"[STEP] Starting Task: {task['name']}")
    
    max_steps = 5
    for i in range(max_steps):
        state = get_state()
        prompt = f"Goal: {description}\nCurrent Resources: {json.dumps(state['resources'])}\nChoose the next action."
        
        try:
            print(f"[STEP] Thinking... (Step {i+1})")
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Clean up the response (Llama sometimes adds markdown blocks)
            content = completion.choices[0].message.content.strip()
            if "`json" in content:
                content = content.split("`json")[1].split("`")[0].strip()
            
            decision = json.loads(content)
            action = decision["action"]
            params = decision["params"]
            
            print(f"[STEP] Action: {action} | Params: {params}")
            result = step(action, params, task_id)
            
            if result.get("done"):
                print(f"[STEP] Task {task_id} completed successfully!")
                return 1.0
            time.sleep(2) 
        except Exception as e:
            print(f"[STEP] Agent error or rate limit: {e}")
            time.sleep(5) # Wait longer if there's an error
            break
    return 0.0

if __name__ == "__main__":
    if not HF_TOKEN or len(HF_TOKEN) < 10:
        print("ERROR: HF_TOKEN not found or invalid in .env file.")
        exit(1)
        
    reset()
    with open("openenv.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    total_score = 0
    for task in config["tasks"]:
        score = solve_task(task)
        total_score += score
    
    print(f"[END] Final average score: {total_score / len(config['tasks'])}")
