import os
import boto3
from io import StringIO
from dotenv import load_dotenv
from glob import glob
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_postgres import PGVector
from datetime import datetime, timezone
import psycopg2

# Load environment variables
load_dotenv()

# AWS S3 credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Azure OpenAI API details
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# PostgreSQL database details
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

# Initialize embedding model
embedding_model = AzureOpenAIEmbeddings(
    model=AZURE_OPENAI_DEPLOYMENT,
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_API_BASE,
    openai_api_version="2022-12-01"
)

# PostgreSQL connection string
PG_CONN_STRING = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
COLLECTION_NAME = "langchain_pg_collection"
EMBEDDING_NAME = "langchain_pg_embedding"

print(PG_CONN_STRING)

# Step 1: Download files from S3 and Chunk Text
def download_and_chunk_s3_files(bucket_name, prefix=""):
    """
    Download all .txt files from an S3 bucket and chunk their content.
    """
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    if "Contents" not in response:
        print("No files found in the specified S3 bucket or prefix.")
        return []

    chunk_content = []
    chunk_metadata = []

    # Define the start and end of the time range (UTC)
    now = datetime.now().date()
    #start_of_day = now.replace(hour=0, minute=0, second=10)

    for obj in response["Contents"]:
        file_key = obj["Key"]
        last_modified_date = obj["LastModified"].date()
        in_time_range = last_modified_date >= now

        if file_key.endswith(".txt") and in_time_range:
            print(f"Downloading {file_key}...")
            s3_object = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            content = s3_object["Body"].read().decode("utf-8")

            # Chunk the file content
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=120)
            chunks = text_splitter.split_text(content)

            # Add chunks with metadata
            for idx, chunk in enumerate(chunks):
                chunk_content.append(chunk)
                chunk_metadata.append({"source_file": file_key, "chunk_id": idx})
 
    return {"texts": chunk_content, "metadatas": chunk_metadata}


# For individual chunk
# def load_and_chunk_file(file_path):
#     with open(file_path, 'r') as file:
#         content = file.read()
        
#     # Chunk text into manageable pieces
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     chunks = text_splitter.split_text(content)
#     return chunks


# Step 2: Store Embeddings in PostgreSQL
def store_embeddings_in_pg(chunks):
    # Initialize PostgreSQL vector store
    pg_vector = PGVector(
        embeddings=embedding_model,
        collection_name=COLLECTION_NAME,
        connection=PG_CONN_STRING,
    )
    
    # Create the table (if not already exists)
    pg_vector.create_tables_if_not_exists()

    # Add embeddings
    pg_vector.add_texts(texts=chunks["texts"], metadatas=chunks["metadatas"])
    print("Embeddings stored successfully in PostgreSQL!")

# Step 3: Query Embeddings
def query_embeddings(question):
    # Connect to the PGVector database
    pg_vector = PGVector(
        embeddings=embedding_model,
        collection_name=COLLECTION_NAME,
        connection=PG_CONN_STRING,
    )
    
    # Perform a similarity search
    results = pg_vector.similarity_search(question, k=5)
    return results

# Function to remove collection data
def remove_data():
    # Connect to the database
    conn = psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )
    cursor = conn.cursor()

    # Drop the table
    cursor.execute(f"DROP TABLE IF EXISTS {COLLECTION_NAME} CASCADE;")
    cursor.execute(f"DROP TABLE IF EXISTS {EMBEDDING_NAME} CASCADE;")
    conn.commit()

    print(f"Collection '{COLLECTION_NAME}' has been removed.")

    # Close the connection
    cursor.close()
    conn.close()

# Step 4: Main Function
if __name__ == "__main__":
    chunks = download_and_chunk_s3_files(S3_BUCKET_NAME)
    #chunks = load_and_chunk_file("./paper.txt")

    if chunks and chunks["texts"] and chunks["metadatas"]:
        #store_embeddings_in_pg(chunks)
    
        # Example query
        question = "What are the key points discussed in the papers?"
        results = query_embeddings(question)
        print("Query Results:", results)
