# WorkQueue (Python Edition)

A Distributed Background Task Processing System written in Python, using Redis for job queuing.

## What's the need for this?

This system is designed to handle the processing and execution of background tasks concurrently to improve user experience.

**Example:** When a user signs in to your website and clicks the login button, you might want to send them a welcome email. If that email task is part of the API call, the user would have to wait until the email is sent. Instead, you can add the "send_email" task to WorkQueue and let it handle the execution in the background.

**Note:** This is built to be modular — any type of job can be added to it, not just sending emails. You just need to add the logic for that job as described below.

## Services

This project provides two independent services:

### 1. Producer

Provides a `/enqueue` route to add your jobs/tasks via HTTP.

#### How to add a job?

- Send an HTTP POST request to the exposed `/enqueue` route at `http://localhost:5000/enqueue`
- It accepts a task in this format (JSON):

**Example: An inbuilt task the system supports is sending an email. Its JSON request would look like this:**

```json
{
    "type": "send_email",
    "retries": 3,
    "payload": {
        "to": "user@example.com",
        "subject": "Welcome to WorkQueue!",
        "body": "Thanks for signing up"
    }
}
```

**Parameters:**
- **type** - REQUIRED. Tells the producer the type of job being added to the queue.
- **retries** - Number of times the system should retry the job if it fails (default: 3).
- **payload** - Contains details about the task in key-value pairs. You can add any type/number of key-value pairs inside the payload, as the backend is built to flexibly accept all types.

This is the Python dataclass it accepts:

```python
@dataclass
class Task:
    type: str
    payload: Dict[str, Any]
    retries: int = 3
```

**Example Response:**

![Producer Response - Task Added Successfully](images/Screenshot%202026-02-15%20224223.png)

```json
{
    "status": "success",
    "message": "Task of type 'send_email' has been successfully added to the queue",
    "queue_length": 1
}
```

As you can see above, the producer successfully receives the task and responds with a 201 status code, confirming that the task has been added to the queue.

### 2. Worker

- Takes the jobs from the queue in a reliable manner and executes them
- Runs **3 worker threads in parallel** (configurable) for fast execution
- Provides a `/metrics` endpoint to view statistics
- Automatically retries failed tasks
- Logs all task execution to `logs/worker.log`

#### How to view the status of your jobs?

Send an HTTP GET request to `http://localhost:8000/metrics`

This will give a response like this:

```json
{
    "total_jobs_in_queue": 0,
    "jobs_done": 10,
    "jobs_failed": 1
}
```

**Metrics explained:**
- **total_jobs_in_queue** - Number of jobs inside the Redis queue at that moment
- **jobs_done** - Total number of jobs executed so far
- **jobs_failed** - Number of jobs that failed to execute, if any

## How are jobs executed?

Inside the `worker_tasks.py` file, you will find task handler functions. This design makes it modular - you can add your job type just by adding another function.

**To add a new type of task:** Just add a new function and register it in `TASK_HANDLERS` dict, and that's it!

```python
def execute_send_email(payload):
    """Actually send a real email"""
    to = payload.get('to')
    subject = payload.get('subject')
    body = payload.get('body')
    
    # Your email sending logic here
    send_real_email(to, subject, body)
    
    logger.info(f"Email sent to {to}")

def execute_resize_image(payload):
    """Resize an image file"""
    image_path = payload.get('image_path')
    new_x = payload.get('new_x')
    new_y = payload.get('new_y')
    
    # Your image resizing logic here
    resize_image_file(image_path, new_x, new_y)
    
    logger.info(f"Image resized to {new_x}x{new_y}")

def execute_generate_pdf(payload):
    """Generate a PDF report"""
    report_name = payload.get('report_name')
    
    # Your PDF generation logic here
    generate_pdf_file(report_name)
    
    logger.info(f"PDF generated: {report_name}")

# Register all tasks
TASK_HANDLERS = {
    'send_email': execute_send_email,
    'resize_image': execute_resize_image,
    'generate_pdf': execute_generate_pdf,
}
```

## Live Example - Task Execution

Here's a real example of the system in action. The worker logs show actual task execution:

### Worker Processing Tasks

![Worker Log - Task Execution in Progress](images/Screenshot%202026-02-15%20224316.png)

As shown above, the worker:
1. Receives the task (resize_image in this case)
2. Extracts the payload (image path, dimensions)
3. Processes the task
4. Logs the completion with timestamp

You can see multiple tasks being processed:
- Task Received: resize_image with payload `{'image_path': '/images/photo.jpg', 'new_x': 1024, 'new_y': 768}`
- Task Received: generate_pdf with payload `{'report_name': 'Q4 Sales Report', 'output_path': '/reports/q4_2024.pdf'}`
- Image resized from original to 1024x768
- Task Completed: resize_image

### Test Results

![Test Script Results - 6 Tasks Processed Successfully](images/Screenshot%202026-02-15%20224343.png)

The test script successfully:
- Sends email tasks to different recipients
- Sends image resize tasks
- Sends PDF generation tasks
- Sends notification tasks
- All tasks return 201 (Created) status
- Queue processes all tasks successfully

### Final Metrics

![Final Metrics - All Tasks Completed](images/Screenshot%202026-02-15%20224402.png)

