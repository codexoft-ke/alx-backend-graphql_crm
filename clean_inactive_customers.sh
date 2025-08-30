#!/bin/bash

# Get the current date and time for logging
timestamp=$(date +"%Y-%m-%d %H:%M:%S")

# Execute the Django command to delete inactive customers
deleted_count=$(python3 ../manage.py shell -c "from customers.models import Customer; from django.utils import timezone; one_year_ago = timezone.now() - timezone.timedelta(days=365); deleted = Customer.objects.filter(orders__isnull=True, created__lt=one_year_ago).delete()[0]; print(deleted)")

# Log the number of deleted customers
echo "$timestamp: Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt