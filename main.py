from src.services.file_watcher import Watcher

def main():
    # Create an instance of the Watcher class
    watcher = Watcher()
    
    # Run the file watcher
    watcher.run()

if __name__ == '__main__':
    main()
    
    
