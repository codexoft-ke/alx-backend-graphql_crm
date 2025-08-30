#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')

try:
    django.setup()
    from crm.models import Order
    
    def get_recent_orders_direct():
        """Get orders from the last 7 days using Django ORM"""
        seven_days_ago = datetime.now() - timedelta(days=7)
        orders = Order.objects.filter(order_date__gte=seven_days_ago).select_related('customer')
        return orders
    
    def log_order_reminders_direct(orders):
        """Log order reminders to the log file using direct ORM results"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = "/tmp/order_reminders_log.txt"
        
        try:
            with open(log_file, "a") as f:
                if orders:
                    f.write(f"{timestamp}: Processing {len(orders)} recent orders\n")
                    
                    for order in orders:
                        order_id = order.id
                        customer_email = order.customer.email
                        customer_name = order.customer.name
                        order_date = order.order_date.isoformat()
                        
                        f.write(f"{timestamp}: Order ID: {order_id}, Customer: {customer_name} ({customer_email}), Date: {order_date}\n")
                else:
                    f.write(f"{timestamp}: No recent orders found\n")
                    
        except Exception as e:
            print(f"Error writing to log file: {str(e)}")
    
    def main():
        """Main function to process order reminders using Django ORM"""
        
        print("Processing order reminders...")
        
        # Get orders directly from Django ORM
        orders = get_recent_orders_direct()
        
        # Log the reminders
        log_order_reminders_direct(orders)
        
        print("Order reminders processed!")
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Error importing Django modules: {e}")
    print("Falling back to basic logging...")
    
    # Fallback version that just logs a message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/order_reminders_log.txt"
    
    try:
        with open(log_file, "a") as f:
            f.write(f"{timestamp}: Order reminders script executed (Django not available)\n")
    except Exception as e:
        print(f"Error writing to log file: {str(e)}")
    
    print("Order reminders processed!")
