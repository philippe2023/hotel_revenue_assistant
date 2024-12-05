import os
import logging
import hashlib
from typing import List
import pandas as pd
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import streamlit as st

# Cache for processed files
processed_files_cache = set()

def is_document_already_processed(file_name: str) -> bool:
    """
    Checks if a document has already been processed by checking its hash in a cache.
    """
    file_hash = hashlib.md5(file_name.encode()).hexdigest()
    return file_hash in processed_files_cache

def mark_document_as_processed(file_name: str):
    """
    Marks a document as processed by adding its hash to the cache.
    """
    file_hash = hashlib.md5(file_name.encode()).hexdigest()
    processed_files_cache.add(file_hash)

def process_document(file) -> List[Document]:
    """Processes a comp set file, extracting data and splitting it into chunks."""
    try:
        # Load file as DataFrame
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            st.error("Unsupported file type. Please upload a CSV or Excel file.")
            return []

        # Validate required columns
        required_columns = ["Date", "Your Rate", "Competitor Rates", "Min LOS", "Advance Purchase"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            return []

        # Convert DataFrame to text chunks
        text_data = df.to_csv(index=False)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)
        splits = text_splitter.split_text(text_data)

        # Create Document objects
        docs = [Document(page_content=chunk, metadata={"file_name": file.name}) for chunk in splits]
        return docs
    except Exception as e:
        logging.error(f"Error processing document: {e}")
        st.error(f"Error processing document: {e}")
        return []