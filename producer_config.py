import os
from dotenv import load_dotenv

load_dotenv()

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Producer Configuration
PRODUCER_PORT = int(os.getenv('PRODUCER_PORT', 5000))
PRODUCER_HOST = os.getenv('PRODUCER_HOST', '0.0.0.0')

# Task Queue Name
TASK_QUEUE = 'task_queue'

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')