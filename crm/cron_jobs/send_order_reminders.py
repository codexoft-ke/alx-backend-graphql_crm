#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

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
    
    # Create a GraphQL client
    transport = RequestsHTTPTransport(
        url='http://localhost:8000/graphql',
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)
    
    # GraphQL query to get orders from the last 7 days
    query = gql("""
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
    """)
    
    variables = {
        "orderDateGte": seven_days_ago_str
    }
    
    try:
        # Execute the GraphQL query
        result = client.execute(query, variable_values=variables)
        return {"data": result}
        
    except Exception as e:
        print(f"Error executing GraphQL query: {str(e)}")
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
