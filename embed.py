import os
import time
import schedule
import logging
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from utils.setup_db import File
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from utils.config import OPENAI_API_KEY
from chromadb import PersistentClient
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    CSVLoader,
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
)

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'system.log')

logger = logging.getLogger("embed_service")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def get_persistent_vectorstore():
    db_path = os.path.join(os.path.dirname(__file__), 'database')
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    client = PersistentClient(
        path=db_path,
        settings=Settings(
            persist_directory=db_path,
            is_persistent=True,
            anonymized_telemetry=False
        )
    )
    return Chroma(client=client, embedding_function=embeddings, collection_name="vector_db")

# Global variable for the vector store
vectorstore = get_persistent_vectorstore()

def load_and_split_documents(file_path):
    # Determine the file type and use the appropriate loader
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.csv':
        loader = CSVLoader(file_path)
    elif file_extension == '.txt':
        loader = TextLoader(file_path)
    elif file_extension == '.pdf':
        loader = PyPDFLoader(file_path)
    elif file_extension in ['.doc', '.docx']:
        loader = Docx2txtLoader(file_path)
    elif file_extension in ['.ppt', '.pptx']:
        loader = UnstructuredPowerPointLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    documents = loader.load()
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    
    return splits

def add_document_to_vectorstore(vectorstore, file_path):
    splits = load_and_split_documents(file_path)
    vectorstore.add_documents(splits)

def embed_files():
    logger.info("Checking for files to embed...")
    
    # Setup database connection
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'folder_watch.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query for files that haven't been embedded
    query = select(File).where(File.embedded == False)
    files_to_embed = session.execute(query).scalars().all()

    for file in files_to_embed:
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'documents', file.file_name)
            if os.path.exists(file_path):
                logger.info(f"Embedding file: {file.file_name}")
                add_document_to_vectorstore(vectorstore, file_path)
                
                # Update the embedded status in the database
                file.embedded = True
                session.commit()
                logger.info(f"File embedded successfully: {file.file_name}")
            else:
                logger.warning(f"File not found: {file.file_name}")
        except Exception as e:
            logger.error(f"Error embedding file {file.file_name}: {str(e)}")
            session.rollback()

    session.close()
    logger.info("Embedding process completed.")

def run_embedding_service():
    schedule.every(1).minutes.do(embed_files)

    logger.info("Embedding service started. Running every 1 minute.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    logger.info("Starting embedding service...")
    run_embedding_service()