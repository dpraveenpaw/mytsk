#!/usr/bin/env python3
import subprocess
import sys
import os
from datetime import datetime

def monitor_logs(source_log='/var/log/nginx/error.log', error_log='/var/log/nginx/filtered_errors.log'):
    try:
        # Use tail -f to follow the log file
        tail_process = subprocess.Popen(
            ['tail', '-f', source_log],  # Remove -n 0 to see existing entries
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Started monitoring at {timestamp}")
        
        with open(error_log, 'a') as error_file:
            header = f"\n=== Monitoring started at {timestamp} ===\n"
            error_file.write(header)
            error_file.flush()
            
            while True:
                line = tail_process.stdout.readline()
                if line:
                    # Log all entries for testing
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    error_file.write(f"{timestamp}: {line}")
                    error_file.flush()
                    print(f"Logged: {line.strip()}")
                    
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
        tail_process.terminate()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        tail_process.terminate()

if __name__ == "__main__":
    monitor_logs()
