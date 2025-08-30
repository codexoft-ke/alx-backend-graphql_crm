"""
Cron job functions for the CRM application.
"""

import os
import sys
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """
    Log a heartbeat message to confirm CRM application health.
    Also optionally queries the GraphQL hello field to verify endpoint responsiveness.
    """
    # Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"
    
    # Log to file
    log_file = "/tmp/crm_heartbeat_log.txt"
    
    try:
        # Append to the log file (don't overwrite)
        with open(log_file, "a") as f:
            f.write(f"{message}\n")
    except Exception as e:
        # If we can't write to log file, at least print the error
        print(f"Error writing to heartbeat log: {e}")
    
    # Optionally query GraphQL hello field to verify endpoint responsiveness
    try:
        # Create GraphQL client
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql',
            timeout=10
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # Simple hello query
        query = gql("""
        query {
            hello
        }
        """)
        
        # Execute the query
        result = client.execute(query)
        
        if result and 'hello' in result:
            # GraphQL endpoint is responsive
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL endpoint responsive: {result['hello']}\n")
        else:
            # GraphQL endpoint returned unexpected result
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL endpoint returned unexpected result\n")
                
    except Exception as e:
        # GraphQL endpoint is not responsive or there's an error
        try:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL endpoint error: {str(e)}\n")
        except:
            # Can't write to log file
            pass


def update_low_stock():
    """
    Execute the UpdateLowStockProducts mutation via GraphQL endpoint
    and log updated product information.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/low_stock_updates_log.txt"
    
    try:
        # Create GraphQL client
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql',
            timeout=30
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # UpdateLowStockProducts mutation
        mutation = gql("""
        mutation {
            updateLowStockProducts {
                success
                message
                count
                updatedProducts {
                    id
                    name
                    stock
                }
            }
        }
        """)
        
        # Execute the mutation
        result = client.execute(mutation)
        
        if result and 'updateLowStockProducts' in result:
            mutation_result = result['updateLowStockProducts']
            
            with open(log_file, "a") as f:
                f.write(f"{timestamp}: {mutation_result['message']}\n")
                
                if mutation_result['success'] and mutation_result['updatedProducts']:
                    for product in mutation_result['updatedProducts']:
                        product_name = product['name']
                        new_stock = product['stock']
                        f.write(f"{timestamp}: Updated product '{product_name}' - New stock: {new_stock}\n")
                elif mutation_result['count'] == 0:
                    f.write(f"{timestamp}: No products required stock updates\n")
        else:
            # Unexpected GraphQL response
            with open(log_file, "a") as f:
                f.write(f"{timestamp}: GraphQL mutation returned unexpected result\n")
                
    except Exception as e:
        # GraphQL endpoint error or mutation failed
        try:
            with open(log_file, "a") as f:
                f.write(f"{timestamp}: Error executing low stock update: {str(e)}\n")
        except:
            # Can't write to log file
            pass
