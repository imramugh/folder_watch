import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.setup_db import setup_database, File
from sqlalchemy import update, delete
from datetime import datetime
from utils.logger import system_logger

SCAN_INTERVAL = 60  # seconds
DOCUMENT_FORMATS = ('.csv', '.txt', '.pdf', '.doc', '.ppt', '.docx', '.pptx')

Session = setup_database()

class FolderHandler(FileSystemEventHandler):
    def __init__(self):
        self.session = Session()

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(DOCUMENT_FORMATS):
            file_name = os.path.basename(event.src_path)
            new_file = File(file_name=file_name, date_modified=datetime.now())
            self.session.add(new_file)
            self.session.commit()
            system_logger.info(f"File added: {file_name}")

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(DOCUMENT_FORMATS):
            file_name = os.path.basename(event.src_path)
            self.session.execute(update(File).where(File.file_name == file_name).values(date_modified=datetime.now()))
            self.session.commit()
            system_logger.info(f"File modified: {file_name}")

    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith(DOCUMENT_FORMATS):
            file_name = os.path.basename(event.src_path)
            self.session.execute(delete(File).where(File.file_name == file_name))
            self.session.commit()
            system_logger.info(f"File deleted: {file_name}")

def sync_files_with_database():
    session = Session()
    documents_path = os.path.join(os.path.dirname(__file__), 'documents')
    
    # Get all files in the documents folder
    files_in_folder = [f for f in os.listdir(documents_path) if f.endswith(DOCUMENT_FORMATS)]
    
    # Get all files in the database
    files_in_db = session.query(File.file_name).all()
    files_in_db = [f[0] for f in files_in_db]
    
    # Add files that are in the folder but not in the database
    for file_name in files_in_folder:
        if file_name not in files_in_db:
            file_path = os.path.join(documents_path, file_name)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            new_file = File(file_name=file_name, date_modified=mod_time)
            session.add(new_file)
            system_logger.info(f"Added missing file to database: {file_name}")
    
    # Remove files from the database that are not in the folder
    for file_name in files_in_db:
        if file_name not in files_in_folder:
            session.execute(delete(File).where(File.file_name == file_name))
            system_logger.info(f"Removed file from database that's not in folder: {file_name}")
    
    session.commit()

def start_monitoring():
    documents_path = os.path.join(os.path.dirname(__file__), 'documents')
    event_handler = FolderHandler()
    observer = Observer()
    observer.schedule(event_handler, documents_path, recursive=False)
    observer.start()
    system_logger.info("Folder monitoring started")

    try:
        while True:
            sync_files_with_database()
            time.sleep(SCAN_INTERVAL)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    system_logger.info("Folder monitoring stopped")

if __name__ == "__main__":
    start_monitoring()