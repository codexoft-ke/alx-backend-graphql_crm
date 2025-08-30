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
