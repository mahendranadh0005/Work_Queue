import requests
import json
import time

PRODUCER_URL = "http://localhost:5000"


def send_task(task_type, payload, retries=3):
   
    url = f"{PRODUCER_URL}/enqueue"
    
    data = {
        "type": task_type,
        "payload": payload,
        "retries": retries
    }
    
    try:
        response = requests.post(url, json=data)
        print(f" {response.status_code}: {response.json()}")
        return response.json()
    except Exception as e:
        print(f" Error: {e}")
        return None


def get_queue_stats():
    try:
        response = requests.get(f"{PRODUCER_URL}/queue-stats")
        print(f"Queue Stats: {response.json()}")
        return response.json()
    except Exception as e:
        print(f" Error: {e}")


def get_metrics():
    try:
        response = requests.get("http://localhost:8000/metrics")
        print(f" Worker Metrics: {response.json()}")
        return response.json()
    except Exception as e:
        print(f" Error: {e}")


def main():
    print("=" * 60)
    print("WorkQueue Test Script")
    print("=" * 60)
    print()
    
    # Test 1: Send email task
    print("Test 1: Sending email task...")
    send_task(
        "send_email",
        {
            "to": "john@example.com",
            "subject": "Welcome to WorkQueue!",
            "body": "This is a test email"
        }
    )
    time.sleep(0.5)
    
    # Test 2: Send multiple emails
    print("\nTest 2: Sending 2 more email tasks...")
    send_task(
        "send_email",
        {
            "to": "jane@example.com",
            "subject": "Test Email 2"
        }
    )
    time.sleep(0.5)
    send_task(
        "send_email",
        {
            "to": "bob@example.com",
            "subject": "Test Email 3"
        }
    )
    time.sleep(0.5)
    
    # Test 3: Resize image task
    print("\nTest 3: Sending image resize task...")
    send_task(
        "resize_image",
        {
            "image_path": "/images/photo.jpg",
            "new_x": 1024,
            "new_y": 768
        }
    )
    time.sleep(0.5)
    
    # Test 4: Generate PDF task
    print("\nTest 4: Sending PDF generation task...")
    send_task(
        "generate_pdf",
        {
            "report_name": "Q4 Sales Report",
            "output_path": "/reports/q4_2024.pdf"
        }
    )
    time.sleep(0.5)
    
    # Test 5: Send notification
    print("\nTest 5: Sending notification task...")
    send_task(
        "send_notification",
        {
            "user_id": "user_12345",
            "message": "Your order #5678 has been shipped!",
            "type": "push"
        }
    )
    time.sleep(0.5)
    
    # Check queue stats
    print("\n" + "=" * 60)
    print("Queue Status (before processing)")
    print("=" * 60)
    get_queue_stats()
    
    # Wait for tasks to be processed
    print("\n Waiting 20 seconds for tasks to be processed...")
    time.sleep(20)
    
    # Check metrics
    print("\n" + "=" * 60)
    print("Final Worker Metrics")
    print("=" * 60)
    get_metrics()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n Error: {e}")