#!/bin/bash

# Get the current date and time for logging
timestamp=$(date +"%Y-%m-%d %H:%M:%S")

# Change to the project directory
cd "$(dirname "$0")/../.."

# Execute the Django command to delete inactive customers
# Delete customers with no orders since a year ago
deleted_count=$(python3 manage.py shell -c "
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

one_year_ago = timezone.now() - timedelta(days=365)
customers_to_delete = Customer.objects.filter(orders__isnull=True, created_at__lt=one_year_ago)
count = customers_to_delete.count()
customers_to_delete.delete()
print(count)
")

# Log the number of deleted customers
echo "$timestamp: Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt
