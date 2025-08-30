# CRM Celery Setup Guide

This guide explains how to set up and run Celery tasks for the CRM application, including weekly report generation.

## Prerequisites

- Python 3.8+
- Django
- Redis server
- All dependencies from requirements.txt

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- celery>=5.3.0
- django-celery-beat>=2.5.0
- redis>=4.0.0
- All other project dependencies

### 2. Install and Start Redis

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### On macOS (using Homebrew):
```bash
brew install redis
brew services start redis
```

#### On Windows:
Download and install Redis from the official website or use WSL.

#### Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### 3. Run Django Migrations

```bash
python manage.py migrate
```

This creates the necessary database tables for django-celery-beat.

### 4. Create Database Tables for Celery Beat

```bash
python manage.py migrate django_celery_beat
```

## Running Celery

### 1. Start Celery Worker

Open a terminal and run:

```bash
celery -A crm worker -l info
```

This starts the Celery worker that will execute tasks.

### 2. Start Celery Beat (Scheduler)

Open another terminal and run:

```bash
celery -A crm beat -l info
```

This starts the Celery Beat scheduler that will trigger tasks according to the schedule.

### 3. Optional: Start Celery Flower (Monitoring)

For monitoring tasks in a web interface:

```bash
pip install flower
celery -A crm flower
```

Then visit http://localhost:5555 in your browser.

## Configuration

### Celery Settings

The Celery configuration is in `crm/settings.py`:

```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
```

### Scheduled Tasks

- **CRM Report Generation**: Runs every Monday at 6:00 AM UTC
  - Task: `crm.tasks.generate_crm_report`
  - Generates weekly report with total customers, orders, and revenue
  - Logs results to `/tmp/crm_report_log.txt`

## Manual Task Execution

### Test the CRM Report Task

```bash
# In Django shell
python manage.py shell

# Execute the task
from crm.tasks import generate_crm_report
result = generate_crm_report.delay()
print(result.get())
```

### Test with Fallback Method

```bash
# In Django shell
python manage.py shell

# Execute the fallback task
from crm.tasks import generate_crm_report_fallback
result = generate_crm_report_fallback.delay()
print(result.get())
```

## Verification

### 1. Check Celery Worker Logs

The Celery worker terminal should show:
- Task registrations
- Task executions
- Any errors or warnings

### 2. Check Celery Beat Logs

The Celery Beat terminal should show:
- Scheduler startup
- Task scheduling events
- Beat schedule information

### 3. Check CRM Report Logs

```bash
cat /tmp/crm_report_log.txt
```

Expected format:
```
YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, Z revenue
```

### 4. Check Redis Connection

```bash
redis-cli monitor
```

This shows real-time Redis commands, including Celery task messages.

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Make sure Redis server is running
   - Check if Redis is accessible on localhost:6379
   - Verify firewall settings

2. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration
   - Verify Django settings module

3. **Task Not Executing**
   - Check if both worker and beat are running
   - Verify task registration in worker logs
   - Check Django timezone settings

4. **GraphQL Endpoint Errors**
   - Ensure Django development server is running
   - Check GraphQL endpoint accessibility
   - Use fallback task if endpoint is unavailable

### Debug Commands

```bash
# Check Celery configuration
celery -A crm inspect conf

# List registered tasks
celery -A crm inspect registered

# Check active tasks
celery -A crm inspect active

# Check scheduled tasks
celery -A crm inspect scheduled
```

## Production Considerations

1. **Use a Process Manager**: Use supervisord or systemd to manage Celery processes
2. **Monitoring**: Set up proper monitoring with Flower or other tools
3. **Logging**: Configure proper logging for production environments
4. **Security**: Secure Redis instance and use authentication
5. **Scaling**: Consider multiple workers for high load scenarios

## File Structure

```
crm/
├── __init__.py          # Celery app initialization
├── celery.py           # Celery configuration
├── tasks.py            # Celery tasks
├── settings.py         # Django settings with Celery config
└── README.md           # This file
```
