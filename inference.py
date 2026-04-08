import os
import json
import httpx
from openai import OpenAI
import time

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3-70B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") # NO DEFAULT

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

def call_env(ep: str, method: str = "GET", payload: dict = None):
    url = f"{API_BASE_URL.rstrip('/')}/{ep}"
    if method == "POST":
        resp = httpx.post(url, json=payload, timeout=30)
    else:
        resp = httpx.get(url, timeout=30)
    return resp.json()

TASKS = [
    {"id": "task_1", "name": "Basic Provisioning", "description": "Create a 't3.micro' instance named 'web-server' in the 'us-east-1' region."},
    {"id": "task_2", "name": "Storage Setup", "description": "Create a secure storage bucket named 'company-reports' and upload a file 'policy.txt' with the content 'confidential-data'."},
    {"id": "task_3", "name": "Full Stack Infrastructure", "description": "Deploy a production-ready environment: create an 'm5.large' instance named 'db-prod' and a bucket 'db-backups'."}
]

def solve_task(task):
    print("[STEP]")
    max_steps = 5
    for _ in range(max_steps):
        state = call_env("state")
        prompt = f"Goal: {task['description']}\nState: {json.dumps(state)}\nAction:"
        try:
            comp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "system", "content": "You are a Cloud Ops agent. Output ONLY a JSON object with 'action' and 'params'."}, {"role": "user", "content": prompt}]
            )
            content = comp.choices[0].message.content.strip()
            if "`json" in content: content = content.split("`json")[1].split("`")[0].strip()
            decision = json.loads(content)
            result = call_env("step", "POST", {"action": decision["action"], "params": decision["params"], "task_id": task["id"]})
            if result.get("done"): return 1.0
            time.sleep(1)
        except: break
    return 0.0

if __name__ == "__main__":
    print("[START]")
    call_env("reset", "POST")
    for task in TASKS: solve_task(task)
    print("[END]")