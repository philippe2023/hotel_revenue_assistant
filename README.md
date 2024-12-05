# Revenue Optimization Assistant

The **Revenue Optimization Assistant** is a data-driven tool designed to help hotels analyze their pricing strategies against competitors. This application uses uploaded competitor rate data to identify days where pricing may be suboptimal, enabling actionable insights to optimize revenue.

## Key Features

- **Upload and Process Data**: Upload CSV or Excel files containing competitor rate data.
- **Question Answering**: Ask questions about pricing trends, overpricing, underpricing, or competitor behavior.
- **Actionable Insights**: Identify overpriced or underpriced days and restrictions based on competitor comparisons.
- **Interactive Visualizations**: View results in structured tables for better readability.
- **Customizable Contexts**: Dynamically process and filter uploaded data to provide precise answers to queries.

---

## How It Works

1. **Upload Dataset**:
   - Upload a file containing columns like `Date`, `Your Rate`, `Competitor Rates`, etc.
   - The system processes the file and stores the data for analysis.

2. **Ask Questions**:
   - Examples:
     - "Which days am I overpriced?"
     - "What is the highest competitor rate recorded?"
     - "Which days have the lowest competitor rates?"

3. **Get Insights**:
   - Results are displayed in a table highlighting actionable insights, such as overpriced days.

4. **Confidence Scoring**:
   - Each response is assigned a confidence score, reflecting the relevance of the data used.

---

## Project Structure

project/
├── app/
│   ├── main_app.py             # Streamlit application file
│   ├── llm_interface.py        # Handles interaction with the language model
│   ├── document_processing.py  # Processes uploaded files into usable data
│   ├── vector_store.py         # Manages vector storage for semantic search
│   ├── utils.py                # Helper functions for data processing and formatting
│   ├── config.yaml             # Configuration file
├── data/
│   ├── example_competitor_rates.csv # Sample dataset
│   ├── generate_data.py # generate sample dataset
├── README.md                   # Project documentation