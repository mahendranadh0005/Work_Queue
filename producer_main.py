from flask import Flask, request, jsonify
import redis
import logging
from shared_models import Task
from producer_config import (
    REDIS_URL, PRODUCER_PORT, PRODUCER_HOST, TASK_QUEUE, LOG_LEVEL
)

# Setup logging
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Connect to Redis
try:
    rdb = redis.from_url(REDIS_URL, decode_responses=True)
    rdb.ping() 
    logger.info(" Connected to Redis")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    exit(1)


@app.route('/enqueue', methods=['POST'])
def enqueue_task():
    
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Validate required fields
        if not data.get('type'):
            return jsonify({'error': 'Missing required field: type'}), 400
        
        if not data.get('payload'):
            return jsonify({'error': 'Missing required field: payload'}), 400
        
        # Create task object
        task = Task(
            type=data['type'],
            payload=data['payload'],
            retries=data.get('retries', 3)
        )
        
        # Validate task based on type
        if task.type == 'send_email':
            if 'to' not in task.payload or 'subject' not in task.payload:
                return jsonify({
                    'error': 'send_email requires "to" and "subject" in payload'
                }), 400
        
        # Add to Redis queue
        queue_length = rdb.rpush(TASK_QUEUE, task.to_json())
        
        logger.info(f" Task added: {task.type} (Queue length: {queue_length})")
        
        return jsonify({
            'status': 'success',
            'message': f"Task of type '{task.type}' has been successfully added to the queue",
            'queue_length': queue_length
        }), 201
    
    except Exception as e:
        logger.error(f" Error processing request: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    
    try:
        rdb.ping()
        return jsonify({'status': 'healthy', 'redis': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.route('/queue-stats', methods=['GET'])
def queue_stats():
   
    try:
        queue_length = rdb.llen(TASK_QUEUE)
        return jsonify({
            'queue_name': TASK_QUEUE,
            'items_in_queue': queue_length
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info(f" Starting Producer Server")
    logger.info(f" Address: http://{PRODUCER_HOST}:{PRODUCER_PORT}")
    logger.info(f" Redis: {REDIS_URL}")
    logger.info(f" Task Queue: {TASK_QUEUE}")
    logger.info("")
    logger.info("Endpoints:")
    logger.info("  POST   /enqueue      - Add a task to queue")
    logger.info("  GET    /health       - Health check")
    logger.info("  GET    /queue-stats  - Queue statistics")
    logger.info("")
    
    app.run(host=PRODUCER_HOST, port=PRODUCER_PORT, debug=False)