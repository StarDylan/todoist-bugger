import os
import schedule
import time
from datetime import datetime, timedelta
import requests
from todoist.api import TodoistAPI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TODOIST_API_TOKEN = os.getenv('TODOIST_API_TOKEN')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
REQUIRED_TASKS = ['Breakfast', 'Lunch', 'Dinner', 'Shower']

def check_planned_day():
    """Check if tomorrow is a planned day with all required tasks having specific times."""
    api = TodoistAPI(TODOIST_API_TOKEN)
    api.sync()
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    tasks = api.items.all()
    
    # Filter tasks for tomorrow
    tomorrow_tasks = [task for task in tasks if task['due'] and task['due']['date'] == tomorrow]
    
    # Check for required tasks with specific times
    planned_tasks = []
    for task in tomorrow_tasks:
        if task['content'] in REQUIRED_TASKS and task['due'].get('datetime'):
            planned_tasks.append(task['content'])
    
    # Check if all required tasks are planned
    missing_tasks = set(REQUIRED_TASKS) - set(planned_tasks)
    
    if missing_tasks:
        send_discord_notification(missing_tasks)

def send_discord_notification(missing_tasks):
    """Send a notification to Discord about missing planned tasks."""
    message = f"⚠️ **Tomorrow is not fully planned!**\nMissing tasks with specific times:\n"
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
    # Schedule the check to run every hour between 7 PM and 10 PM
    for hour in range(19, 23):  # 7 PM to 10 PM
        schedule.every().day.at(f"{hour:02d}:00").do(check_planned_day)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main() 