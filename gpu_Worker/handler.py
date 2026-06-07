import os
import sys
import boto3
import yt_dlp
import runpod
import urllib.request
from botocore.exceptions import ClientError

def log(msg: str):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

def test_proxy_connection():
    proxy_url = os.getenv("PROXY_URL")
    if not proxy_url:
        return {"error": "PROXY_URL not set"}
    
    url = 'https://geo.brdtest.com/welcome.txt?product=isp&method=native'
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({'https': proxy_url, 'http': proxy_url})
    )
    try:
        response = opener.open(url, timeout=10).read().decode()
        return {"status": "success", "proxy_response": response}
    except Exception as e:
        return {"error": f"Proxy test failed: {str(e)}"}

def handler(job):
    job_input = job.get("input") or {}
    mode = job_input.get("mode", 0)
    
    # 1. Modus 1: Proxy Check
    if mode == 1:
        log("Running Proxy Diagnostic Mode...")
        return test_proxy_connection()

    # 2. Modus 0: Voller Download & Upload
    youtube_url = job_input.get("url") or job_input.get("userInput")
    if not youtube_url:
        return {"error": "Missing input.url"}

    bucket_name = os.getenv("S3_BUCKET_NAME")
    job_id = job.get("id", "no-job-id")
    s3_key = job_input.get("file_name") or f"{job_id}.wav"
    proxy_url = os.getenv("PROXY_URL")

    # AWS Setup
    session = boto3.Session(
        aws_access_key_id=os.getenv("IAM_USER_API_KEY"),
        aws_secret_access_key=os.getenv("IAM_USER_SECRET"),
        region_name=os.getenv("region_name", "eu-central-1"),
    )
    s3 = session.client("s3")

    # YTDLP Optionen
    ydl_opts = {
        "format": "bestaudio/best",
        "proxy": proxy_url,
        "impersonate": "chrome-124",
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
        log(f"Download start for {youtube_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_id = info["id"]

        local_file = f"/tmp/{video_id}.wav"
        if not os.path.exists(local_file):
            return {"error": "Download failed: file not found"}

        log(f"Upload start: s3://{bucket_name}/{s3_key}")
        s3.upload_file(local_file, bucket_name, s3_key)
        
        if os.path.exists(local_file):
            os.remove(local_file)
            
        log("Process success")
        return {"status": "success", "bucket": bucket_name, "key": s3_key}

    except Exception as e:
        return {"error": f"Failed: {str(e)}"}

runpod.serverless.start({"handler": handler})