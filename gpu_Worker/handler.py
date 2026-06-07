import sys
import runpod

def handler(job):
    user_input = (job.get("input") or {}).get("userInput")
    sys.stderr.write(f"THIS IS THE USER INPUT: {user_input}\n")
    sys.stderr.flush()
    return {"status": "done", "echo": user_input}

runpod.serverless.start({"handler": handler})