Final metrics show:
- **6 jobs completed** (jobs_done: 6)
- **0 jobs failed** (jobs_failed: 0)
- **0 tasks in queue** (total_jobs_in_queue: 0)
- **Queue is empty** - all tasks processed

This demonstrates the system working perfectly with 100% success rate!




## Quick Start

### Prerequisites
- Python 3.8+
- Redis (running in Docker or locally)
- pip (Python package manager)

### Installation

```bash
# 1. Clone or download the project
cd workqueue

# 2. Create logs directory
mkdir -p logs

# 3. Install dependencies
pip install -r requirements.txt

# 4. Make sure Redis is running
redis-cli ping
# Output: PONG

# If Redis is not running, start it
docker run -d -p 6379:6379 redis:latest
```

### Running the System

**Terminal 1 - Start Producer (HTTP Server)**
```bash
python producer_main.py
```

You should see:
```
Starting Producer Server
Address: http://0.0.0.0:5000
Running on http://127.0.0.1:5000
```

**Terminal 2 - Start Worker (Task Processor)**
```bash
python worker_main.py
```

You should see:
```
WORKQUEUE WORKER STARTING
Redis: redis://localhost:6379/0
Workers: 3
Metrics: http://0.0.0.0:8000/metrics
```

**Terminal 3 - Send Tasks**
```bash
# Send an email task
curl -X POST http://localhost:5000/enqueue \
  -H "Content-Type: application/json" \
  -d '{
    "type": "send_email",
    "payload": {
      "to": "user@example.com",
      "subject": "Hello!"
    },
    "retries": 3
  }'

# Check metrics
curl http://localhost:8000/metrics
```

## Monitoring

### View Worker Logs (Real-time)
```bash
tail -f logs/worker.log
```

### Check Queue Status
```bash
curl http://localhost:5000/queue-stats
```

### Check Worker Metrics
```bash
curl http://localhost:8000/metrics
```

### View Tasks in Redis Queue
```bash
redis-cli
LLEN task_queue        # See how many tasks are queued
LRANGE task_queue 0 -1 # See all tasks
```

## Additional Features

### Concurrency
- **3 parallel worker threads** (configurable via `.env` - `NUM_WORKERS=3`)
- Tasks are processed simultaneously for fast execution
- Thread-safe metrics tracking

### Logging
- Each event is logged to `logs/worker.log`
- Helps trace success or failure of jobs
- Example log output:
```
[2026-02-15 22:00:00,123] INFO - Task Received: send_email
[2026-02-15 22:00:00,124] INFO -    Payload: {'to': 'user@example.com', 'subject': 'Hello'}
[2026-02-15 22:00:02,125] INFO - Task Completed: send_email
```

### Retry Logic
- Failed tasks are automatically retried
- Configurable number of retries per task
- Dead tasks (all retries failed) are logged

### Configuration
Edit `.env` to customize:
```env
REDIS_HOST=localhost
REDIS_PORT=6379
PRODUCER_PORT=5000
WORKER_PORT=8000
NUM_WORKERS=3
LOG_LEVEL=INFO
```

## File Structure

```
workqueue/
├── producer_main.py       # HTTP server that receives tasks
├── worker_main.py         # Task processor with 3 parallel workers
├── worker_tasks.py        # Task handler functions (edit this to add tasks)
├── shared_models.py       # Task and Metrics data classes
├── producer_config.py     # Producer configuration
├── worker_config.py       # Worker configuration
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore file
├── logs/
│   └── worker.log         # Worker execution logs
└── README.md              # This file
```

## Adding a New Task Type

**Step 1: Add function in `worker_tasks.py`**
```python
def execute_my_custom_task(payload):
    """Handle my custom task"""
    data = payload.get('data')
    # Your logic here
    logger.info(f"Custom task processed: {data}")
```

**Step 2: Register in `TASK_HANDLERS`**
```python
TASK_HANDLERS = {
    'send_email': execute_send_email,
    'my_custom_task': execute_my_custom_task,  # ADD THIS
}
```

**Step 3: Send the task**
```bash
curl -X POST http://localhost:5000/enqueue \
  -H "Content-Type: application/json" \
  -d '{
    "type": "my_custom_task",
    "payload": {"data": "hello"},
    "retries": 3
  }'
```

That's it! The worker will automatically handle your new task type.

## API Endpoints

### Producer Endpoints

**POST /enqueue**
- Add a task to the queue
- Returns: Task added confirmation

**GET /health**
- Check producer health status
- Returns: Health status and Redis connection status

**GET /queue-stats**
- Get current queue statistics
- Returns: Number of items in queue

### Worker Endpoints

**GET /metrics**
- Get worker metrics
- Returns: jobs_done, jobs_failed, total_jobs_in_queue

**GET /health**
- Check worker health status
- Returns: Health status and Redis connection status


## Troubleshooting

### Redis Connection Error
```
ConnectionError: Error 111 connecting to 127.0.0.1:6379
```
**Solution:** Start Redis
```bash
redis-cli ping  # Test connection
docker run -d -p 6379:6379 redis:latest  # Start Redis
```


### Tasks Not Processing
1. Check if worker is running
2. Check logs: `tail -f logs/worker.log`
3. Check queue: `curl http://localhost:5000/queue-stats`
4. Restart worker: `python worker_main.py`

