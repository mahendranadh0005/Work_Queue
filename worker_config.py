import os
from dotenv import load_dotenv

load_dotenv()

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Worker Configuration
WORKER_PORT = int(os.getenv('WORKER_PORT', 8000))
WORKER_HOST = os.getenv('WORKER_HOST', '0.0.0.0')
NUM_WORKERS = int(os.getenv('NUM_WORKERS', 3))

# Task Queue Name
TASK_QUEUE = 'task_queue'

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/worker.log')