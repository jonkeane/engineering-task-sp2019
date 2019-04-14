from .celery_server import app
import time

@app.task
def process(msg):
    process_change(msg["wait"])
    return msg

def process_change(wait_secs):
    start = time.time()
    while time.time() - start < wait_secs:
        time.sleep(0.001)
