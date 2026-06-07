import os
import boto3
import yt_dlp
import runpod

def handler(job):
    user_input = (job.get("input") or {}).get("userInput")
    print(f"-----> THIS IS THE USER INPUT: {user_input}", flush=True)
    return {"status": "done"}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})