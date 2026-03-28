import os
import json
import urllib.request
from openai import OpenAI

# Ensure the API key is present
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable not set.")
    exit(1)

client = OpenAI()
BASE_URL = "http://127.0.0.1:7860" # Local port for FastAPI

def send_post(endpoint, data=None):
    """Helper function to send POST requests using the standard library."""
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    req = urllib.request.Request(url, headers=headers, method='POST')
    
    if data is not None:
        req.data = json.dumps(data).encode('utf-8')
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Request failed: {e}")
        return {}

def run_dummy_agent(task_level):
    print(f"\n--- Running Baseline for {task_level.upper()} Task ---")
    
    # 1. Reset Environment
    send_post("/reset", {"task_level": task_level})
    
    # 2. Hardcoded solution for the Easy Task to prove the grader works
    if task_level == "easy":
        print("Agent reading file...")
        send_post("/step", {
            "action_type": "ReadFile", 
            "action_data": {"filepath": "/data/user_data.txt"}
        })
        
        print("Agent writing redacted file...")
        send_post("/step", {
            "action_type": "WriteFile", 
            "action_data": {
                "filepath": "/data/user_data.txt", 
                "content": "Customer Profile:\nName: John Doe\nSSN: [REDACTED]\nStatus: Active"
            }
        })
        
        print("Agent submitting task...")
        send_post("/step", {
            "action_type": "SubmitTask", 
            "action_data": {"reasoning": "I replaced the SSN with [REDACTED]."}
        })
        
        res = send_post("/grader", {})
        score = res.get("score")
        print(f"Final Score for Easy: {score}")

if __name__ == "__main__":
    run_dummy_agent("easy")
    print("Baseline execution complete.")