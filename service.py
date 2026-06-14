import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import threading
import time
import os, sys
from pathlib import Path
from src.services.file_watcher import Watcher
from src.utils.log_result import logResult

# Force working directory to the project root

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "FileWatcherService"
    _svc_display_name_ = "File Watcher Service"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        self.is_alive = True
        self.watcher = None
        self.log_path = "Log.txt"

    def SvcStop(self):
        logResult(self.log_path, "Service is stopping...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_alive = False
        if self.watcher and self.watcher.observer:
            self.watcher.observer.stop()
            self.watcher.observer.join(timeout=5)  # Add a timeout for the thread join
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        try:
            os.chdir(Path(__file__).parent)
            sys.path.insert(0, str(Path(__file__).parent))
            
            logResult(self.log_path, "Service is starting up.")
            
            # Report service as running ASAP
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )

            # Start watcher in background thread
            self.watcher = Watcher()
            watcher_thread = threading.Thread(target=self.watcher.run, daemon=True)
            watcher_thread.start()
            logResult(self.log_path, "Watcher thread started successfully.")

            # Now just wait until stop is triggered
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

            # On shutdown
            if self.watcher and self.watcher.observer:
                self.watcher.observer.stop()
                self.watcher.observer.join(timeout=5)
            watcher_thread.join(timeout=10)

        except Exception as e:
            logResult(self.log_path, f"Fatal error during startup: {e}")
            servicemanager.LogErrorMsg(f"Fatal error: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # If no arguments are provided, assume this is a run from the service manager
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Otherwise, assume it's a command from the command line
        win32serviceutil.HandleCommandLine(AppServerSvc)