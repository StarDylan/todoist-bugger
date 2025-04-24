import os
import schedule
import time
import argparse
from datetime import datetime, timedelta
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
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please ensure all required variables are set in your .env file")
        sys.exit(1)

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
        send_discord_notification(missing_tasks)
        logger.info("Missing required tasks for tomorrow", extra={'missing_tasks': list(missing_tasks)})
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
        logger.error("Failed to send Discord notification", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description='Check Todoist tasks for planned day')
    parser.add_argument('--check-now', action='store_true', help='Run a single check and exit')
    parser.add_argument('--json-logging', action='store_true', help='Use JSON structured logging')
    args = parser.parse_args()

    # Setup logging based on the flag
    global logger
    logger = setup_logging(args.json_logging)
    logger.info("Starting application", extra={'check_now': args.check_now, 'json_logging': args.json_logging})

    # Validate environment variables
    validate_environment()

    if args.check_now:
        result = check_planned_day()
        logger.info("Single check completed", extra={'all_tasks_planned': result})
        return

    # Schedule the check to run every hour between 7 PM and 10 PM
    for hour in range(19, 23):  # 7 PM to 10 PM
        schedule.every().day.at(f"{hour:02d}:00").do(check_planned_day)
        logger.info(f"Scheduled check for {hour:02d}:00")
    
    logger.info("Entering main scheduling loop")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main() 