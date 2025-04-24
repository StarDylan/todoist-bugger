# Todoist Daily Planner Checker

This application checks your Todoist tasks to ensure you have a properly planned day for tomorrow. It verifies that you have scheduled times for Breakfast, Lunch, Dinner, and Shower tasks. If any of these tasks are missing or don't have specific times set, it will send a notification to your Discord channel.

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and fill in your credentials:
   - `TODOIST_API_TOKEN`: Your Todoist API token
   - `DISCORD_WEBHOOK_URL`: Your Discord webhook URL

## Running with Docker

1. Build the Docker image:
   ```bash
   docker build -t todoist-planner .
   ```

2. Run the container:
   ```bash
   docker run -d --env-file .env todoist-planner
   ```

## How it Works

- The application runs checks every hour between 7 PM and 10 PM
- It looks for tomorrow's tasks in your Todoist
- It verifies that you have the following tasks with specific times set:
  - Breakfast
  - Lunch
  - Dinner
  - Shower
- If any of these tasks are missing or don't have specific times, it will send a notification to your Discord channel

## Requirements

- Python 3.11+
- Docker (optional)
- Todoist API token
- Discord webhook URL 