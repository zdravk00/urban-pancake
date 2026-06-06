import runpod

def handler(job):
    # Einfachste Antwort, um zu zeigen: Es läuft!
    return {"status": "success", "message": "GPU ist bereit und empfängt Befehle"}

runpod.serverless.start({"handler": handler})