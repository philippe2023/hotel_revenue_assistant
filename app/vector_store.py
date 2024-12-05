import logging
from typing import List, Optional
from langchain.schema import Document

import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)
import streamlit as st
import yaml

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()

def get_vector_collection() -> Optional[chromadb.Collection]:
    """Gets or creates a ChromaDB collection for vector storage."""
    try:
        ollama_ef = OllamaEmbeddingFunction(
            url=config["ollama_url"],
            model_name=config["embedding_model"],
        )

        chroma_client = chromadb.PersistentClient(path=config["vector_store_path"])
        collection = chroma_client.get_or_create_collection(
            name="revenue_optimization",
            embedding_function=ollama_ef,
            metadata={"hnsw:space": "cosine"},
        )
        return collection
    except Exception as e:
        logging.error(f"An error occurred while accessing the vector collection: {e}")
        st.error(f"An error occurred while accessing the vector collection: {e}")
        return None

def add_to_vector_collection(all_splits: List[Document], file_name: str):
    """Adds document splits to a vector collection for semantic search."""
    try:
        collection = get_vector_collection()
        if not collection:
            st.error("Vector store collection could not be initialized.")
            return

        if not all_splits:
            st.warning(f"No document splits found for file '{file_name}'. Skipping.")
            return

        documents, metadatas, ids = [], [], []

        for idx, split in enumerate(all_splits):
            if not split.page_content.strip():  # Skip empty content
                logging.warning(f"Skipping empty split in file '{file_name}' (Index: {idx})")
                continue
            documents.append(split.page_content)
            metadatas.append(split.metadata)
            ids.append(f"{file_name}_{idx}")

        if not documents:
            st.warning(f"No valid documents to add for file '{file_name}'.")
            return

        logging.info(f"Adding {len(documents)} documents to the vector store.")
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        st.success(f"Data from '{file_name}' added to the vector store!")
    except Exception as e:
        logging.error(f"An error occurred while adding data to the vector store: {e}")
        st.error(f"An error occurred while adding data to the vector store: {e}")

def query_collection(prompt: str, n_results: int = 10):
    """Queries the vector collection with a given prompt to retrieve relevant documents and their distances."""
    try:
        collection = get_vector_collection()
        if not collection:
            st.error("Vector store collection could not be initialized.")
            return None
        results = collection.query(
            query_texts=[prompt],
            n_results=n_results,
            include=['documents', 'distances', 'metadatas']
        )
        logging.info(f"Query returned {len(results['documents'][0]) if results and 'documents' in results else 0} results.")
        return results
    except Exception as e:
        logging.error(f"An error occurred while querying the collection: {e}")
        st.error(f"An error occurred while querying the collection: {e}")
        return None

def list_uploaded_documents() -> List[str]:
    """Lists the names of uploaded documents."""
    try:
        collection = get_vector_collection()
        if not collection:
            return []
        # Fetch all IDs from the collection
        all_ids = collection.get()["ids"]
        # Extract document names from IDs
        document_names = set([doc_id.rsplit("_", 1)[0] for doc_id in all_ids])
        return sorted(list(document_names))
    except Exception as e:
        logging.error(f"An error occurred while listing documents: {e}")
        st.error(f"An error occurred while listing documents: {e}")
        return []

def delete_document(document_name: str):
    """Deletes all vectors associated with a document."""
    try:
        collection = get_vector_collection()
        if not collection:
            st.error("Vector store collection could not be initialized.")
            return
        # Find all IDs associated with the document
        all_ids = collection.get()["ids"]
        ids_to_delete = [
            doc_id for doc_id in all_ids if doc_id.startswith(f"{document_name}_")
        ]
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            st.success(f"Document '{document_name}' deleted successfully.")
        else:
            st.info(f"No data found for document '{document_name}'.")
    except Exception as e:
        logging.error(f"An error occurred while deleting the document: {e}")
        st.error(f"An error occurred while deleting the document: {e}")