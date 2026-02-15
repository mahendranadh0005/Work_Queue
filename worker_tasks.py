

import time
import logging

logger = logging.getLogger(__name__)


def execute_send_email(payload):
    to = payload.get('to')
    subject = payload.get('subject')
    body = payload.get('body', 'No body provided')
    
    # Simulate email sending delay
    time.sleep(2)
    
    logger.info(f" Email sent to {to}")
    logger.info(f"   Subject: {subject}")
    logger.info(f"   Body: {body}")
    
    print(f"[SEND_EMAIL] Sending email to {to} with subject '{subject}'")


def execute_resize_image(payload):
    image_path = payload.get('image_path', 'unknown')
    new_x = payload.get('new_x', 0)
    new_y = payload.get('new_y', 0)
    
    # Simulate image processing delay
    time.sleep(3)
    
    logger.info(f"  Image resized: {image_path}")
    logger.info(f"   New dimensions: {new_x}x{new_y}")
    
    print(f"[RESIZE_IMAGE] Resizing image to {new_x}x{new_y}")


def execute_generate_pdf(payload):
    report_name = payload.get('report_name', 'Unknown Report')
    output_path = payload.get('output_path', 'output.pdf')
    
    # Simulate PDF generation delay
    time.sleep(4)
    
    logger.info(f" PDF generated: {report_name}")
    logger.info(f"   Output: {output_path}")
    
    print(f"[GENERATE_PDF] Generating PDF for {report_name}")


def execute_send_notification(payload):
    user_id = payload.get('user_id', 'unknown')
    message = payload.get('message', 'No message')
    notification_type = payload.get('type', 'push')
    
    # Simulate notification sending delay
    time.sleep(1)
    
    logger.info(f" Notification sent to {user_id}")
    logger.info(f"   Type: {notification_type}")
    logger.info(f"   Message: {message}")
    
    print(f"[SEND_NOTIFICATION] Sending {notification_type} to {user_id}")


# Mapping of task types to their execution functions
TASK_HANDLERS = {
    'send_email': execute_send_email,
    'resize_image': execute_resize_image,
    'generate_pdf': execute_generate_pdf,
    'send_notification': execute_send_notification,
}


def execute_task(task_type, payload):
    
    if task_type not in TASK_HANDLERS:
        raise ValueError(f"Unsupported task type: {task_type}")
    
    handler = TASK_HANDLERS[task_type]
    handler(payload)