import random
import time
import requests
import json
from datetime import datetime
import uuid

url = "http://localhost:3000/log"

log_levels = ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL']

def generate_random_id():
    return str(uuid.uuid4())

def generate_logs():
    log_level = random.choice(log_levels)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f'This is a {log_level} log'

    log = {
    "level": log_level,
	"message": message,
	# "timestamp": timestamp,
	"traceId": generate_random_id(),
    "spanId": generate_random_id(),
    "name": "Alice",
    "age": 25,
    }

    return log

def send_logs(log_data):
    response = requests.post(url,json=log_data)
    if response.status_code == 200:
        print(f"Log sent successfully: {log_data}")
    else:
        print(f"Failed to send log: {response.status_code}")

def main():
    while True:
        log_data = generate_logs()
        send_logs(log_data)
        time.sleep(random.randint(1,3))

if __name__ =="__main__":
    main()

