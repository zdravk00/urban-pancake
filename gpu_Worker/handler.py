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

# NEUE FUNKTION: Testet den Proxy
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
    
    # NEU: Mode Abfrage (0 = Download, 1 = Proxy Test)
    mode = job_input.get("mode", 0)
    
    if mode == 1:
        log("Running Proxy Diagnostic Mode...")
        return test_proxy_connection()

    # AB HIER: Deine existierende Download-Logik
    youtube_url = job_input.get("url") or job_input.get("userInput")
    if not youtube_url:
        return {"error": "Missing input.url"}

    # ... [Rest deines bestehenden Codes für AWS/S3] ...
    
    # WICHTIG: Füge hier in ydl_opts noch den Proxy hinzu
    proxy_url = os.getenv("PROXY_URL")
    ydl_opts = {
        "format": "bestaudio/best",
        "proxy": proxy_url, # Proxy wird hier für den Download genutzt
        "impersonate": "chrome-124", # Profi-Einstellung gegen Bot-Erkennung
        "outtmpl": "/tmp/%(id)s.%(ext)s",
        # ... restliche Optionen ...
    }
    
    # ... [Rest deines Handlers] ...
    return {"status": "success", "message": "Download completed"}

runpod.serverless.start({"handler": handler})