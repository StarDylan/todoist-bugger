# Todoist Daily Planner Checker

This application checks your Todoist tasks to ensure you have properly planned tomorrow's day. It verifies that you have scheduled the "Plan for the Next Day" task with a specific time. If the task is missing or doesn't have a specific time set, it will send a notification to your Discord channel.

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and fill in your credentials:
   - `TODOIST_API_TOKEN`: Your Todoist API token
   - `DISCORD_WEBHOOK_URL`: Your Discord webhook URL

## Running the Application

### Using Python

1. Ensure you have Python 3.13+ installed
2. Install dependencies:
   ```bash
   uv sync --locked
   ```
3. Run the application:
   ```bash
   uv run main.py
   ```

### Command Line Arguments

- `--check-now`: Run a single check and exit
- `--json-logging`: Use JSON structured logging instead of plain text

### Running with Docker

1. Build the Docker image:
   ```bash
   docker build -t todoist-bugger .
   ```

2. Run the container:
   ```bash
   docker run -d --env-file .env todoist-bugger
   ```

## How it Works

- The application runs checks every hour between 7 PM and 10 PM
- It looks for tomorrow's tasks in your Todoist
- It verifies that you have the "Plan for the Next Day" task with a specific time set
- If the task is missing or doesn't have a specific time, it will send a notification to your Discord channel

## Requirements

- Python 3.13+
- Docker (optional)
- Todoist API token
- Discord webhook URL
