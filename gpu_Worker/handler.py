import os
import boto3
import yt_dlp

# S3 Client initialisieren
s3_client = boto3.client('s3', region_name='eu-central-1')

def handler(job):
    job_input = job.get("input", {})
    youtube_url = job_input.get("url")
    
    # HIER DIE KORREKTUR: Wir holen den KEY, nicht den Wert!
    bucket_name = os.environ.get('S3_BUCKET_NAME') 
    
    file_name = f"{job.get('id')}.wav"
    local_path = f"/tmp/{file_name}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': '/tmp/%(id)s.%(ext)s',
        'quiet': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        # yt-dlp benennt die Datei oft leicht anders, wir suchen den Pfad dynamisch
        downloaded_file = f"/tmp/{info['id']}.wav"
        
    # Upload zu S3
    s3_client.upload_file(downloaded_file, bucket_name, file_name)
    
    # Aufräumen
    os.remove(downloaded_file)
    
    return {
        "status": "success",
        "s3_url": f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
    }