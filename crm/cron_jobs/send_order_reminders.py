#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta
import requests
import json

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

def send_graphql_query():
    """Send GraphQL query to get orders from the last 7 days"""
    
    # Calculate the date 7 days ago
    seven_days_ago = datetime.now() - timedelta(days=7)
    seven_days_ago_str = seven_days_ago.isoformat()
    
    # GraphQL query to get orders from the last 7 days
    query = """
    query GetRecentOrders($orderDateGte: DateTime) {
        allOrders(orderDateGte: $orderDateGte) {
            edges {
                node {
                    id
                    orderDate
                    customer {
                        email
                        name
                    }
                }
            }
        }
    }
    """
    
    variables = {
        "orderDateGte": seven_days_ago_str
    }
    
    payload = {
        "query": query,
        "variables": variables
    }
    
    try:
        # Send the GraphQL request
        response = requests.post(
            'http://localhost:8000/graphql',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"GraphQL request failed with status {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to GraphQL endpoint at http://localhost:8000/graphql")
        print("Make sure the Django server is running.")
        return None
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def log_order_reminders(orders_data):
    """Log order reminders to the log file"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/order_reminders_log.txt"
    
    try:
        with open(log_file, "a") as f:
            if orders_data and 'data' in orders_data and 'allOrders' in orders_data['data']:
                orders = orders_data['data']['allOrders']['edges']
                
                if orders:
                    f.write(f"{timestamp}: Processing {len(orders)} recent orders\n")
                    
                    for edge in orders:
                        order = edge['node']
                        order_id = order['id']
                        customer_email = order['customer']['email']
                        customer_name = order['customer']['name']
                        order_date = order['orderDate']
                        
                        f.write(f"{timestamp}: Order ID: {order_id}, Customer: {customer_name} ({customer_email}), Date: {order_date}\n")
                else:
                    f.write(f"{timestamp}: No recent orders found\n")
            else:
                f.write(f"{timestamp}: Error retrieving orders data\n")
                
    except Exception as e:
        print(f"Error writing to log file: {str(e)}")

def main():
    """Main function to process order reminders"""
    
    print("Processing order reminders...")
    
    # Get orders from GraphQL
    orders_data = send_graphql_query()
    
    # Log the reminders
    log_order_reminders(orders_data)
    
    print("Order reminders processed!")

if __name__ == "__main__":
    main()
