import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from utils.config import OPENAI_API_KEY
from chromadb import PersistentClient
from chromadb.config import Settings

def setup_vector_db():
    # Update the db_path to point directly to the database folder
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
    
    # Initialize OpenAI embeddings
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in config.py")
    
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    
    # Create a PersistentClient with the custom SQLite file name
    client = PersistentClient(
        path=db_path,
        settings=Settings(
            persist_directory=db_path,
            is_persistent=True,
            anonymized_telemetry=False
        )
    )
    
    # Create Chroma vector store using the custom client
    vectorstore = Chroma(
        client=client,
        embedding_function=embeddings,
        collection_name="vector_db"
    )
    
    return vectorstore

if __name__ == '__main__':
    setup_vector_db()
    print("Vector database setup complete.")