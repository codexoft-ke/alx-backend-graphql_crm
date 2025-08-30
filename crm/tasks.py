"""
Celery tasks for the CRM application.
"""

from celery import shared_task
from datetime import datetime
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import django
import os

# Ensure Django is set up
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()


@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report with total customers, orders, and revenue.
    Uses GraphQL queries to fetch the data and logs the report.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/crm_report_log.txt"
    
    try:
        # Create GraphQL client
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql',
            timeout=30
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # GraphQL query to get CRM statistics
        query = gql("""
        query {
            allCustomers {
                edges {
                    node {
                        id
                    }
                }
            }
            allOrders {
                edges {
                    node {
                        id
                        totalAmount
                    }
                }
            }
        }
        """)
        
        # Execute the query
        result = client.execute(query)
        
        if result:
            # Calculate statistics
            customers = result.get('allCustomers', {}).get('edges', [])
            orders = result.get('allOrders', {}).get('edges', [])
            
            total_customers = len(customers)
            total_orders = len(orders)
            
            # Calculate total revenue
            total_revenue = 0
            for order_edge in orders:
                order = order_edge.get('node', {})
                amount = order.get('totalAmount', 0)
                if amount:
                    total_revenue += float(amount)
            
            # Format the report
            report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue"
            
            # Log the report
            with open(log_file, "a") as f:
                f.write(f"{report_message}\n")
            
            return f"CRM report generated successfully: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue"
            
        else:
            error_message = f"{timestamp} - Error: Failed to fetch data from GraphQL endpoint"
            with open(log_file, "a") as f:
                f.write(f"{error_message}\n")
            return "Failed to generate CRM report: No data received"
            
    except Exception as e:
        # Handle any errors
        error_message = f"{timestamp} - Error generating CRM report: {str(e)}"
        try:
            with open(log_file, "a") as f:
                f.write(f"{error_message}\n")
        except:
            pass
        return f"Failed to generate CRM report: {str(e)}"


@shared_task
def generate_crm_report_fallback():
    """
    Fallback CRM report generation using Django ORM directly.
    This can be used when the GraphQL endpoint is not available.
    """
    from crm.models import Customer, Order
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/crm_report_log.txt"
    
    try:
        # Get statistics using Django ORM
        total_customers = Customer.objects.count()
        total_orders = Order.objects.count()
        
        # Calculate total revenue
        orders = Order.objects.all()
        total_revenue = sum(float(order.total_amount) for order in orders if order.total_amount)
        
        # Format the report
        report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue"
        
        # Log the report
        with open(log_file, "a") as f:
            f.write(f"{report_message}\n")
        
        return f"CRM report generated successfully (fallback): {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue"
        
    except Exception as e:
        error_message = f"{timestamp} - Error generating CRM report (fallback): {str(e)}"
        try:
            with open(log_file, "a") as f:
                f.write(f"{error_message}\n")
        except:
            pass
        return f"Failed to generate CRM report (fallback): {str(e)}"
