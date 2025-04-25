import os
import argparse
import requests
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv
import logging
from pythonjsonlogger import jsonlogger
import sys

def setup_logging(use_json: bool):
    """Configure logging based on the specified format."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler()
    
    if use_json:
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

def validate_environment():
    """Validate that all required environment variables are present."""
    required_vars = ['TODOIST_API_TOKEN', 'DISCORD_WEBHOOK_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error("Missing required environment variables", extra={'missing_vars': missing_vars})
        logger.error("Please ensure all required variables are set")
        return False

    return True

# Load environment variables
load_dotenv()

# Configuration
TODOIST_API_TOKEN = os.getenv('TODOIST_API_TOKEN')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
REQUIRED_TASKS = ['Plan for the Next Day']

def check_planned_day():
    """Check if tomorrow is a planned day with all required tasks having specific times."""
    logger.info("Starting planned day check")
    api = TodoistAPI(TODOIST_API_TOKEN)
    tasks = api.get_tasks(filter='tomorrow')
    
    # Check for required tasks with specific times
    planned_tasks = set()
    for task in tasks:
        if task.content in REQUIRED_TASKS and task.due.datetime:
            planned_tasks.add(task.content)
    
    # Check if all required tasks are planned
    missing_tasks = set(REQUIRED_TASKS) - planned_tasks
    logger.debug("Task check results", extra={
        'required_tasks': list(REQUIRED_TASKS),
        'planned_tasks': list(planned_tasks),
        'missing_tasks': list(missing_tasks)
    })
    
    if missing_tasks:
        logger.info("Missing required tasks for tomorrow", extra={'missing_tasks': list(missing_tasks)})
        send_discord_notification(missing_tasks)
        return False
    logger.info("All required tasks are planned for tomorrow")
    return True

def send_discord_notification(missing_tasks):
    """Send a notification to Discord about missing planned tasks."""
    logger.info("Sending Discord notification for missing tasks")
    message = "⚠️ **Tomorrow is not fully planned!**\nMissing tasks with specific times:\n"
    for task in missing_tasks:
        message += f"- {task}\n"
    
    payload = {
        "content": message
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        logger.info("Discord notification sent successfully")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Discord notification: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description='Check Todoist tasks for planned day')
    parser.add_argument('--json-logging', action='store_true', help='Use JSON structured logging')
    args = parser.parse_args()

    # Setup logging based on the flag
    global logger
    logger = setup_logging(args.json_logging)
    logger.info("Starting application", extra={'json_logging': args.json_logging})

    # Validate environment variables
    success = validate_environment()

    if not success:
        logger.error("Exiting due to missing environment variables")
        sys.exit(1)
        return

    # Run a single check
    result = check_planned_day()
    logger.info("Check completed", extra={'all_tasks_planned': result})

if __name__ == "__main__":
    main() 