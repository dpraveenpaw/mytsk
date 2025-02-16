#!/usr/bin/env python3
import subprocess
import sys

def monitor_logs(source_log='server.log', error_log='server_errors.log'):
    try:
        # Use tail -f to follow the log file
        tail_process = subprocess.Popen(
            ['tail', '-f', '-n', '0', source_log],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Open error log in append mode
        with open(error_log, 'a') as error_file:
            print(f"Monitoring {source_log} for errors...")
            
            # Process each new line
            while True:
                line = tail_process.stdout.readline()
                if 'ERROR' in line.upper():
                    error_file.write(line)
                    error_file.flush()
                    
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
        tail_process.terminate()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        tail_process.terminate()

if __name__ == "__main__":
    monitor_logs('/var/log/nginx/error.log', '/var/log/nginx/server_errors.log')
