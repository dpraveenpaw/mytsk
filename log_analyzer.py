#!/usr/bin/env python3
import os
import time
from datetime import datetime
import argparse

class LogNavigator:
    def __init__(self, log_file):
        self.log_file = log_file
        self.cursor = 0
        self.buffer_size = 4096
        self.total_size = self.get_file_size()
    
    def get_file_size(self):
        return os.path.getsize(self.log_file)
    
    def get_progress(self):
        """Returns the current progress as a percentage"""
        return (self.cursor / self.total_size) * 100 if self.total_size > 0 else 0
    
    def read_chunk(self, position, size):
        with open(self.log_file, 'r') as f:
            f.seek(max(0, position))  # Ensure we don't seek to negative position
            return f.read(size)
    
    def navigate_forward(self, lines=10):
        current_position = self.cursor
        lines_read = 0
        
        while lines_read < lines:
            chunk = self.read_chunk(current_position, self.buffer_size)
            if not chunk:
                break
                
            new_lines = chunk.count('\n')
            if new_lines + lines_read >= lines:
                # Find the position of the nth newline
                count = lines - lines_read
                pos = 0
                for _ in range(count):
                    pos = chunk.find('\n', pos + 1)
                current_position += pos + 1
                break
            
            lines_read += new_lines
            current_position += len(chunk)
        
        self.cursor = current_position
        # Read from the max of 0 or (cursor - buffer_size) to avoid negative positions
        read_start = max(0, self.cursor - self.buffer_size)
        return self.read_chunk(read_start, self.buffer_size)
    
    def navigate_backward(self, lines=10):
        if self.cursor <= 0:
            return ""
            
        current_position = max(0, self.cursor - self.buffer_size)
        chunk = self.read_chunk(current_position, self.cursor - current_position)
        newline_positions = [i for i, char in enumerate(chunk) if char == '\n']
        
        if len(newline_positions) >= lines:
            self.cursor = current_position + newline_positions[-lines]
        else:
            self.cursor = current_position
            
        return self.read_chunk(self.cursor, self.buffer_size)

def main():
    parser = argparse.ArgumentParser(description='Navigate through nginx access logs')
    parser.add_argument('--log-file', default='/var/log/nginx/access.log',
                        help='Path to the nginx access log file')
    parser.add_argument('--lines', type=int, default=10,
                        help='Number of lines to display at once')
    args = parser.parse_args()
    
    # Verify that the log file exists
    if not os.path.exists(args.log_file):
        print(f"Error: Log file '{args.log_file}' does not exist.")
        return
    
    navigator = LogNavigator(args.log_file)
    
    while True:
        print("\n=== Log Navigator ===")
        print(f"Position: {navigator.cursor} bytes / {navigator.total_size} bytes ({navigator.get_progress():.1f}%)")
        print("Commands: f (forward), b (backward), r (reset), q (quit)")
        command = input("> ").lower()
        
        if command == 'q':
            break
        elif command == 'f':
            content = navigator.navigate_forward(args.lines)
            print(content)
        elif command == 'b':
            content = navigator.navigate_backward(args.lines)
            print(content)
        elif command == 'r':
            navigator.cursor = 0
            print("Cursor reset to beginning of file")
        else:
            print("Invalid command")
            
if __name__ == "__main__":
    main()
