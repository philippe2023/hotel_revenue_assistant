import os
import logging

import streamlit as st
from streamlit.runtime.state import SessionState

from document_processing import (
    process_document,
    is_document_already_processed,
    mark_document_as_processed,
)
from vector_store import (
    add_to_vector_collection,
    query_collection,
    list_uploaded_documents,
    delete_document,
)
from llm_interface import call_llm
from utils import normalize_scores, get_confidence_color, extract_relevant_context, format_response
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

st.set_page_config(page_title="Revenue Optimization Assistant", layout="wide")

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()

def main():
    # Sidebar
    with st.sidebar:
        st.title("Revenue Optimization Assistant")
        st.markdown("Upload comp set data and identify pricing and restriction opportunities.")

        # File uploader
        uploaded_files = st.file_uploader(
            "Upload Comp Set Data",
            type=["csv", "xlsx"],
            accept_multiple_files=False
        )
        if st.button("Process Data"):
            if uploaded_files:
                with st.spinner("Processing data..."):
                    if not is_document_already_processed(uploaded_files.name):
                        docs = process_document(uploaded_files)
                        if docs:
                            add_to_vector_collection(docs, uploaded_files.name)
                            mark_document_as_processed(uploaded_files.name)
                            st.success(f"File '{uploaded_files.name}' processed successfully!")
                        else:
                            st.error(f"Processing failed for file '{uploaded_files.name}'.")
                    else:
                        st.warning(f"File '{uploaded_files.name}' has already been processed.")
            else:
                st.warning("Please upload a comp set file.")

    # Main Content
    st.title("Revenue Optimization Insights")
    st.header("Ask a Question")
    question = st.text_area("Enter your question (e.g., 'Which days am I overpriced?'):", key="question_input")
    n_results = st.slider("Number of records to retrieve:", 1, 20, 10, key="n_results_slider")
    if st.button("Get Insights"):
        if question.strip():  # Ensure the question is not empty or whitespace
            with st.spinner("Analyzing..."):
                # Query the vector store and generate an answer
                results = query_collection(question, n_results)
                if results and 'documents' in results and 'distances' in results:
                    documents = results['documents'][0] if results['documents'] else []
                    distances = results['distances'][0] if results['distances'] else []

                    if not documents or not distances:
                        st.warning("No relevant documents were found for your query.")
                        return  # Skip further processing
                    
                    # Normalize retrieval scores
                    retrieval_scores = normalize_scores(distances)

                    # Calculate confidence score
                    confidence_score = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0.0
                    color = get_confidence_color(confidence_score)
                    st.markdown(f"**Confidence Score:** <span style='color:{color}'>{confidence_score:.2f}</span>", unsafe_allow_html=True)

                    # Extract relevant context for the question
                    context = " ".join(documents)
                    relevant_context = extract_relevant_context(context, question)
                    
                    # Generate response using the LLM
                    response_generator = call_llm(relevant_context, question, "en")
                    response = "".join(chunk for chunk in response_generator)

                    # Format and display the response
                    if response.strip():
                        # Convert response to DataFrame for better visualization
                        import pandas as pd
                        from io import StringIO

                        try:
                            # Attempt to parse the response into a DataFrame
                            df = pd.read_csv(StringIO(response))
                            # Select key columns for display
                            display_df = df[["Date", "Your Rate", "Average Competitor Rate"]]
                            # Display the table
                            st.markdown("### Answer")
                            st.table(display_df)  # Display the table in a structured format
                        except Exception as e:
                            # If the response isn't a valid CSV, show it as markdown
                            st.markdown(response)
                    else:
                        st.warning("No response generated. Please refine your question.")
                else:
                    st.warning("No relevant data found.")
        else:
            st.warning("Please enter a valid question.")

if __name__ == "__main__":
    main()