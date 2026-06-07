import os
import sys
import boto3
import yt_dlp
import runpod
from botocore.exceptions import ClientError

def log(msg: str):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

def handler(job):
    job_input = job.get("input") or {}

    # Du kannst weiter "userInput" schicken (YouTube-URL), oder "url"
    youtube_url = job_input.get("url") or job_input.get("userInput")
    if not youtube_url:
        return {"error": "Missing input.url (or input.userInput)"}

    bucket_name = os.getenv("S3_BUCKET_NAME")
    if not bucket_name:
        return {"error": "Missing env var S3_BUCKET_NAME"}

    # optional: Wunsch-Dateiname, sonst jobId.wav
    job_id = job.get("id", "no-job-id")
    s3_key = job_input.get("file_name") or f"{job_id}.wav"

    log(f"URL erhalten: {youtube_url}")

    # AWS creds
    aws_access_key = os.getenv("IAM_USER_API_KEY")
    aws_secret_key = os.getenv("IAM_USER_SECRET")
    region = os.getenv("region_name", "eu-central-1")

    if not aws_access_key or not aws_secret_key:
        return {"error": "Missing IAM_USER_API_KEY or IAM_USER_SECRET env var"}

    session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region,
    )

    # AWS check (STS) + S3 client
    sts = session.client("sts")
    s3 = session.client("s3")

    try:
        identity = sts.get_caller_identity()
        log(f"AWS check success (Account {identity['Account']})")
    except ClientError as e:
        return {"error": f"AWS check failed: {e.response['Error']['Message']}"}

    # Download + Convert to wav (ffmpeg erforderlich!)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "/tmp/%(id)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }],
    }

    try:
        log("Download start")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_id = info["id"]

        local_file = f"/tmp/{video_id}.wav"
        if not os.path.exists(local_file):
            return {"error": f"Download failed: file not found: {local_file}"}

        log("Download success")
    except Exception as e:
        return {"error": f"Download failed: {str(e)}"}

    # Upload to S3
    try:
        log(f"Upload start: s3://{bucket_name}/{s3_key}")
        s3.upload_file(local_file, bucket_name, s3_key)
        log("Upload success")
    except ClientError as e:
        return {"error": f"Upload failed: {e.response['Error']['Message']}"}
    finally:
        try:
            os.remove(local_file)
        except Exception:
            pass

    return {
        "status": "success",
        "bucket": bucket_name,
        "key": s3_key,
        "region": region,
    }

runpod.serverless.start({"handler": handler})
