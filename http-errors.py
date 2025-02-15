#!/usr/bin/env python3
import os
import time
from datetime import datetime
import argparse
import re

class LogNavigator:
    def __init__(self, log_file):
        self.log_file = log_file
        self.cursor = 0
        self.buffer_size = 4096
        self.total_size = self.get_file_size()
        # Regex pattern to match log lines and extract status code
        self.log_pattern = re.compile(r'.*" (\d{3}) .*')
    
    def get_file_size(self):
        return os.path.getsize(self.log_file)
    
    def get_progress(self):
        return (self.cursor / self.total_size) * 100 if self.total_size > 0 else 0
    
    def is_5xx_error(self, line):
        """Check if the log line contains a 5xx status code"""
        match = self.log_pattern.match(line)
        if match:
            status_code = int(match.group(1))
            return 500 <= status_code < 600
        return False
    
    def read_chunk_with_5xx_filter(self, position, size, lines_needed=10):
        with open(self.log_file, 'r') as f:
            f.seek(max(0, position))
            error_lines = []
            bytes_read = 0
            
            while len(error_lines) < lines_needed:
                chunk = f.read(self.buffer_size)
                if not chunk:
                    break
                
                bytes_read += len(chunk)
                for line in chunk.splitlines():
                    if self.is_5xx_error(line):
                        error_lines.append(line)
                        
            return error_lines, bytes_read
    
    def navigate_forward(self, lines=10):
        error_lines, bytes_read = self.read_chunk_with_5xx_filter(self.cursor, self.buffer_size, lines)
        self.cursor = min(self.cursor + bytes_read, self.total_size)
        return '\n'.join(error_lines)
    
    def navigate_backward(self, lines=10):
        if self.cursor <= 0:
            return ""
        
        # Move cursor back by buffer size
        start_position = max(0, self.cursor - self.buffer_size)
        error_lines, _ = self.read_chunk_with_5xx_filter(start_position, self.cursor - start_position, lines)
        
        if error_lines:
            self.cursor = start_position
        return '\n'.join(error_lines[-lines:])

def main():
    parser = argparse.ArgumentParser(description='Navigate through nginx access logs - 5xx Error Filter')
    parser.add_argument('--log-file', default='/var/log/nginx/access.log',
                        help='Path to the nginx access log file')
    parser.add_argument('--lines', type=int, default=10,
                        help='Number of error lines to display at once')
    args = parser.parse_args()
    
    if not os.path.exists(args.log_file):
        print(f"Error: Log file '{args.log_file}' does not exist.")
        return
    
    navigator = LogNavigator(args.log_file)
    
    print("\nNginx 5xx Error Log Navigator")
    print("This tool shows only server errors (HTTP 500-599)")
    
    while True:
        print("\n=== 5xx Error Navigator ===")
        print(f"Position: {navigator.cursor} bytes / {navigator.total_size} bytes ({navigator.get_progress():.1f}%)")
        print("Commands: f (forward), b (backward), r (reset), q (quit)")
        command = input("> ").lower()
        
        if command == 'q':
            break
        elif command == 'f':
            content = navigator.navigate_forward(args.lines)
            if content:
                print("\nFound 5xx errors:")
                print(content)
            else:
                print("No 5xx errors found in this section")
        elif command == 'b':
            content = navigator.navigate_backward(args.lines)
            if content:
                print("\nFound 5xx errors:")
                print(content)
            else:
                print("No 5xx errors found in this section")
        elif command == 'r':
            navigator.cursor = 0
            print("Cursor reset to beginning of file")
        else:
            print("Invalid command")

if __name__ == "__main__":
    main()
