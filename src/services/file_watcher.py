import sys
import os
import time
import logging
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.data_processing import variable_expense
from src.utils.log_result import *

# ## from https://www.youtube.com/watch?v=3_0_9Rf1ouQ
class Watcher:
    
    DIRECTORY_TO_WATCH = os.path.join(os.getcwd(), "data")
    
    
    def __init__(self):
        self.observer = Observer()
        
    def run(self):
        log_path = "Log.txt"
        event_handler = Handler()
        # Set recursive to False to watch only the specified directory, not its subdirectories
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        try:
            print("\nMonitoring")
            logResult(log_path, "Service is starting...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            logResult(log_path, "Service is stopping...")
        except Exception as e:
            logging.error(f"Service encountered an error: {e}")
        finally:
            print("\nDone")
            logResult(log_path, "Service has stopped.")
        self.observer.join()


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        self.process(event)
    
    def on_deleted(self, event):
        self.process(event)
        
    def on_modified(self, event):
        self.process(event)
    
    def on_moved(self, event):
        self.process(event)
    
    @staticmethod
    def process(event):
        """
        
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'

        event.src_path
            path to the changed file

        """       
        # Process CSV files created or modified after the watcher started
        full_path = event.src_path
        file_name = os.path.basename(full_path)
        destination_dir = os.path.join("data","Archived")
        os.makedirs(destination_dir, exist_ok=True) # Ensure archive directory exists
        dest_file_path = os.path.join(destination_dir,file_name)
        log_path = "Log.txt"
        
        # Check if it's a file creation event
        # logResult(log_path, f"Event Type: {event.event_type}")
        
        if event.event_type == 'created' and os.path.isfile(event.src_path):
            _, file_extension = os.path.splitext(event.src_path)
            if file_extension.lower() == '.csv':
                
                logResult(log_path, f"New CSV file detected: {file_name}")
                time.sleep(2) # Add a delay to ensure file is ready
                try:
                    # Process the new CSV File directly
                    variable_expense.ProcessVarExp(full_path)
                    logResult(log_path, f"Processed File {file_name}")
                    # Move or delete the file after processing
                    # Check if the destination file exists:
                    if os.path.exists(dest_file_path):
                        # Remove the existing file
                        os.remove(dest_file_path)
                        logResult(log_path, f"Removed existing file: {dest_file_path}")
                    
                    # # Move the processed CSV file to destination
                    shutil.move(event.src_path, destination_dir)
                    logResult(log_path, f"Moved {file_name} to: {destination_dir}")

                except Exception as e:
                    pass
                    logResult(log_path, f"Failed to processs file: {e}")
            else:
                
                logResult(log_path, f"Rejected non-CSV file: {event.src_path}")
