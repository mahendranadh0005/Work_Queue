from flask import Flask, jsonify
import redis
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from shared_models import Task, Metrics
from worker_config import (
    REDIS_URL, WORKER_PORT, WORKER_HOST, NUM_WORKERS, TASK_QUEUE, LOG_LEVEL, LOG_FILE
)
from worker_tasks import execute_task

# Setup logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app for metrics endpoint
app = Flask(__name__)

# Connect to Redis
try:
    rdb = redis.from_url(REDIS_URL, decode_responses=True)
    rdb.ping()
    logger.info(" Connected to Redis")
except Exception as e:
    logger.error(f" Failed to connect to Redis: {e}")
    exit(1)

# Metrics (thread-safe)
metrics_lock = threading.Lock()
metrics = Metrics(
    total_jobs_in_queue=0,
    jobs_done=0,
    jobs_failed=0
)


def update_metrics(key, value=1):
    with metrics_lock:
        if key == 'queue_length':
            metrics.total_jobs_in_queue = value
        elif key == 'jobs_done':
            metrics.jobs_done += value
        elif key == 'jobs_failed':
            metrics.jobs_failed += value


def worker_loop():
    
    logger.info(f" Worker thread started")
    
    while True:
        try:
            # Blocking pop: waits for a task (timeout 0 = wait forever)
            result = rdb.blpop(TASK_QUEUE, timeout=0)
            
            if not result:
                continue
            
            # result is a tuple: (queue_name, task_json)
            task_json = result[1]
            
            try:
                # Parse task
                task = Task.from_json(task_json)
                
                # Update queue length
                queue_length = rdb.llen(TASK_QUEUE)
                update_metrics('queue_length', queue_length)
                
                logger.info(f"")
                logger.info(f"{'='*60}")
                logger.info(f" Task Received: {task.type}")
                logger.info(f"   Payload: {task.payload}")
                logger.info(f"   Retries Left: {task.retries}")
                logger.info(f"{'='*60}")
                
                # Execute task
                try:
                    execute_task(task.type, task.payload)
                    
                    logger.info(f" Task Completed: {task.type}")
                    update_metrics('jobs_done', 1)
                    
                except Exception as task_error:
                    # Task execution failed
                    logger.error(f" Task Failed: {task.type}")
                    logger.error(f"Error: {str(task_error)}")
                    
                    # Retry logic
                    if task.retries > 0:
                        task.retries -= 1
                        logger.info(f"Retrying task ({task.retries} retries left)")
                        rdb.rpush(TASK_QUEUE, task.to_json())
                    else:
                        logger.error(f"Task failed permanently after all retries")
                        update_metrics('jobs_failed', 1)
                
            except Exception as parse_error:
                logger.error(f"Error parsing task: {str(parse_error)}")
                update_metrics('jobs_failed', 1)
        
        except Exception as e:
            logger.error(f"Worker error: {str(e)}")
            time.sleep(1)  # Wait before retrying


@app.route('/metrics', methods=['GET'])
def get_metrics():
    
    with metrics_lock:
        return jsonify(metrics.to_dict()), 200


@app.route('/health', methods=['GET'])
def health_check():
    try:
        rdb.ping()
        return jsonify({'status': 'healthy', 'redis': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


def run_flask():
    logger.info(f"📊 Starting Metrics Server on http://{WORKER_HOST}:{WORKER_PORT}")
    app.run(host=WORKER_HOST, port=WORKER_PORT, debug=False, use_reloader=False)


if __name__ == '__main__':
    logger.info("")
    logger.info("          WorkQueue Worker Service Starting             ")
    logger.info(f" Redis URL: {REDIS_URL}")
    logger.info(f"Task Queue: {TASK_QUEUE}")
    logger.info(f"Number of Workers: {NUM_WORKERS}")
    logger.info(f"Metrics Server: http://{WORKER_HOST}:{WORKER_PORT}/metrics")
    logger.info(f"Log File: {LOG_FILE}")
    logger.info("")
    
    # Start Flask metrics server in a thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Start worker threads
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        for i in range(NUM_WORKERS):
            executor.submit(worker_loop)
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down workers...")