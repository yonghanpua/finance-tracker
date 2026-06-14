import os
import time
import logging
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.data_processing import variable_expense
from src.utils.log_result import logResult
from config.settings import WATCH_DIR, LOG_PATH

# ## from https://www.youtube.com/watch?v=3_0_9Rf1ouQ
class Watcher:
    def __init__(self):
        self.observer = Observer()
        
    def run(self):
        event_handler = Handler()
        # Set recursive to False to watch only the specified directory, not its subdirectories
        self.observer.schedule(event_handler, str(WATCH_DIR), recursive=False)
        self.observer.start()
        try:
            print("\nMonitoring")
            logResult("Service is starting...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            logResult("Service is stopping...")
        except Exception as e:
            logResult(f"Service encountered an error: {e}")
        finally:
            print("\nDone")
            logResult("Service has stopped.")
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
        if event.is_directory:
            return
        
        # Process CSV files created or modified after the watcher started
        full_path = event.src_path
        file_name = os.path.basename(full_path)
        destination_dir = Path(WATCH_DIR) / "Archived"
        destination_dir.mkdir(parents=True, exist_ok=True)
        dest_file_path = destination_dir / file_name
        
        # Check if it's a file creation event
        
        if event.event_type == 'created' and os.path.isfile(full_path):
            _, file_extension = os.path.splitext(full_path)
            if file_extension.lower() == '.csv':
                
                logResult(f"New CSV file detected: {file_name}")
                time.sleep(2) # Add a delay to ensure file is ready
                try:
                    # Process the new CSV File directly
                    variable_expense.ProcessVarExp(full_path)
                    logResult(f"Processed File {file_name}")
                    # Move or delete the file after processing
                    # Check if the destination file exists:
                    if dest_file_path.exists():
                        dest_file_path.unlink()
                        logResult(f"Removed existing file: {dest_file_path}")
                    
                    # # Move the processed CSV file to destination
                    shutil.move(full_path, str(destination_dir))
                    logResult(f"Moved {file_name} to: {destination_dir}")

                except Exception as e:
                    logResult(f"Failed to processs file {file_name}: {e}")
            else:
                
                logResult(f"Rejected non-CSV file: {file_name}")
