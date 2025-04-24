import os
import schedule
import time
import argparse
from datetime import datetime, timedelta
import requests
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TODOIST_API_TOKEN = os.getenv('TODOIST_API_TOKEN')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
REQUIRED_TASKS = ['Plan for the Next Day']

def check_planned_day():
    """Check if tomorrow is a planned day with all required tasks having specific times."""
    api = TodoistAPI(TODOIST_API_TOKEN)
    tasks = api.get_tasks(filter='tomorrow')
    
    # Check for required tasks with specific times
    planned_tasks = set()
    for task in tasks:
        if task.content in REQUIRED_TASKS and task.due.datetime:
            planned_tasks.add(task.content)
    
    # Check if all required tasks are planned
    missing_tasks = set(REQUIRED_TASKS) - planned_tasks
    print(REQUIRED_TASKS, planned_tasks, missing_tasks)
    
    if missing_tasks:
        send_discord_notification(missing_tasks)
        return False
    return True

def send_discord_notification(missing_tasks):
    """Send a notification to Discord about missing planned tasks."""
    message = "⚠️ **Tomorrow is not fully planned!**\nMissing tasks with specific times:\n"
    for task in missing_tasks:
        message += f"- {task}\n"
    
    payload = {
        "content": message
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending Discord notification: {e}")

def main():
    parser = argparse.ArgumentParser(description='Check Todoist tasks for planned day')
    parser.add_argument('--check-now', action='store_true', help='Run a single check and exit')
    args = parser.parse_args()

    if args.check_now:
        result = check_planned_day()
        print("Check completed. All tasks planned." if result else "Check completed. Missing tasks found.")
        return

    # Schedule the check to run every hour between 7 PM and 10 PM
    for hour in range(19, 23):  # 7 PM to 10 PM
        schedule.every().day.at(f"{hour:02d}:00").do(check_planned_day)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main() 