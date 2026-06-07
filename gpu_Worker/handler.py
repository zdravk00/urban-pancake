import os
import boto3
import runpod
from botocore.exceptions import ClientError

def handler(job):
    aws_access_key = os.getenv("IAM_USER_API_KEY")
    aws_secret_key = os.getenv("IAM_USER_SECRET")
    region = os.getenv("region_name", "eu-central-1")

    session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region
    )
    sts = session.client("sts")

    try:
        identity = sts.get_caller_identity()
        print("AWS connection OK", flush=True)
        return {
            "ok": True,
            "account": identity["Account"],
            "arn": identity["Arn"]
        }
    except ClientError as e:
        return {"error": e.response["Error"]["Message"]}

runpod.serverless.start({"handler": handler})