import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            os.system('cls' if os.name == 'nt' else 'clear')
            print("🔄 Reloading...")
            os.system('python main.py')  # החלף בשם של הקובץ שלך

if __name__ == "__main__":
    path = "."
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
