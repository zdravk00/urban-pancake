import sys
import os
import boto3
import runpod
from botocore.exceptions import ClientError

def handler(job):
    job_input = job.get("input") or {}
    user_input = job_input.get("userInput")

    sys.stderr.write(f"user Input --------------------> {user_input}\n")
    sys.stderr.flush()

    aws_access_key = os.getenv("IAM_USER_API_KEY")
    aws_secret_key = os.getenv("IAM_USER_SECRET")
    region = os.getenv("region_name", "eu-central-1")

    if not aws_access_key or not aws_secret_key:
        return {"error": "Missing IAM_USER_API_KEY or IAM_USER_SECRET env var"}

    session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region
    )
    sts = session.client("sts")

    try:
        identity = sts.get_caller_identity()
        sys.stderr.write("AWS connection OK\n")
        sys.stderr.flush()
        return {
            "ok": True,
            "account": identity["Account"],
            "arn": identity["Arn"],
            "echo": user_input
        }
    except ClientError as e:
        return {"error": e.response["Error"]["Message"]}

runpod.serverless.start({"handler": handler})
