import os
import shutil
import sys
import logging

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from setup_db import setup_database
from setup_vector_db import setup_vector_db

# Setup logging
log_dir = os.path.join(project_root, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'system.log')

logger = logging.getLogger("clear_data")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def clear_database_folder():
    db_folder = os.path.join(project_root, 'database')
    
    # Check if the database folder exists
    if os.path.exists(db_folder):
        # Remove all contents of the database folder
        for filename in os.listdir(db_folder):
            file_path = os.path.join(db_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    logger.info(f"Deleted file: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    logger.info(f"Deleted directory: {file_path}")
            except Exception as e:
                logger.error(f'Failed to delete {file_path}. Reason: {e}')
    else:
        # Create the database folder if it doesn't exist
        os.makedirs(db_folder)
        logger.info(f"Created database folder: {db_folder}")

    logger.info("Database folder cleared.")

def recreate_databases():
    logger.info("Recreating SQL database...")
    setup_database()
    logger.info("SQL database recreated.")

    logger.info("Recreating vector database...")
    setup_vector_db()
    logger.info("Vector database recreated.")

if __name__ == "__main__":
    logger.info("Starting data clearing process...")
    clear_database_folder()
    recreate_databases()
    logger.info("Data clearing and recreation process completed.")